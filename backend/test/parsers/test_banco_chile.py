import pytest
from datetime import datetime
from decimal import Decimal
from app.parsers.banco_chile import BancoChileParser
from app.email.connection import EmailMessage

class TestBancoChileParser:
    
    @pytest.fixture
    def parser(self):
        return BancoChileParser()
    
    @pytest.fixture
    def email_compra(self):
        """Email de ejemplo de compra"""
        return EmailMessage(
            uid="123",
            subject="Compra realizada con tu Tarjeta de Débito",
            sender="EnvioDigital@BancoChile.cl",
            date=datetime.now(),
            body_html="""
            <html>
                <body>
                    <p>Estimado Cliente,</p>
                    <p>Te informamos que se realizó una compra con tu tarjeta terminada en 1234</p>
                    <p><strong>SUPERMERCADO JUMBO</strong></p>
                    <p>Por un monto de <b>$25.990</b></p>
                    <p>Fecha: 15/03/2024 a las 14:30</p>
                </body>
            </html>
            """,
            body_text="",
            raw_email=b""
        )
    
    def test_can_parse_banco_chile_email(self, parser, email_compra):
        assert parser.can_parse(email_compra) == True
    
    def test_parse_compra(self, parser, email_compra):
        transaction = parser.parse(email_compra)
        
        assert transaction is not None
        assert transaction.type == "compra"
        assert transaction.amount == Decimal("25990")
        assert transaction.merchant == "SUPERMERCADO JUMBO"
        assert transaction.last_digits == "1234"
        assert transaction.bank == "banco_chile"