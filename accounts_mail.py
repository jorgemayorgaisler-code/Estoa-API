"""Optional SMTP delivery. No credentials or tokens in logs."""
import os
import ssl
import smtplib
from email.message import EmailMessage

def send_code(email,token,purpose):
    if purpose not in ("verify","reset"):
        raise ValueError("Unknown purpose")
    host=os.environ["ESTOA_SMTP_HOST"]
    sender=os.environ["ESTOA_SMTP_FROM"]
    user=os.environ["ESTOA_SMTP_USER"]
    password=os.environ["ESTOA_SMTP_PASSWORD"]
    msg=EmailMessage()
    msg["From"]=sender
    msg["To"]=email
    msg["Subject"]="ESTOA: verifica tu cuenta" if purpose=="verify" else "ESTOA: recupera tu contraseña"
    msg.set_content("Tu código ESTOA es: "+token+"\nVence en 30 minutos. Si no solicitaste este código, ignora este mensaje.")
    with smtplib.SMTP_SSL(host,int(os.environ.get("ESTOA_SMTP_PORT","465")),timeout=10,context=ssl.create_default_context()) as smtp:
        smtp.login(user,password)
        smtp.send_message(msg)
