import os
import math
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager


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


def save_html(driver, url, output_file):
    """Save the HTML content of a URL to a local file."""
    if os.path.exists(output_file):
        print(f"Skipping download: {output_file} already exists.")
        return

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mh-estate-vertical__primary"))
        )
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(driver.page_source)
        print(f"HTML saved to {output_file}.")
    except Exception as e:
        print(f"Error accessing {url}: {e}")


def load_or_initialize_pickle(file_path, columns):
    """Load existing pickle file or initialize a new DataFrame."""
    if os.path.exists(file_path):
        return pd.read_pickle(file_path)
    return pd.DataFrame(columns=columns)


def save_to_pickle(dataframe, file_path):
    """Save a DataFrame to a pickle file."""
    dataframe.to_pickle(file_path)


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
                    print(f"Skipping div with no data: {div}")

            except Exception as e:
                print(f"Error processing div {div}: {e}")

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
                print(f"Error processing article {article}: {e}")

        # Step 3: Merge DIV and Article Data
        final_data = []
        for idx, item in enumerate(div_data):
            ref = item.get("ref")
            price = item.get("price")

            # Get the corresponding URL from article_data_list by index
            property_url = article_data_list[idx] if idx < len(article_data_list) else None

            if ref and property_url:
                final_data.append({"ref": ref, "price": price, "url": property_url})
            else:
                print(f"Skipping item due to missing URL: ref={ref}, price={price}")

        return pd.DataFrame(final_data)

    except Exception as e:
        print(f"Error parsing HTML file {html_file}: {e}")
        return pd.DataFrame()








def merge_dataframes(existing_df, new_df):
    """Merge existing DataFrame with new data, avoiding duplicates."""
    combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset="ref", keep="last").reset_index(drop=True)
    return combined_df


def process_page(driver, url, html_file, pickle_file, new_pickle_file):
    """Process a single page and update the main and new properties pickle files."""
    save_html(driver, url, html_file)
    extracted_data = extract_data_from_html(html_file)

    # Load existing data
    existing_data = load_or_initialize_pickle(pickle_file, ["ref", "price", "url"])

    # Identify new properties
    new_properties = extracted_data[~extracted_data["ref"].isin(existing_data["ref"])]
    
    # Update the main dataset
    updated_data = merge_dataframes(existing_data, extracted_data)
    save_to_pickle(updated_data, pickle_file)

    # Save new properties to separate pickle
    if not new_properties.empty:
        existing_new_properties = load_or_initialize_pickle(new_pickle_file, ["ref", "price", "url"])
        combined_new_properties = merge_dataframes(existing_new_properties, new_properties)
        save_to_pickle(combined_new_properties, new_pickle_file)

    print(f"Number of items: {len(updated_data)}")

    return updated_data, new_properties


def get_total_items(driver, url, output_dir):
    html_file = os.path.join(output_dir, f"page_1.html")
    save_html(driver, url, html_file)

    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        elements = soup.select("li.mh-search__results")
        for element in elements:
            total_items = int(element.string.strip().split()[0])
            break

        return total_items
    except Exception as e:
        print(f"Error get_total_items(). Exception: {e}")
        return 0



def scrape_all_pages(base_url, page_template, output_dir, main_pickle_file, new_pickle_file, items_per_page):
    """Scrape multiple pages and consolidate the data, starting with a new 'new_properties.pkl'."""
    os.makedirs(output_dir, exist_ok=True)

    # Initialize the 'new_properties.pkl' as an empty DataFrame
    empty_df = pd.DataFrame(columns=["ref", "price", "url"])
    save_to_pickle(empty_df, new_pickle_file)
    print(f"Initialized a fresh new_properties file at {new_pickle_file}.")

    driver = initialize_driver()
    try:
        total_items = get_total_items(driver, base_url, output_dir)
        print(f'Total Properties: {total_items}')
        total_pages = math.ceil(total_items / items_per_page)
        for page in range(total_pages):
            url = base_url if page == 0 else page_template.format(page=page)
            html_file = os.path.join(output_dir, f"page_{page + 1}.html")
            print('-'*100)
            print(f"Scraping page {page + 1}/{total_pages}...")
            process_page(driver, url, html_file, main_pickle_file, new_pickle_file)
    except Exception as e:
        print(f'Excepcion: {e}')
    finally:
        driver.quit()




def scrap_axius():
    output_directory = "axius"
    main_pickle_file_path = os.path.join(output_directory, "properties.pkl")
    new_pickle_file_path = os.path.join(output_directory, "new_properties.pkl")
    first_page_url = "https://arxus.es/propiedades/?TipoOperacion=Venta&Precio2=50000"
    page_url_template = "https://arxus.es/propiedades/?TipoOperacion=Venta&Precio2=50000&pagina={page}"
    items_per_page = 12

    scrape_all_pages(
        base_url=first_page_url,
        page_template=page_url_template,
        output_dir=output_directory,
        main_pickle_file=main_pickle_file_path,
        new_pickle_file=new_pickle_file_path,
        items_per_page=items_per_page,
    )