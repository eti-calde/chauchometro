import re
from decimal import Decimal
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup
import logging

from app.parsers.base import BaseParser, Transaction, TransactionType
from app.email.connection import EmailMessage

logger = logging.getLogger(__name__)


class BancoChileParser(BaseParser):
    """Parser para emails del Banco de Chile

    Formatos soportados:
    - "Cargo en Cuenta": compra con débito
    - "Giro con Tarjeta de Débito": giro en cajero
    - "Transferencia realizada": transferencia enviada
    - "Abono en tu cuenta": depósito recibido
    - "Compra realizada con tu Tarjeta": compra con crédito (formato antiguo)
    """

    SENDER_EMAIL = "enviodigital@bancochile.cl"

    # Subjects que debemos ignorar (no son transacciones)
    IGNORED_SUBJECTS = [
        "cartola cuenta corriente",
    ]

    # Mapeo de subjects a tipos de transacción
    SUBJECT_PATTERNS = {
        TransactionType.COMPRA: [
            r"cargo en cuenta",
            r"compra realizada con tu tarjeta",
        ],
        TransactionType.GIRO: [
            r"giro con tarjeta",
        ],
        TransactionType.TRANSFERENCIA: [
            r"transferencia realizada",
        ],
        TransactionType.ABONO: [
            r"abono en tu cuenta",
        ],
    }

    def can_parse(self, email_message: EmailMessage) -> bool:
        """Verifica si es un email del Banco de Chile"""
        return self.SENDER_EMAIL in email_message.sender.lower()

    def parse(self, email_message: EmailMessage) -> Optional[Transaction]:
        """Parsea el email según su tipo"""
        subject_lower = email_message.subject.lower()

        # Ignorar emails que no son transacciones
        for ignored in self.IGNORED_SUBJECTS:
            if ignored in subject_lower:
                logger.debug(f"Ignorando email no transaccional: {email_message.subject}")
                return None

        # Detectar tipo de transacción
        transaction_type = self._detect_type(subject_lower)
        if not transaction_type:
            logger.warning(f"Tipo de transacción no reconocido: {email_message.subject}")
            return None

        # Extraer texto del HTML
        text = self._extract_text(email_message.body_html)

        # Parsear según tipo
        try:
            if transaction_type == TransactionType.COMPRA:
                return self._parse_compra(email_message, text)
            elif transaction_type == TransactionType.GIRO:
                return self._parse_giro(email_message, text)
            elif transaction_type == TransactionType.TRANSFERENCIA:
                return self._parse_transferencia(email_message, text)
            elif transaction_type == TransactionType.ABONO:
                return self._parse_abono(email_message, text)
        except Exception as e:
            logger.error(f"Error parseando email Banco Chile: {e}")
            return None

        return None

    def _detect_type(self, subject_lower: str) -> Optional[TransactionType]:
        """Detecta el tipo de transacción basado en el asunto"""
        for tx_type, patterns in self.SUBJECT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, subject_lower):
                    return tx_type
        return None

    def _extract_text(self, html: str) -> str:
        """Extrae texto limpio del HTML"""
        if not html:
            return ""
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style', 'head']):
            tag.decompose()
        return soup.get_text(separator=' ', strip=True)

    def _parse_amount(self, text: str) -> Optional[Decimal]:
        """Extrae el monto del texto

        Formatos:
        - $30.000
        - $5.390
        - $50
        """
        match = re.search(r'\$\s*([\d.]+)', text)
        if not match:
            return None
        # Remover puntos de miles y convertir
        amount_str = match.group(1).replace('.', '')
        return Decimal(amount_str)

    def _parse_date(self, text: str) -> Optional[datetime]:
        """Extrae fecha y hora del texto

        Formato: DD/MM/YYYY HH:MM
        """
        match = re.search(r'(\d{2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2})', text)
        if not match:
            return None
        dia, mes, año, hora, minuto = match.groups()
        return datetime(int(año), int(mes), int(dia), int(hora), int(minuto))

    def _parse_account(self, text: str) -> Optional[str]:
        """Extrae los últimos 4 dígitos de la cuenta

        Formato: ****3204
        """
        match = re.search(r'\*{4}(\d{4})', text)
        return match.group(1) if match else None

    def _parse_compra(self, email_message: EmailMessage, text: str) -> Optional[Transaction]:
        """Parsea email de compra/cargo en cuenta

        Formato esperado:
        "Te informamos que se ha realizado una compra por $XX.XXX
         con cargo a Cuenta ****XXXX en COMERCIO el DD/MM/YYYY HH:MM."
        """
        # Extraer monto
        amount = self._parse_amount(text)
        if not amount:
            logger.error("No se encontró monto en email de compra")
            return None

        # Extraer comercio - está entre "en " y " el DD/MM"
        comercio_match = re.search(r'en\s+(.+?)\s+el\s+\d{2}/\d{2}', text)
        comercio = comercio_match.group(1).strip() if comercio_match else None

        # Extraer fecha
        fecha = self._parse_date(text) or email_message.date

        # Extraer cuenta
        cuenta = self._parse_account(text)

        return Transaction(
            bank="banco_chile",
            type=TransactionType.COMPRA,
            amount=amount,
            description=f"Compra en {comercio or 'comercio no identificado'}",
            date=fecha,
            merchant=comercio,
            last_digits=cuenta,
            email_id=email_message.uid,
            raw_data={
                'subject': email_message.subject,
            }
        )

    def _parse_giro(self, email_message: EmailMessage, text: str) -> Optional[Transaction]:
        """Parsea email de giro en cajero

        Formato esperado:
        "Te informamos que se ha realizado un giro en Cajero por $XX.XXX
         con cargo a Cuenta ****XXXX el DD/MM/YYYY HH:MM."
        """
        # Extraer monto
        amount = self._parse_amount(text)
        if not amount:
            logger.error("No se encontró monto en email de giro")
            return None

        # Extraer fecha
        fecha = self._parse_date(text) or email_message.date

        # Extraer cuenta
        cuenta = self._parse_account(text)

        return Transaction(
            bank="banco_chile",
            type=TransactionType.GIRO,
            amount=amount,
            description="Giro en cajero automático",
            date=fecha,
            merchant="Cajero automático",
            last_digits=cuenta,
            email_id=email_message.uid,
            raw_data={
                'subject': email_message.subject,
            }
        )

    def _parse_transferencia(self, email_message: EmailMessage, text: str) -> Optional[Transaction]:
        """Parsea email de transferencia realizada"""
        amount = self._parse_amount(text)
        if not amount:
            logger.error("No se encontró monto en email de transferencia")
            return None

        # Buscar destinatario
        destinatario = None
        for pattern in [r'a\s+([^$\n]+?)\s+por', r'destinatario[:\s]+([^<\n]+)']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                destinatario = match.group(1).strip()
                break

        fecha = self._parse_date(text) or email_message.date
        cuenta = self._parse_account(text)

        return Transaction(
            bank="banco_chile",
            type=TransactionType.TRANSFERENCIA,
            amount=amount,
            description=f"Transferencia a {destinatario or 'destinatario desconocido'}",
            date=fecha,
            merchant=destinatario,
            last_digits=cuenta,
            email_id=email_message.uid,
            raw_data={'subject': email_message.subject}
        )

    def _parse_abono(self, email_message: EmailMessage, text: str) -> Optional[Transaction]:
        """Parsea email de abono recibido"""
        amount = self._parse_amount(text)
        if not amount:
            logger.error("No se encontró monto en email de abono")
            return None

        # Buscar origen
        origen = None
        for pattern in [r'de\s+([^$\n]+?)\s+por', r'origen[:\s]+([^<\n]+)']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                origen = match.group(1).strip()
                break

        fecha = self._parse_date(text) or email_message.date
        cuenta = self._parse_account(text)

        return Transaction(
            bank="banco_chile",
            type=TransactionType.ABONO,
            amount=amount,
            description=f"Abono de {origen or 'origen desconocido'}",
            date=fecha,
            merchant=origen,
            last_digits=cuenta,
            email_id=email_message.uid,
            raw_data={'subject': email_message.subject}
        )
