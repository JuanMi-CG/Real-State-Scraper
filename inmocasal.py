import os
import math
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ctools.clogger import logger
from ctools import cscrap


COLUMNS = ["ref", "price", "url", "inmobiliaria"]
FOLDER_NAME = 'inmocasal'


def extract_data_from_html(html_file):
    """Extract relevant data from the HTML file using BeautifulSoup."""
    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        # Step 1: Extract DIVs
        div_elements = soup.select("div.zt-prop-blog-minis-item")
        div_data = []

        for div in div_elements:
            try:
                # Extract Ref and Price tags from the div
                ref_tag = div.find("strong", string=lambda s: s and "Ref. " in s)
                price_tag = div.find("b")
                
                ref = ref_tag.string.replace("Ref. ", "").strip() if ref_tag else None
                price = price_tag.string.replace("€", "").strip() if price_tag else None
                url = f"https://www.inmocasal.es/propiedad/?referencia={ref}"

                # Store the extracted data
                if ref or price:
                    div_data.append({"ref": ref, "price": price, "url": url, "inmobiliaria": FOLDER_NAME})
                else:
                    logger.info(f"Skipping div with no data: {div}")

            except Exception as e:
                logger.error(f"Error processing div {div}: {e}")

        # Return the DataFrame after processing all divs
        return pd.DataFrame(div_data)
        
    except Exception as e:
        logger.error(f"Error extract_data_from_html(): {e}")







def process_page(driver, url, html_file, pickle_file, new_pickle_file):
    """Process a single page and update the main and new properties pickle files."""
    condition = EC.presence_of_element_located((By.CLASS_NAME, "zt-prop-blog-minis-item"))
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

def get_total_pages(driver, url, output_dir):
    html_file = os.path.join(output_dir, f"page_1.html")
    condition = EC.presence_of_element_located((By.CLASS_NAME, "zt-paginacion"))
    cscrap.save_html(driver, url, html_file, wait_until=condition)

    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        # Select the div with the class "zt-paginacion"
        div_elements = soup.select("div.zt-paginacion")
        
        # Iterate over div_elements to find the correct span
        for div in div_elements:
            span = div.find("span", string=lambda s: s and "Página 1 de " in s)
            if span:
                total_pages = int(span.string.strip().replace("Página 1 de ", ""))
                logger.info(f'Número de páginas: {total_pages}')
                return total_pages

        # If no span is found, return 0
        logger.info("No matching span found for total pages.")
        return 0

    except Exception as e:
        logger.info(f"Error get_total_pages(). Exception: {e}")
        return 0




def scrape_all_pages(base_url, page_template, output_dir, main_pickle_file, new_pickle_file):
    """Scrape multiple pages and consolidate the data, starting with a new 'new_properties.pkl'."""
    os.makedirs(output_dir, exist_ok=True)

    driver = cscrap.initialize_driver()
    try:
        total_items = get_total_pages(driver, base_url, output_dir)
        logger.info(f'Total Properties: {total_items}')
        total_pages = total_items
        for page in range(total_pages):
            url = base_url if page == 0 else page_template.format(page=page)
            html_file = os.path.join(output_dir, f"page_{page + 1}.html")
            logger.info('-'*100)
            logger.info(f"Scraping page {page + 1}/{total_pages}...")
            process_page(driver, url, html_file, main_pickle_file, new_pickle_file)
    except Exception as e:
        logger.error(f'Excepcion: {e}')
    finally:
        driver.quit()



def scrap(folder_name):
    properties_path = 'results/properties.pkl'
    new_properties_path = 'results/new_properties.pkl'
    
    # Define the areas and propiedades to iterate over
    areas = [3, 4, 5]
    propiedades = [2, 6]

    # Loop through all combinations of areas and propiedades
    for area in areas:
        for propiedad in propiedades:
            first_page_url = f"https://www.inmocasal.es/busqueda-avanzada/?gestion=comprar&propiedad={propiedad}&area={area}&precioMin=0&precioMax=75000&ordenar=1&pagina=1"
            page_url_template = f"https://www.inmocasal.es/busqueda-avanzada/?gestion=comprar&propiedad={propiedad}&area={area}&precioMin=0&precioMax=75000&ordenar=1&pagina={{page}}"

            # Call the scraping function for each combination
            scrape_all_pages(
                base_url=first_page_url,
                page_template=page_url_template,
                output_dir=folder_name,
                main_pickle_file=properties_path,
                new_pickle_file=new_properties_path,
            )


# def scrap(folder_name):
#     properties_path = 'results/properties.pkl'
#     new_properties_path = 'results/new_properties.pkl'
#     # ----------------------- SCRAPPING ------------------------------------ 

#     # ------------- PROPIEDAD 6 (PISOS) AREA 5 (Área de La Felguera, Sama y Laviana) -------------
#     propiedad = 6
#     area = 5
#     first_page_url = f"https://www.inmocasal.es/busqueda-avanzada/?gestion=comprar&propiedad={propiedad}&area={area}&precioMax=75000&ordenar=1&pagina=1"
#     page_url_template = f"https://www.inmocasal.es/busqueda-avanzada/?gestion=comprar&propiedad={propiedad}&area={area}&precioMax=75000&ordenar=1&pagina="
#     page_url_template += "{page}"

#     scrape_all_pages(
#         base_url=first_page_url,
#         page_template=page_url_template,
#         output_dir=folder_name,
#         main_pickle_file=properties_path,
#         new_pickle_file=new_properties_path,
#     )
    