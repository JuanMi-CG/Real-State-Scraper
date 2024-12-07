import os
import pandas as pd

from ctools.clogger import logger
from ctools import cscrap
from ctools import email_tools

# # Load environment variables from .env file for local testing
# from dotenv import load_dotenv
# load_dotenv(override=True)

# EMAIL Config
sender_email = os.environ["EMAIL_USER"]
receiver_email = os.environ["EMAIL_RECEIVER"]
password = os.environ["EMAIL_PASS"]

COLUMNS = ["ref", "price", "url", "inmobiliaria"]


# Initialize the 'new_properties.pkl' as an empty DataFrame
new_properties = 'results/new_properties.pkl'
properties = 'results/properties.pkl'

# --------------------------------- EJECUCIÓN PRINCIPAL
empty_df = pd.DataFrame(columns=COLUMNS)
cscrap.save_to_pickle(empty_df, new_properties)
logger.info(f"Initialized a fresh new_properties file at {new_properties}.")


# AXIUS
import axius
folder_name = 'axius'
axius.scrap(folder_name)

axius_df = pd.read_pickle(properties)
logger.info(axius_df)

# INMOCASAL
import inmocasal
folder_name = 'inmocasal'
inmocasal.scrap(folder_name)

inmocasal_df = pd.read_pickle(properties)
logger.info(inmocasal_df)


# ------------- EMAILING
logger.info('-'*100)
new_properties_df = pd.read_pickle(new_properties)
logger.info(new_properties_df)
email_tools.emailing(new_properties_df, new_properties, sender_email, receiver_email, password)