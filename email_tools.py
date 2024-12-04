import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

def get_email_content(file_path):
    # Cargar el DataFrame
    df = pd.read_pickle(file_path)
    
    # Verificar si hay datos
    if df.empty:
        subject = "Actualización: No hay nuevas viviendas disponibles"
        body = "No se han registrado nuevas viviendas en el sistema en el último lote de datos."
        return subject, body
    
    # Generar subject
    num_viviendas = len(df)
    subject = f"Actualización axius: {num_viviendas} nuevas viviendas disponibles"
    
    # Generar body
    resumen = df.to_html(index=False, border=0)
    body = (
        f"Estimado equipo,\n\n"
        f"Se han registrado {num_viviendas} nuevas viviendas en el sistema. Adjunto los datos a continuación:\n\n"
        f"{resumen}\n\n"
        f"Un saludo! Nos vemos pronto."
    )
    
    return subject, body



def send_email(sender_email, receiver_email, password, subject, body):
    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Enable TLS encryption
            server.login(sender_email, password)  # Log in to the SMTP server
            server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email
            print("Correo enviado con éxito")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
