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

def download_pdf_from_s3(url, output_directory="downloads", max_retries=5, initial_delay=1):
    try:
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        output_path = os.path.join(output_directory, 'downloaded_document.pdf')
        
        current_retry = 0
        while current_retry <= max_retries:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                if 'application/pdf' not in response.headers.get('content-type', '').lower():
                    raise RequestException("Response does not contain PDF content")
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"Successfully downloaded PDF to: {output_path}")
                return output_path
                
            except RequestException as e:
                current_retry += 1
                if current_retry > max_retries:
                    print(f"Maximum retries ({max_retries}) exceeded. Final error: {e}")
                    return None
                    
                delay = initial_delay * (2 ** (current_retry - 1))
                print(f"Attempt {current_retry}/{max_retries} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
                
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def openfile(fileIdList):
    if not fileIdList:
        print("No files to download")
        return
    
    for fileId in fileIdList:
        url = 'https://www.mergentonline.com/investextsearchlive.php?opt=loadDocument&docid='
        doctype = 'pdf'
        file_url = f"{url}{fileId}&doctype={doctype}"
        
        output_directory = "downloads"
        max_retries = 5
        initial_delay = 1
        
        download_pdf_from_s3(file_url, output_directory, max_retries, initial_delay)

def extract_table_ids(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', class_='tablesorter bodyline')
        
        if not table or not (tbody := table.find('tbody')):
            raise ValueError("Table or tbody not found in HTML content")
            
        ids = []
        for row in tbody.find_all('tr', id=re.compile('^key_')):
            if id_match := re.search(r'key_(\d+)', row['id']):
                ids.append(id_match.group(1))
        
        return ids
        
    except Exception as e:
        print(f"Error processing HTML: {str(e)}")
        return []

def set_search_criteria(firstname, lastname, contributor_name):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)
        
        driver.get("https://www.mergentonline.com/investextfullsearch.php")
        time.sleep(2)
        
        # Set date range
        custom_date_radio = wait.until(EC.element_to_be_clickable((By.ID, "customDateChkb")))
        driver.execute_script("arguments[0].click();", custom_date_radio)
        driver.execute_script("document.getElementById('textInRangeFrom').value='01/01/1999'")
        driver.execute_script("document.getElementById('textInRangeTo').value='12/31/2023'")
        time.sleep(2)
        
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
                time.sleep(2)
                
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
                time.sleep(2)
                
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
                time.sleep(2)
                
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
        while True:
            # Click submit on the last criteria (Author)
            submit_button = wait.until(
                EC.element_to_be_clickable((By.ID, "submitbtn3"))
            )
            submit_button.click()

            try:
                # Wait for match element to appear
                match_element = WebDriverWait(driver, 35).until(
                    EC.presence_of_element_located((By.XPATH, "//td[@class='match']//div[@id='matched3' and contains(text(), 'Matches')]"))
                )
                # Click on the View link
                view_link = driver.find_element(By.XPATH, "//a[@class='view' and @onclick='selectView(3)']")
                view_link.click()

                # Wait for result page to load 
                wait.until(EC.title_contains("Mergent Online"))
                
                # Append current page HTML to the list
                html_content = driver.page_source
                ids = extract_table_ids(html_content)
                table_ids.extend(ids)
                
                # Check if there is a next page link
                next_link = driver.find_elements(By.XPATH, "//a[contains(text(), 'Next')]")
                while next_link:
                    next_link[0].click()
                    next_link = driver.find_elements(By.XPATH, "//a[contains(text(), 'Next')]")
                    html_content = driver.page_source
                    ids = extract_table_ids(html_content)
                    table_ids.extend(ids)
                    time.sleep(2)
                    
            except TimeoutException:
                # Check if "N/A" is present
                try:
                    na_element = driver.find_element(By.XPATH, "//td[@class='match']//div[@id='matched3' and contains(text(), 'N/A')]")
                    # If "N/A" is found, continue the loop to resubmit
                    continue
                except NoSuchElementException:
                    # If neither match count nor "N/A" is found, raise an exception
                    raise Exception("Unable to find match count or N/A")

            return table_ids
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        driver.quit()

def main():
    ids = set_search_criteria()
    for i, id in enumerate(ids):
        print(i, id)

if __name__ == "__main__":
    main()