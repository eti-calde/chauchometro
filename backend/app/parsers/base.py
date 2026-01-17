from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

class TransactionType(str, Enum):
    COMPRA = "compra"
    TRANSFERENCIA = "transferencia"
    ABONO = "abono"
    GIRO = "giro"
    OTRO = "otro"

class Transaction:
    """Modelo de transacción parseada"""
    def __init__(
        self,
        bank: str,
        type: TransactionType,
        amount: Decimal,
        description: str,
        date: datetime,
        merchant: Optional[str] = None,
        last_digits: Optional[str] = None,
        email_id: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.bank = bank
        self.type = type
        self.amount = amount
        self.description = description
        self.date = date
        self.merchant = merchant
        self.last_digits = last_digits
        self.email_id = email_id
        self.raw_data = raw_data or {}
    
    def __repr__(self):
        return f"Transaction({self.type}, ${self.amount}, {self.merchant or self.description}, {self.date})"

class BaseParser(ABC):
    """Clase base para parsers de bancos"""
    
    def __init__(self):
        self.bank_name = self.__class__.__name__.replace('Parser', '').lower()
    
    @abstractmethod
    def can_parse(self, email_message) -> bool:
        """Determina si este parser puede procesar el email"""
        pass
    
    @abstractmethod
    def parse(self, email_message) -> Optional[Transaction]:
        """Parsea el email y retorna una transacción"""
        pass