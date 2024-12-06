import os
import pandas as pd
import axius
import aws
import email_tools
import time_lapse

from clogger import logger

# # Load environment variables from .env file for local testing
# from dotenv import load_dotenv
# load_dotenv(override=True)

# EMAIL Config
sender_email = os.environ["EMAIL_USER"]
receiver_email = os.environ["EMAIL_RECEIVER"]
password = os.environ["EMAIL_PASS"]

# --------------------------------- EJECUCIÓN PRINCIPAL
folder_name = 'axius'
axius.scrap_axius(folder_name, sender_email, receiver_email, password)

axius_df = pd.read_pickle('axius/properties.pkl')
email_tools.emailing(axius_df, folder_name, sender_email, receiver_email, password)