import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from src.models.MailModels import EmailDetails

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

WHATSAPP_CONTATO = os.getenv("WHATSAPP_CONTATO")
EMAIL_CONTATO = os.getenv("EMAIL_CONTATO")


def send_email(email_details: EmailDetails):
    msg = EmailMessage()
    msg["Subject"] = "Orçamento EloDrinks para sua festa 🥳"
    msg["From"] = EMAIL_USER
    msg["To"] = email_details.email

    corpo_html = f"""
    <html>
        <body>
            <p>Olá {email_details.name},<br><br>
            Nós da <strong>EloDrinks</strong> olhamos com cuidado e fizemos com carinho o orçamento para sua festa de <strong>{email_details.type}</strong> na data <strong>{email_details.date}</strong>.<br><br>
            O valor final para seu pedido é <strong>R${email_details.value}</strong>.<br><br>
            <a href="{email_details.payment_link}" style="padding:10px 15px; background-color:#28a745; color:white; text-decoration:none; border-radius:5px;">Confirmar pedido e realizar pagamento</a><br><br>
            Caso tenha alguma ressalva, entre em contato conosco:<br>
            📞 WhatsApp: {WHATSAPP_CONTATO}<br>
            📧 Email: {EMAIL_CONTATO}<br><br>
            Atenciosamente,<br>
            Equipe <strong>EloDrinks</strong></p>
        </body>
    </html>
    """

    msg.set_content("Seu cliente precisa de um e-mail com HTML para visualizar este conteúdo.")
    msg.add_alternative(corpo_html, subtype='html')

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        raise Exception(f"Erro ao enviar e-mail: {e}")
