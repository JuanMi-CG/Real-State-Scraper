import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os

from ctools import time_lapse
from ctools.clogger import logger


SEND_EMAILS = (os.getenv('SEND_EMAILS', 'false') == 'true')


def emailing(df, new_properties_path, sender_email, receiver_email, password):
    if not df.empty:
        logger.info(f'{len(df)} new properties are available. Sending email...')
        # aws.upload_file_to_s3(bucket_name, properties_path, s3_key)
        subject, body = get_email_content(new_properties_path)
        send_email(sender_email, receiver_email, password, subject, body)
    else:
        last_email_days = time_lapse.days_since_last_email()
        if last_email_days > 7:
            send_health_reminder(sender_email, receiver_email, password, last_email_days)
        else:
            logger.info("No new properties are available. Email won't be sent.")





def get_email_content(file_path):
    
    # Cargar el DataFrame
    df = pd.read_pickle(file_path)
    
    # Verificar si hay datos
    if df.empty:
        subject = "Actualización: No hay nuevas viviendas disponibles"
        body = "<p>No se han registrado nuevas viviendas en el sistema en el último lote de datos.</p>"
        return subject, body
    
    # Generar subject
    num_viviendas = len(df)
    subject = f"Actualización: {num_viviendas} nuevas viviendas disponibles"
    
    # Generar resumen en formato HTML
    resumen = df.to_html(index=False, border=1, classes="dataframe", justify="center")
    
    # Crear un cuerpo de correo con HTML completo
    body = f"""
    <html>
    <head>
    <style>
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }}
        .dataframe th {{
            background-color: #f2f2f2;
        }}
    </style>
    </head>
    <body>
        <p>Estimado equipo,</p>
        <p>Se han registrado {num_viviendas} nuevas viviendas en el sistema. Adjunto los datos a continuación:</p>
        {resumen}
        <p>Un saludo! Nos vemos pronto.</p>
    </body>
    </html>
    """
    
    return subject, body




def send_email(sender_email, receiver_email, password, subject, body):
    if SEND_EMAILS:
        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        receiver_email_list = receiver_email.split(',')

        try:
            # Connect to the SMTP server and send the email
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Enable TLS encryption
                server.login(sender_email, password)  # Log in to the SMTP server
                server.sendmail(sender_email, receiver_email_list, message.as_string())  # Send the email
                logger.info("Correo enviado con éxito")
                time_lapse.update_last_email_date()
        except Exception as e:
            logger.error(f"Error al enviar el correo: {e}")
    else:
        logger.info("Email would be sent but SEND_EMAILS is set on False to avois spaming, email won't be sent")


def send_health_reminder(sender_email, receiver_email, password, last_email_days):
    # Health reminder
    subject = "SCRAPER - Sin viviendas nuevas"
    html_body = f"""
    <html>
        <body>
            <p>Hola!</p>
            <p>Sigo scrapeando las webs pero no ha habido viviendas en los últimos <strong>{last_email_days} días</strong>.</p>
            <p>Escribiré de nuevo en <strong>7 días</strong> o cuando aparezcan nuevas viviendas.</p>
            <p>Nos vemos!</p>
        </body>
    </html>
    """
    send_email(sender_email, receiver_email, password, subject, html_body)