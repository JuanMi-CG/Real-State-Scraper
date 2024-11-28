import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Obtener credenciales de los Secrets
sender_email = os.environ["EMAIL_USER"]
receiver_email = os.environ["EMAIL_RECEIVER"]  # Fix typo here
password = os.environ["EMAIL_PASS"]

subject = "Hello from GitHub Actions"
body = "Este es un correo enviado desde un script de Python ejecutado en una GitHub Action."

# Crear el mensaje de correo
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject

message.attach(MIMEText(body, "plain"))

# Enviar el correo
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Cifrado TLS
        server.login(sender_email, password)  # Inicio de sesión
        server.sendmail(sender_email, receiver_email, message.as_string())  # Enviar correo
        print("Correo enviado con éxito")
except Exception as e:
    print(f"Error al enviar el correo: {e}")
