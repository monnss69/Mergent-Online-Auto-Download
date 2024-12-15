import requests
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import re
import time
from extract_sheets import extract_data_from_excel
import logging
import argparse
import pandas as pd

def download_pdf_from_s3(url, company_name, id, last_name, file_num, year, output_directory="downloads", max_retries=5, initial_delay=1):
    try:
        # Ensure output directory exists
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        filename = f"{company_name}_{id}_{last_name}_{file_num}_{year}.pdf"
        output_path = os.path.join(output_directory, filename)
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
            "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.mergentonline.com",  # Update this as per the originating site
        })
        current_retry = 0
        while current_retry < max_retries:
            try:
                print(f"Attempt {current_retry + 1}/{max_retries} - Downloading: {url}")
                response = session.get(url, allow_redirects=True, stream=True)
                response.raise_for_status()
                # Handle meta-refresh redirects
                if "text/html" in response.headers.get("content-type", ""):
                    soup = BeautifulSoup(response.text, "html.parser")
                    meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
                    if meta_refresh and "url=" in meta_refresh["content"]:
                        redirect_url = meta_refresh["content"].split("url=")[-1]
                        print(f"Redirecting to: {redirect_url}")
                        url = redirect_url  # Update URL and retry
                        continue
                # Verify PDF content
                if "application/pdf" not in response.headers.get("content-type", ""):
                    print("Content is not a PDF, retrying...")
                    current_retry += 1
                    time.sleep(initial_delay + current_retry)
                    continue
                # Save the PDF
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Successfully downloaded PDF to: {output_path}")
                return output_path
            except requests.exceptions.RequestException as e:
                current_retry += 1
                delay = initial_delay * (2 ** (current_retry - 1))
                print(f"Retry {current_retry}/{max_retries} after {delay}s due to: {e}")
                time.sleep(delay)
        print(f"Failed to download PDF after {max_retries} attempts.")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None
def openfile(fileId, company_name, id, last_name, year, num):
    if not fileId:
        print("No files to download")
        return
    
    url = 'https://www.mergentonline.com/investextsearchlive.php?opt=loadDocument&docid=%5B%22'
    doctype = 'pdf'
    file_url = f"{url}{fileId}%22%5D&doctype={doctype}"
    
    output_directory = f"{company_name}_{id}_{last_name}"
    max_retries = 5
    initial_delay = 1
    
    download_pdf_from_s3(file_url, company_name, id, last_name, num, year, output_directory, max_retries, initial_delay)
