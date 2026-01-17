import imaplib
import email
from email.header import decode_header
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EmailMessage:
    """Estructura para representar un email"""
    uid: str
    subject: str
    sender: str
    date: datetime
    body_html: str
    body_text: str
    raw_email: bytes

class EmailConnector:
    """Conector genérico para servicios de email vía IMAP"""
    
    PROVIDERS = {
        'gmail': {
            'imap_server': 'imap.gmail.com',
            'imap_port': 993
        },
        'outlook': {
            'imap_server': 'outlook.office365.com',
            'imap_port': 993
        }
    }
    
    def __init__(self, email_address: str, password: str, provider: str = 'gmail'):
        self.email_address = email_address
        self.password = password
        self.provider = provider.lower()
        self.connection: Optional[imaplib.IMAP4_SSL] = None
        
        if self.provider not in self.PROVIDERS:
            raise ValueError(f"Proveedor no soportado: {provider}")
    
    def connect(self) -> None:
        """Conecta al servidor IMAP"""
        try:
            config = self.PROVIDERS[self.provider]
            self.connection = imaplib.IMAP4_SSL(
                config['imap_server'], 
                config['imap_port']
            )
            self.connection.login(self.email_address, self.password)
            logger.info(f"Conectado exitosamente a {self.provider}")
        except imaplib.IMAP4.error as e:
            logger.error(f"Error de autenticación: {e}")
            raise
        except Exception as e:
            logger.error(f"Error conectando a IMAP: {e}")
            raise
    
    def disconnect(self) -> None:
        """Desconecta del servidor IMAP"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except:
                pass
    
    def search_emails(
        self, 
        sender: str, 
        since_date: Optional[datetime] = None,
        subject_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[EmailMessage]:
        """
        Busca emails por remitente y fecha
        
        Args:
            sender: Email del remitente
            since_date: Buscar desde esta fecha (default: últimos 30 días)
            subject_filter: Filtrar por asunto que contenga este texto
            limit: Máximo número de emails a retornar
        """
        if not self.connection:
            self.connect()
        
        # Seleccionar inbox
        self.connection.select('INBOX')
        
        # Construir query de búsqueda
        if not since_date:
            since_date = datetime.now() - timedelta(days=30)
        
        date_str = since_date.strftime("%d-%b-%Y")
        search_criteria = f'(FROM "{sender}" SINCE {date_str})'
        
        try:
            # Buscar emails
            typ, data = self.connection.search(None, search_criteria)
            if typ != 'OK':
                logger.error(f"Error en búsqueda: {typ}")
                return []
            
            email_ids = data[0].split()
            email_ids = email_ids[-limit:]  # Limitar resultados
            
            emails = []
            for email_id in email_ids:
                try:
                    email_msg = self._fetch_email(email_id)
                    if email_msg and (not subject_filter or subject_filter.lower() in email_msg.subject.lower()):
                        emails.append(email_msg)
                except Exception as e:
                    logger.error(f"Error procesando email {email_id}: {e}")
                    continue
            
            logger.info(f"Encontrados {len(emails)} emails de {sender}")
            return emails
            
        except Exception as e:
            logger.error(f"Error buscando emails: {e}")
            return []
    
    def _fetch_email(self, email_id: bytes) -> Optional[EmailMessage]:
        """Obtiene un email por ID"""
        try:
            typ, data = self.connection.fetch(email_id, '(RFC822)')
            if typ != 'OK':
                return None
            
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extraer información básica
            subject = self._decode_header(email_message['Subject'])
            sender = email_message['From']
            date = email.utils.parsedate_to_datetime(email_message['Date'])
            
            # Extraer cuerpo
            body_html = ""
            body_text = ""
            
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/html":
                        body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == "text/plain":
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                content_type = email_message.get_content_type()
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                if content_type == "text/html":
                    body_html = body
                else:
                    body_text = body
            
            return EmailMessage(
                uid=email_id.decode(),
                subject=subject,
                sender=sender,
                date=date,
                body_html=body_html,
                body_text=body_text,
                raw_email=raw_email
            )
            
        except Exception as e:
            logger.error(f"Error decodificando email: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Decodifica headers de email"""
        if not header:
            return ""
        
        decoded = decode_header(header)[0]
        if isinstance(decoded[0], bytes):
            return decoded[0].decode(decoded[1] or 'utf-8', errors='ignore')
        return str(decoded[0])
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()