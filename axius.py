import os
import math
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ctools.clogger import logger
from ctools import cscrap


COLUMNS = ["ref", "price", "url", "inmobiliaria"]
FOLDER_NAME = 'axius'

def extract_data_from_html(html_file):
    """Extract relevant data from the HTML file using BeautifulSoup."""
    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        # Step 1: Extract DIVs
        div_elements = soup.select("div.mh-estate-vertical__primary")
        div_data = []

        for div in div_elements:
            try:
                # Extract Ref and Price tags from the div
                ref_tag = div.find("span", string=lambda s: s and "Ref.:" in s)
                price_tag = div.find("span", string=lambda s: s and "Precio:" in s)

                ref = ref_tag.string.replace("Ref.:", "").strip() if ref_tag else None
                price = price_tag.string.replace("Precio:", "").replace("€", "").strip() if price_tag else None

                # Store the extracted data
                if ref or price:
                    div_data.append({"ref": ref, "price": price})
                else:
                    logger.info(f"Skipping div with no data: {div}")

            except Exception as e:
                logger.error(f"Error processing div {div}: {e}")

        # Step 2: Extract Articles
        articles = soup.find_all("article", id=lambda x: x and x.startswith("inmueble_"))
        article_data_list = []

        for article in articles:
            try:
                # Extract property code from article ID
                property_code = article.get("id").replace("inmueble_", "").strip()
                # Store property code for URL construction
                article_data_list.append(f"https://arxus.es/ficha-inmueble/?cod_inmueble={property_code}")
            except Exception as e:
                logger.error(f"Error processing article {article}: {e}")

        # Step 3: Merge DIV and Article Data
        final_data = []
        for idx, item in enumerate(div_data):
            ref = item.get("ref")
            price = item.get("price")

            # Get the corresponding URL from article_data_list by index
            property_url = article_data_list[idx] if idx < len(article_data_list) else None

            if ref and property_url:
                final_data.append({"ref": ref, "price": price, "url": property_url, "inmobiliaria": FOLDER_NAME})
            else:
                logger.error(f"Skipping item due to missing URL: ref={ref}, price={price}")

        return pd.DataFrame(final_data)

    except Exception as e:
        logger.error(f"Error parsing HTML file {html_file}: {e}")
        return pd.DataFrame()










def process_page(driver, url, html_file, pickle_file, new_pickle_file):
    """Process a single page and update the main and new properties pickle files."""
    condition = EC.presence_of_element_located((By.CLASS_NAME, "mh-estate-vertical__primary"))
    cscrap.save_html(driver, url, html_file, wait_until=condition)
    extracted_data = extract_data_from_html(html_file)

    # Load existing data
    existing_data = cscrap.load_or_initialize_pickle(pickle_file, COLUMNS)

    # Identify new properties
    temp_existing_data = existing_data[existing_data['inmobiliaria'] == FOLDER_NAME]
    new_properties = extracted_data[
        (~extracted_data["ref"].isin(temp_existing_data["ref"])) &
        (extracted_data["inmobiliaria"] == FOLDER_NAME)
    ]
    
    # Update the main dataset
    updated_data = cscrap.merge_dataframes(existing_data, extracted_data)
    cscrap.save_to_pickle(updated_data, pickle_file)

    # Save new properties to separate pickle
    if not new_properties.empty:
        existing_new_properties = cscrap.load_or_initialize_pickle(new_pickle_file, COLUMNS)
        combined_new_properties = cscrap.merge_dataframes(existing_new_properties, new_properties)
        cscrap.save_to_pickle(combined_new_properties, new_pickle_file)

    logger.info(f"Number of items: {len(updated_data)}")

def get_total_items(driver, url, output_dir):
    html_file = os.path.join(output_dir, f"page_1.html")
    condition = EC.presence_of_element_located((By.CLASS_NAME, "mh-search__results"))
    cscrap.save_html(driver, url, html_file, wait_until=condition)

    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        elements = soup.select("li.mh-search__results")
        for element in elements:
            total_items = int(element.string.strip().split()[0])
            break

        return total_items
    except Exception as e:
        logger.info(f"Error get_total_items(). Exception: {e}")
        return 0


def scrape_all_pages(base_url, page_template, output_dir, main_pickle_file, new_pickle_file, items_per_page):
    """Scrape multiple pages and consolidate the data, starting with a new 'new_properties.pkl'."""
    os.makedirs(output_dir, exist_ok=True)

    driver = cscrap.initialize_driver()
    try:
        total_items = get_total_items(driver, base_url, output_dir)
        logger.info(f'Total Properties: {total_items}')
        total_pages = math.ceil(total_items / items_per_page)
        
        for page in range(1, total_pages + 1):
            if page == 1:
                url = base_url  # First page uses the base URL
            else:
                url = page_template.format(page=page - 1)  # Adjust for correct page numbering
            
            html_file = os.path.join(output_dir, f"page_{page}.html")
            logger.info('-' * 100)
            logger.info(f"Scraping page {page}/{total_pages}...")
            
            process_page(driver, url, html_file, main_pickle_file, new_pickle_file)
    except Exception as e:
        logger.info(f'Excepcion: {e}')
    finally:
        driver.quit()


# def scrape_all_pages(base_url, page_template, output_dir, main_pickle_file, new_pickle_file, items_per_page):
#     """Scrape multiple pages and consolidate the data, starting with a new 'new_properties.pkl'."""
#     os.makedirs(output_dir, exist_ok=True)

#     driver = cscrap.initialize_driver()
#     try:
#         total_items = get_total_items(driver, base_url, output_dir)
#         logger.info(f'Total Properties: {total_items}')
#         total_pages = math.ceil(total_items / items_per_page)
#         for page in range(total_pages):
#             url = base_url if page == 0 else page_template.format(page=page)
#             html_file = os.path.join(output_dir, f"page_{page + 1}.html")
#             logger.info('-'*100)
#             logger.info(f"Scraping page {page + 1}/{total_pages}...")
#             process_page(driver, url, html_file, main_pickle_file, new_pickle_file)
#     except Exception as e:
#         logger.info(f'Excepcion: {e}')
#     finally:
#         driver.quit()




def scrap(folder_name):
    properties_path = 'results/properties.pkl'
    new_properties_path = 'results/new_properties.pkl'
    # ----------------------- SCRAPPING ------------------------------------ 

    first_page_url = "https://arxus.es/propiedades/?TipoOperacion=Venta&Precio2=50000"
    page_url_template = "https://arxus.es/propiedades/?TipoOperacion=Venta&Precio2=50000&pagina={page}"
    items_per_page = 12

    scrape_all_pages(
        base_url=first_page_url,
        page_template=page_url_template,
        output_dir=folder_name,
        main_pickle_file=properties_path,
        new_pickle_file=new_properties_path,
        items_per_page=items_per_page,
    )