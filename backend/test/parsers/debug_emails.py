#!/usr/bin/env python
"""Script para debuggear el contenido de los emails del Banco de Chile"""

import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from app.email.connection import EmailConnector

def extract_text_from_html(html):
    """Extrae texto legible del HTML"""
    if not html:
        return "(vacío)"
    soup = BeautifulSoup(html, 'html.parser')
    # Eliminar scripts y estilos
    for tag in soup(['script', 'style', 'head']):
        tag.decompose()
    text = soup.get_text(separator='\n', strip=True)
    # Limpiar líneas vacías múltiples
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def main():
    load_dotenv()

    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_provider = os.getenv('EMAIL_PROVIDER', 'gmail')

    if not email_address or not email_password:
        print("ERROR: Configura EMAIL_ADDRESS y EMAIL_PASSWORD en .env")
        return

    print(f"Conectando a {email_provider}...")

    with EmailConnector(email_address, email_password, email_provider) as connector:
        emails = connector.search_emails(
            sender="enviodigital@bancochile.cl",
            since_date=datetime.now() - timedelta(days=60)
        )

        print(f"\n{'='*80}")
        print(f"ENCONTRADOS: {len(emails)} emails del Banco de Chile")
        print(f"{'='*80}\n")

        # Mostrar solo los primeros 10
        for i, email_msg in enumerate(emails[:10]):
            print(f"\n{'#'*80}")
            print(f"EMAIL {i+1}")
            print(f"{'#'*80}")
            print(f"UID: {email_msg.uid}")
            print(f"SUBJECT: {email_msg.subject}")
            print(f"FROM: {email_msg.sender}")
            print(f"DATE: {email_msg.date}")
            print(f"\n{'-'*40}")
            print("CONTENIDO EXTRAÍDO:")
            print(f"{'-'*40}")
            content = extract_text_from_html(email_msg.body_html)
            print(content[:2500])
            print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