def extract_table_ids(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', class_='tablesorter bodyline')
        
        if not table or not (tbody := table.find('tbody')):
            raise ValueError("Table or tbody not found in HTML content")
            
        ids = []
        years = []
        
        for row in tbody.find_all('tr', id=re.compile('^key_')):
            if id_match := re.search(r'key_(\d+)', row['id']):
                # Extract ID
                ids.append(id_match.group(1))
                
                # Extract date and year
                date_cell = row.find_all('td')[2]  # Third td contains the date
                date_text = date_cell.text.strip()
                year = date_text.split('/')[-1]  # Get the year from date format MM/DD/YYYY
                years.append(year)
        
        return ids, years
        
    except Exception as e:
        print(f"Error processing HTML: {str(e)}")
        return [], []
def setup_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--window-size=1920,1080')  # Set a specific window size
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')  # Disable compositor
    chrome_options.add_argument('--force-device-scale-factor=1')
    return chrome_options

def extract_report_ids(firstname, lastname, contributor_name, retry_count=1):

    if retry_count%5 == 0:
        time.sleep(120)

    driver = None
    try:
        logging.info(f"Starting attempt {retry_count} for {firstname} {lastname}")
        chrome_options = setup_chrome_options()
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Failed to create Chrome driver: {str(e)}")
            return [], []
            
        if not driver:
            print("Failed to initialize Chrome driver")
            return [], []
        
        driver.get("https://www.mergentonline.com/investextfullsearch.php")
        wait = WebDriverWait(driver, 15)
        time.sleep(1)
        
        # Set date range
        custom_date_radio = wait.until(EC.element_to_be_clickable((By.ID, "customDateChkb")))
        driver.execute_script("arguments[0].click();", custom_date_radio)
        driver.execute_script("document.getElementById('textInRangeFrom').value='01/01/1999'")
        driver.execute_script("document.getElementById('textInRangeTo').value='12/31/2022'")
        time.sleep(1)
        
        # Add criteria in sequence
        for criteria_num in [5, 11, 8, 9]:
            driver.execute_script(f"addCriteria(1, {criteria_num})")
            time.sleep(1)
            
            # Handle Report Style criteria
            if criteria_num == 5:
                lookup_link = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Use REPORTSTYLE Lookup')]"))
                )
                main_window = driver.current_window_handle
                driver.execute_script("arguments[0].click();", lookup_link)
                time.sleep(1)
                
                popup_window = None
                for window_handle in driver.window_handles:
                    if window_handle != main_window:
                        popup_window = window_handle
                        driver.switch_to.window(popup_window)
                        break
                
                equity_checkbox = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox' and contains(@value, '150000018-EQUITY')]"))
                )
                driver.execute_script("arguments[0].click();", equity_checkbox)
                
                driver.close()
                driver.switch_to.window(main_window)
            
            # Handle Contributor criteria
            elif criteria_num == 8:
                lookup_link = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Use CONTRIBUTOR Lookup')]"))
                )
                main_window = driver.current_window_handle
                driver.execute_script("arguments[0].click();", lookup_link)
                time.sleep(1)
                
                popup_window = None
                for window_handle in driver.window_handles:
                    if window_handle != main_window:
                        popup_window = window_handle
                        driver.switch_to.window(popup_window)
                        break
                
                # Find and use the search form
                search_form = wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
                search_box = search_form.find_element(By.NAME, "lookupsearch")
                search_box.send_keys(contributor_name)
                search_form.submit()
                time.sleep(1)
                
                # Wait for and select the first result
                first_result = wait.until(
                    EC.presence_of_element_located((By.XPATH, 
                        "//table[contains(@style, 'width:100%')]//tr[2]//input[@type='checkbox']"
                    ))
                )
                driver.execute_script("arguments[0].click();", first_result)
                
                driver.close()
                driver.switch_to.window(main_window)
                
            # Handle Author criteria
            elif criteria_num == 9:
                # Wait for first name input field and enter "John"
                firstname_input = wait.until(
                    EC.presence_of_element_located((By.NAME, "firstname3"))
                )
                firstname_input.clear()
                firstname_input.send_keys(firstname)
                
                # Find last name input field and enter "Grassano"
                lastname_input = wait.until(
                    EC.presence_of_element_located((By.NAME, "lastname3"))
                )
                lastname_input.clear()
                lastname_input.send_keys(lastname)
                
                # Trigger the setAuthorName JavaScript function
                driver.execute_script("setAuthorName(3)")
                time.sleep(1)
        table_ids = []
        table_years = []
        print(f"Attempt {retry_count} to get matches...")
        submit_button = wait.until(
            EC.element_to_be_clickable((By.ID, "submitbtn3"))
        )
        submit_button.click()
        try:
            match_element = WebDriverWait(driver, 100).until(
                EC.presence_of_element_located((By.XPATH, "//td[@class='match']//div[@id='matched3' and contains(text(), 'Matches')]"))
            )
            
            view_link = driver.find_element(By.XPATH, "//a[@class='view' and @onclick='selectView(3)']")
            view_link.click()
            wait.until(EC.title_contains("Mergent Online"))
            
            html_content = driver.page_source
            ids, years = extract_table_ids(html_content)
            table_ids = []
            table_years = []
            table_ids.extend(ids)
            table_years.extend(years)
            
            next_link = driver.find_elements(By.XPATH, "//a[contains(text(), 'Next')]")
            while next_link:
                next_link[0].click()
                next_link = driver.find_elements(By.XPATH, "//a[contains(text(), 'Next')]")
                html_content = driver.page_source
                ids, years = extract_table_ids(html_content)
                table_ids.extend(ids)
                table_years.extend(years)
                time.sleep(2)
                
            return table_ids, table_years
                
        except TimeoutException:
            try:
                na_element = driver.find_element(By.XPATH, "//td[@class='match']//div[@id='matched3' and contains(text(), 'N/A')]")
                print(f"Got N/A response on attempt {retry_count}, restarting process...")
                driver.quit()
                time.sleep(2)
                return extract_report_ids(firstname, lastname, contributor_name, retry_count + 1)
            except NoSuchElementException:
                raise Exception("Unable to find match count or N/A")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return [], []
    
    finally:
        driver.quit()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )
def main():
    setup_logging()
    logging.info("Starting scraper")

    file_path = "broker_analyst_2_1.xlsx"
    try:
        last_name, first_name, analys_id, IBES_id, company = extract_data_from_excel(file_path)
        logging.info(f"Successfully read {len(first_name)} analysts from Excel")

        for i in range(len(last_name)):
            logging.info(f"Processing analyst {i+1}/{len(last_name)}: {first_name[i]} {last_name[i]}")
            ids, years = extract_report_ids(first_name[i], last_name[i], company[i])

            if not ids:
                logging.warning(f"No reports found for {first_name[i]} {last_name[i]}")
                continue

            logging.info(f"Found {len(ids)} reports for {first_name[i]} {last_name[i]}")
            for j in range(len(ids)):
                openfile(ids[j], IBES_id[i], analys_id[i], last_name[i], years[j], len(ids) - j)

    except Exception as e:
        logging.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()