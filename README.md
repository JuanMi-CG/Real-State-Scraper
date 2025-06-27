# Real State Scraper

A Python scraper that collects property listings from two sites—Axius and Inmocasal—and emails new results.

---

## Features

- Headless Chrome (Selenium) scraping with automatic driver management  
- Incremental detection of new listings  
- Persistent storage using Pickle  
- Email notifications (HTML table) for new properties and periodic health updates  
- Configurable via environment variables  

---

## Requirements

- Python 3.10+  
- Chrome or Chromium browser installed  

The project uses:
```text
selenium==4.27.1
webdriver-manager==4.0.2
beautifulsoup4==4.12.3
pandas==2.2.3
boto3==1.35.74  # (optional, currently unused)
python-dotenv     # for local .env support
