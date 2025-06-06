import os
import pytest
import smtplib
import importlib
from email.message import EmailMessage

from src.models.MailModels import EmailDetails

# Import do módulo correto: src.services.email.sendMail
mail_mod = importlib.import_module("src.services.email.sendMail")


# -------------------------
# Fixtures para variáveis de ambiente e monkeypatch de constantes no módulo
# -------------------------
@pytest.fixture(autouse=True)
def set_env_vars_and_module_vars(monkeypatch):
    """
    Define variáveis de ambiente necessárias e recarrega o módulo sendMail
    para que ele reflita as novas variáveis, depois sobrescreve as constantes.
    """
    # Define as variáveis de ambiente
    monkeypatch.setenv("EMAIL_HOST", "smtp.testserver.com")
    monkeypatch.setenv("EMAIL_PORT", "587")
    monkeypatch.setenv("EMAIL_USER", "user@test.com")
    monkeypatch.setenv("EMAIL_PASS", "password123")
    monkeypatch.setenv("WHATSAPP_CONTATO", "+551199999999")
    monkeypatch.setenv("EMAIL_CONTATO", "contato@test.com")

    # Recarrega o módulo para que ele leia as novas variáveis
    importlib.reload(mail_mod)

    # Sobrescreve as constantes do módulo (caso já tenham sido lidas uma vez)
    monkeypatch.setattr(mail_mod, "EMAIL_HOST", os.getenv("EMAIL_HOST"))
    monkeypatch.setattr(mail_mod, "EMAIL_PORT", int(os.getenv("EMAIL_PORT")))
    monkeypatch.setattr(mail_mod, "EMAIL_USER", os.getenv("EMAIL_USER"))
    monkeypatch.setattr(mail_mod, "EMAIL_PASS", os.getenv("EMAIL_PASS"))
    monkeypatch.setattr(mail_mod, "WHATSAPP_CONTATO", os.getenv("WHATSAPP_CONTATO"))
    monkeypatch.setattr(mail_mod, "EMAIL_CONTATO", os.getenv("EMAIL_CONTATO"))


# -------------------------
# Fake SMTP para sucesso
# -------------------------
class FakeSMTP:
    """
    FakeSMTP simula smtplib.SMTP para testes de sucesso:
    - starttls()
    - login()
    - send_message()
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.started_tls = False
        self.logged_in = False
        self.sent_message = None

        # Armazena a última instância criada para inspeção
        FakeSMTP._last_instance = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, user, password):
        # Verifica que login usa as constantes do módulo recarregado
        assert user == mail_mod.EMAIL_USER
        assert password == mail_mod.EMAIL_PASS
        self.logged_in = True

    def send_message(self, msg: EmailMessage):
        # Armazena a mensagem para inspeção posterior
        self.sent_message = msg


# -------------------------
# Fake SMTP para erro
# -------------------------
class FakeSMTPError:
    """
    FakeSMTPError simula smtplib.SMTP que falha ao enviar a mensagem.
    """
    def __init__(self, host, port):
        FakeSMTPError._last_instance = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        pass

    def send_message(self, msg: EmailMessage):
        raise smtplib.SMTPException("Simulated send failure")


# -------------------------
# Teste de envio bem-sucedido
# -------------------------
def test_send_email_success(monkeypatch):
    # Monkeypatcha smtplib.SMTP para usar FakeSMTP
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)

    # Cria EmailDetails válido
    email_details = EmailDetails(
        email="cliente@example.com",
        name="Cliente Teste",
        type="Aniversário",
        date="2025-06-10",
        value="150.00",
        payment_link="https://testlink.com/pagar/123",
    )

    # Chama a função send_email do módulo recarregado
    mail_mod.send_email(email_details)

    # Recupera a instância usada pelo FakeSMTP
    smtp_instance = FakeSMTP._last_instance
    sent_msg: EmailMessage = smtp_instance.sent_message

    # Validações do EmailMessage
    assert isinstance(sent_msg, EmailMessage)
    assert sent_msg["Subject"] == "Orçamento EloDrinks para sua festa 🥳"
    assert sent_msg["From"] == mail_mod.EMAIL_USER
    assert sent_msg["To"] == email_details.email

    # Verifica corpo texto simples
    plain = sent_msg.get_body(preferencelist=("plain",))
    assert plain is not None
    assert "Seu cliente precisa de um e-mail com HTML para visualizar este conteúdo." in plain.get_content()

    # Verifica corpo HTML
    html_part = sent_msg.get_body(preferencelist=("html",))
    assert html_part is not None
    html_content = html_part.get_content()
    assert f"Olá {email_details.name}" in html_content
    assert f"{email_details.type}" in html_content
    assert f"{email_details.date}" in html_content
    assert f"R${email_details.value}" in html_content
    assert email_details.payment_link in html_content
    assert mail_mod.WHATSAPP_CONTATO in html_content
    assert mail_mod.EMAIL_CONTATO in html_content


# -------------------------
# Teste de envio que falha
# -------------------------
def test_send_email_failure(monkeypatch):
    # Monkeypatcha smtplib.SMTP para usar FakeSMTPError
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTPError)

    # Cria EmailDetails válido
    email_details = EmailDetails(
        email="cliente@example.com",
        name="Cliente Teste",
        type="Casamento",
        date="2025-07-01",
        value="200.00",
        payment_link="https://testlink.com/pagar/456",
    )

    # Espera que o envio lance Exception com "Erro ao enviar e-mail"
    with pytest.raises(Exception) as excinfo:
        mail_mod.send_email(email_details)

    msg = str(excinfo.value)
    assert "Erro ao enviar e-mail" in msg
    assert "Simulated send failure" in msg
