#!/usr/bin/env python
"""Script para probar el scraping de emails"""

import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from app.email.connection import EmailConnector
from app.parsers.banco_chile import BancoChileParser

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Cargar variables de entorno
    load_dotenv()
    
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_provider = os.getenv('EMAIL_PROVIDER', 'gmail')
    
    if not email_address or not email_password:
        logger.error("Configura EMAIL_ADDRESS y EMAIL_PASSWORD en .env")
        return
    
    # Conectar y buscar emails
    logger.info(f"Conectando a {email_provider}...")
    
    with EmailConnector(email_address, email_password, email_provider) as connector:
        # Buscar emails del Banco de Chile de los últimos 30 días
        emails = connector.search_emails(
            sender="enviodigital@bancochile.cl",
            since_date=datetime.now() - timedelta(days=30)
        )
        
        logger.info(f"Encontrados {len(emails)} emails del Banco de Chile")
        
        # Parsear emails
        parser = BancoChileParser()
        transactions = []
        
        for email_msg in emails:
            if parser.can_parse(email_msg):
                transaction = parser.parse(email_msg)
                if transaction:
                    transactions.append(transaction)
                    logger.info(f"✓ Parseado: {transaction}")
                else:
                    logger.warning(f"✗ No se pudo parsear: {email_msg.subject}")
        
        # Resumen
        logger.info(f"\nResumen:")
        logger.info(f"- Total emails: {len(emails)}")
        logger.info(f"- Transacciones parseadas: {len(transactions)}")
        
        if transactions:
            total = sum(t.amount for t in transactions)
            logger.info(f"- Total gastado: ${total:,.0f}")

if __name__ == "__main__":
    main()