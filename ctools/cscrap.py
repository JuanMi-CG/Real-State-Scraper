import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

from ctools.clogger import logger



def initialize_driver():
    """Initialize and return a Selenium WebDriver with configured options."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def save_html(driver, url, output_file, max_retries=2, wait_until=None, wait_timeout=10):
    if os.path.exists(output_file):
        logger.info(f"Skipping download: {output_file} already exists.")
        return

    retries = 0
    while retries < max_retries:
        try:
            time.sleep(random.uniform(2, 5))
            logger.info(f'Entrando en la web: {url}')
            driver.get(url)

            # If there's a wait condition, apply it
            if wait_until:
                WebDriverWait(driver, wait_timeout).until(wait_until)

            # Save the HTML content
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(driver.page_source)

            # Check if the file has content
            if os.path.getsize(output_file) > 0:
                logger.info(f"HTML saved to {output_file}.")
                return
            else:
                logger.warning(f"Empty HTML content for {url}. Retrying...")
                retries += 1

        except Exception as e:
            logger.error(f"Error accessing {url} on attempt {retries + 1}: {e}")
            retries += 1

    logger.error(f"Failed to save non-empty HTML content for {url} after {max_retries} retries.")

# def save_html(driver, url, output_file):
#     """Save the HTML content of a URL to a local file."""
#     if os.path.exists(output_file):
#         logger.info(f"Skipping download: {output_file} already exists.")
#         return

#     try:
#         time.sleep(random.uniform(2, 5))
#         print(f'Entrando en la web: {url}')
#         driver.get(url)
#         with open(output_file, "w", encoding="utf-8") as file:
#             file.write(driver.page_source)
#         logger.info(f"HTML saved to {output_file}.")
#     except Exception as e:
#         logger.error(f"Error accessing {url}: {e}")


def load_or_initialize_pickle(file_path, columns):
    """Load existing pickle file or initialize a new DataFrame."""
    if os.path.exists(file_path):
        return pd.read_pickle(file_path)
    return pd.DataFrame(columns=columns)


def save_to_pickle(dataframe, file_path):
    """Save a DataFrame to a pickle file."""
    dataframe.to_pickle(file_path)



def merge_dataframes(existing_df, new_df):
    """Merge existing DataFrame with new data, avoiding duplicates based on 'ref' and 'inmobiliaria'."""
    combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=["ref", "inmobiliaria"], keep="last").reset_index(drop=True)
    return combined_df
