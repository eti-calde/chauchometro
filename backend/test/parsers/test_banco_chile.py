import pytest
from datetime import datetime
from decimal import Decimal
from app.parsers.banco_chile import BancoChileParser
from app.parsers.base import TransactionType
from app.email.connection import EmailMessage


class TestBancoChileParser:
    """Tests para el parser de emails del Banco de Chile"""

    @pytest.fixture
    def parser(self):
        return BancoChileParser()

    # =========================================================================
    # Fixtures con emails de ejemplo (formato real del banco)
    # =========================================================================

    @pytest.fixture
    def email_cargo_cuenta(self):
        """Email real de cargo en cuenta (compra con débito)"""
        return EmailMessage(
            uid="758",
            subject="Cargo en Cuenta",
            sender="Banco de Chile <enviodigital@bancochile.cl>",
            date=datetime(2025, 12, 18, 22, 0, 26),
            body_html="""
            <html>
            <body>
                <p>Etienne Rojas Calderon:</p>
                <p>Te informamos que se ha realizado una compra por $5.390
                con cargo a Cuenta ****3204 en HIPER VINA CENTRO el 18/12/2025 19:00.</p>
                <p>Revisa Saldos y Movimientos en App Mi Banco o Banco en Línea.</p>
            </body>
            </html>
            """,
            body_text="",
            raw_email=b""
        )

    @pytest.fixture
    def email_giro_cajero(self):
        """Email real de giro en cajero automático"""
        return EmailMessage(
            uid="755",
            subject="Giro con Tarjeta de Débito",
            sender="Banco de Chile <enviodigital@bancochile.cl>",
            date=datetime(2025, 12, 13, 17, 18, 41),
            body_html="""
            <html>
            <body>
                <p>Etienne Rojas Calderon:</p>
                <p>Te informamos que se ha realizado un giro en Cajero por $30.000
                con cargo a Cuenta ****3204 el 13/12/2025 14:18.</p>
                <p>Revisa Saldos y Movimientos en App Mi Banco o Banco en Línea.</p>
            </body>
            </html>
            """,
            body_text="",
            raw_email=b""
        )

    @pytest.fixture
    def email_cartola(self):
        """Email de cartola (no es transacción, debe ignorarse)"""
        return EmailMessage(
            uid="800",
            subject="Cartola Cuenta Corriente",
            sender="Banco de Chile <enviodigital@bancochile.cl>",
            date=datetime(2026, 1, 3, 4, 31, 15),
            body_html="""
            <html>
            <body>
                <p>Esta es tu Cartola Cuenta Corriente</p>
                <p>Adjunto a este mail enviamos tu Cartola de Cuenta Corriente.</p>
            </body>
            </html>
            """,
            body_text="",
            raw_email=b""
        )

    @pytest.fixture
    def email_otro_banco(self):
        """Email de otro banco (no debe parsearse)"""
        return EmailMessage(
            uid="999",
            subject="Compra realizada",
            sender="notificaciones@otrobanco.cl",
            date=datetime.now(),
            body_html="<html><body>Compra por $10.000</body></html>",
            body_text="",
            raw_email=b""
        )

    @pytest.fixture
    def email_mal_formateado(self):
        """Email del banco con formato inesperado"""
        return EmailMessage(
            uid="888",
            subject="Cargo en Cuenta",
            sender="Banco de Chile <enviodigital@bancochile.cl>",
            date=datetime.now(),
            body_html="""
            <html>
            <body>
                <p>Este email no tiene el formato esperado</p>
                <p>Sin monto ni información de transacción</p>
            </body>
            </html>
            """,
            body_text="",
            raw_email=b""
        )

    @pytest.fixture
    def email_compra_online(self):
        """Email de compra online con nombre de comercio especial"""
        return EmailMessage(
            uid="806",
            subject="Cargo en Cuenta",
            sender="Banco de Chile <enviodigital@bancochile.cl>",
            date=datetime(2026, 1, 4, 23, 24, 11),
            body_html="""
            <html>
            <body>
                <p>Te informamos que se ha realizado una compra por $41.970
                con cargo a Cuenta ****3204 en DP     *IKEA.COM el 04/01/2026 20:24.</p>
            </body>
            </html>
            """,
            body_text="",
            raw_email=b""
        )

    # =========================================================================
    # Tests de detección (can_parse)
    # =========================================================================

    def test_can_parse_banco_chile_email(self, parser, email_cargo_cuenta):
        """Debe detectar emails del Banco de Chile"""
        assert parser.can_parse(email_cargo_cuenta) is True

    def test_cannot_parse_other_bank(self, parser, email_otro_banco):
        """No debe parsear emails de otros bancos"""
        assert parser.can_parse(email_otro_banco) is False

    # =========================================================================
    # Tests de parsing - Cargo en Cuenta (Compra)
    # =========================================================================

    def test_parse_cargo_cuenta(self, parser, email_cargo_cuenta):
        """Debe parsear correctamente un cargo en cuenta"""
        transaction = parser.parse(email_cargo_cuenta)

        assert transaction is not None
        assert transaction.type == TransactionType.COMPRA
        assert transaction.amount == Decimal("5390")
        assert transaction.merchant == "HIPER VINA CENTRO"
        assert transaction.last_digits == "3204"
        assert transaction.bank == "banco_chile"
        assert transaction.date == datetime(2025, 12, 18, 19, 0)

    def test_parse_compra_online(self, parser, email_compra_online):
        """Debe parsear compras online con nombres especiales"""
        transaction = parser.parse(email_compra_online)

        assert transaction is not None
        assert transaction.type == TransactionType.COMPRA
        assert transaction.amount == Decimal("41970")
        assert "IKEA" in transaction.merchant
        assert transaction.last_digits == "3204"

    # =========================================================================
    # Tests de parsing - Giro en Cajero
    # =========================================================================

    def test_parse_giro_cajero(self, parser, email_giro_cajero):
        """Debe parsear correctamente un giro en cajero"""
        transaction = parser.parse(email_giro_cajero)

        assert transaction is not None
        assert transaction.type == TransactionType.GIRO
        assert transaction.amount == Decimal("30000")
        assert transaction.last_digits == "3204"
        assert transaction.bank == "banco_chile"
        assert transaction.date == datetime(2025, 12, 13, 14, 18)

    # =========================================================================
    # Tests de emails ignorados
    # =========================================================================

    def test_cartola_ignored(self, parser, email_cartola):
        """La cartola no es transacción, debe retornar None"""
        transaction = parser.parse(email_cartola)
        assert transaction is None

    # =========================================================================
    # Tests de manejo de errores
    # =========================================================================

    def test_email_mal_formateado_returns_none(self, parser, email_mal_formateado):
        """Email sin monto debe retornar None sin crashear"""
        transaction = parser.parse(email_mal_formateado)
        assert transaction is None

    def test_email_html_vacio(self, parser):
        """Email con HTML vacío no debe crashear"""
        email = EmailMessage(
            uid="777",
            subject="Cargo en Cuenta",
            sender="enviodigital@bancochile.cl",
            date=datetime.now(),
            body_html="",
            body_text="",
            raw_email=b""
        )
        transaction = parser.parse(email)
        assert transaction is None

    def test_email_html_none(self, parser):
        """Email con HTML None no debe crashear"""
        email = EmailMessage(
            uid="666",
            subject="Cargo en Cuenta",
            sender="enviodigital@bancochile.cl",
            date=datetime.now(),
            body_html=None,
            body_text="",
            raw_email=b""
        )
        transaction = parser.parse(email)
        assert transaction is None

    # =========================================================================
    # Tests de extracción de campos específicos
    # =========================================================================

    def test_extrae_monto_sin_puntos(self, parser):
        """Debe extraer montos pequeños sin separador de miles"""
        email = EmailMessage(
            uid="111",
            subject="Cargo en Cuenta",
            sender="enviodigital@bancochile.cl",
            date=datetime.now(),
            body_html="""
            <html><body>
            <p>Te informamos que se ha realizado una compra por $50
            con cargo a Cuenta ****1234 en COMERCIO el 01/01/2026 10:00.</p>
            </body></html>
            """,
            body_text="",
            raw_email=b""
        )
        transaction = parser.parse(email)

        assert transaction is not None
        assert transaction.amount == Decimal("50")

    def test_extrae_monto_con_puntos(self, parser):
        """Debe extraer montos grandes con separador de miles"""
        email = EmailMessage(
            uid="222",
            subject="Cargo en Cuenta",
            sender="enviodigital@bancochile.cl",
            date=datetime.now(),
            body_html="""
            <html><body>
            <p>Te informamos que se ha realizado una compra por $108.885
            con cargo a Cuenta ****1234 en CLAUDE.AI el 13/01/2026 08:28.</p>
            </body></html>
            """,
            body_text="",
            raw_email=b""
        )
        transaction = parser.parse(email)

        assert transaction is not None
        assert transaction.amount == Decimal("108885")
