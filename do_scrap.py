import os
import pandas as pd
import axius
import aws
import email_tools
import time_lapse

# Load environment variables from .env file for local testing
from dotenv import load_dotenv
load_dotenv()

# EMAIL Config
sender_email = os.environ["EMAIL_USER"]
receiver_email = os.environ["EMAIL_RECEIVER"]
password = os.environ["EMAIL_PASS"]

# AWS Config
bucket_name = os.environ["BUCKET_NAME"]
properties_path = os.environ["PROPERTIES_PATH"]
s3_key = os.environ["S3_KEY"]

# New Properties
new_properties_path = os.environ["NEW_PROPERTIES_PATH"]


# --------------------------------- EJECUCIÓN PRINCIPAL
aws.download_file_from_s3(bucket_name, s3_key, properties_path)
axius.scrap_axius()

df = pd.read_pickle(new_properties_path)
if not df.empty:
    print(f'{len(df)} new properties are available. Sending email...')
    aws.upload_file_to_s3(bucket_name, properties_path, s3_key)
    subject, body = email_tools.get_email_content(new_properties_path)
    email_tools.send_email(sender_email, receiver_email, password, subject, body)
else:
    print("No new properties are available. Email won't be sent.")
    last_email = time_lapse.days_since_last_email()
    if time_lapse.days_since_last_email() > 7:
        # Health reminder
        subject = "AXIUS SCRAPER - Sin viviendas nuevas"
        body = f"Hola!\n\nSigo scrapeando la web de axius pero no ha habido viviendas en los últimos {last_email} dias.\n\n Escribiré de nuevo en 7 dias o \n\nNos vemos!"
        email_tools.send_email(sender_email, receiver_email, password, subject, body)
        time_lapse.update_last_email_date()