import requests
import random 
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains  # Added this line
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import re
import time
from extract_sheets import extract_data_from_excel
import logging
import argparse
import pandas as pd
from fake_useragent import UserAgent

def generate_random_fingerprint():
    # Random screen resolutions
    resolutions = [
        (1920, 1080), (1366, 768), (1536, 864), 
        (1440, 900), (1280, 720), (1600, 900)
    ]
    
    # Random color depths
    color_depths = [24, 32]
    
    # Random platforms
    platforms = ['Windows', 'Linux', 'MacIntel']
    
    # Random hardware concurrency (CPU cores)
    hw_concurrency = [2, 4, 6, 8, 12, 16]
    
    # Random device memory (GB)
    device_memory = [2, 4, 8, 16]
    
    return {
        'resolution': random.choice(resolutions),
        'color_depth': random.choice(color_depths),
        'platform': random.choice(platforms),
        'hardware_concurrency': random.choice(hw_concurrency),
        'device_memory': random.choice(device_memory)
    }

def add_random_behaviors(driver):
    """Add random canvas noise and other browser behaviors"""
    # Randomize canvas fingerprint
    canvas_noise = """
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    
    HTMLCanvasElement.prototype.toDataURL = function(type) {
        const canvas = document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(this, 0, 0);
        
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const pixels = imageData.data;
        
        // Add subtle random noise to pixels
        for(let i = 0; i < pixels.length; i += 4) {
            pixels[i] += Math.floor(Math.random() * 2);     // Red
            pixels[i+1] += Math.floor(Math.random() * 2);   // Green
            pixels[i+2] += Math.floor(Math.random() * 2);   // Blue
        }
        
        ctx.putImageData(imageData, 0, 0);
        return originalToDataURL.apply(canvas, arguments);
    };
    
    CanvasRenderingContext2D.prototype.getImageData = function() {
        const imageData = originalGetImageData.apply(this, arguments);
        const pixels = imageData.data;
        
        // Add subtle random noise
        for(let i = 0; i < pixels.length; i += 4) {
            pixels[i] += Math.floor(Math.random() * 2);
            pixels[i+1] += Math.floor(Math.random() * 2);
            pixels[i+2] += Math.floor(Math.random() * 2);
        }
        
        return imageData;
    };
    """
    driver.execute_script(canvas_noise)

def random_mouse_movement(driver):
    """Perform random mouse movements"""
    action = ActionChains(driver)
    
    # Get window size
    window_size = driver.get_window_size()
    width = window_size['width']
    height = window_size['height']
    
    # Generate random points for mouse movement
    points = [(random.randint(0, width), random.randint(0, height)) 
             for _ in range(random.randint(3, 7))]
    
    # Perform random movements
    current_x = current_y = 0
    for x, y in points:
        # Calculate intermediate points for more natural movement
        steps = random.randint(2, 5)
        for i in range(steps):
            intermediate_x = current_x + (x - current_x) * (i + 1) / steps
            intermediate_y = current_y + (y - current_y) * (i + 1) / steps
            action.move_by_offset(intermediate_x - current_x, intermediate_y - current_y)
            action.pause(random.uniform(0.1, 0.3))
            current_x, current_y = intermediate_x, intermediate_y
    
    action.perform()
    time.sleep(random.uniform(0.5, 1))

def human_like_click(driver, element):
    """Perform a more human-like click with slight offset and random timing"""
    try:
        # Get element size and location
        size = element.size
        location = element.location
        
        # Calculate random offset within element
        offset_x = random.randint(5, max(6, size['width'] - 5))
        offset_y = random.randint(5, max(6, size['height'] - 5))
        
        # Create action chain for the click
        action = ActionChains(driver)
        action.move_to_element_with_offset(element, offset_x, offset_y)
        action.pause(random.uniform(0.1, 0.3))
        action.click()
        action.perform()
        
        # Random pause after click
        time.sleep(random.uniform(0.5, 1.5))
    except Exception as e:
        logging.warning(f"Failed to perform human-like click: {str(e)}")
        # Fallback to regular click
        element.click()
        time.sleep(random.uniform(0.5, 1.5))

def random_scroll(driver):
    """Perform random scrolling behavior"""
    try:
        # Get page height
        page_height = driver.execute_script("return document.body.scrollHeight")
        viewport_height = driver.execute_script("return window.innerHeight")
        
        if page_height > viewport_height:
            # Random number of scroll actions
            for _ in range(random.randint(2, 4)):
                # Random scroll position
                scroll_to = random.randint(0, page_height - viewport_height)
                
                # Smooth scroll with random speed
                driver.execute_script(f"""
                    window.scrollTo({{
                        top: {scroll_to},
                        behavior: 'smooth'
                    }});
                """)
                time.sleep(random.uniform(0.5, 1.5))
    except Exception as e:
        logging.warning(f"Failed to perform random scroll: {str(e)}")

def random_page_interaction(driver):
    """Perform random page interactions"""
    try:
        # Random text selection
        driver.execute_script("""
        function getRandomText() {
            var texts = [];
            var walker = document.createTreeWalker(
                document.body, 
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            var node;
            while(node = walker.nextNode()) {
                if(node.textContent.trim().length > 20) {
                    texts.push(node);
                }
            }
            if(texts.length > 0) {
                return texts[Math.floor(Math.random() * texts.length)];
            }
            return null;
        }
        
        var textNode = getRandomText();
        if(textNode) {
            var range = document.createRange();
            range.setStart(textNode, 0);
            range.setEnd(textNode, Math.floor(textNode.length / 2));
            var sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
        }
        """)
        time.sleep(random.uniform(0.3, 0.7))
        
        # Clear selection
        driver.execute_script("window.getSelection().removeAllRanges();")
    except Exception as e:
        logging.warning(f"Failed to perform random page interaction: {str(e)}")

def download_pdf_from_s3(url, company_name, id, last_name, file_num, year, output_directory="downloads", max_retries=5, initial_delay=1):
    try:
        # Ensure output directory exists
        last_name = last_name.split(",")[0]
        
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        filename = f"{company_name}_{id}_{last_name}_{file_num}_{year}.pdf"
        output_path = os.path.join(output_directory, filename)

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6639.39 Safari/537.36",
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
    
    # Generate random fingerprint
    fingerprint = {
        'resolution': random.choice([(1920, 1080), (1366, 768), (1536, 864), (1440, 900)]),
        'color_depth': random.choice([24, 32]),
        'platform': random.choice(['Windows', 'Linux', 'MacIntel']),
        'hardware_concurrency': random.choice([2, 4, 6, 8, 12]),
        'device_memory': random.choice([2, 4, 8, 16])
    }
    
    # Basic Chrome settings
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument(f'--window-size={fingerprint["resolution"][0]},{fingerprint["resolution"][1]}')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    
    # Open DevTools
    chrome_options.add_argument('--auto-open-devtools-for-tabs')
    
    # Add random user agent
    ua = UserAgent()
    chrome_options.add_argument(f'--user-agent={ua.random}')
    
    # Add experimental options
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    return chrome_options, fingerprint

def inject_random_fingerprint(driver, fingerprint):
    # JavaScript code to override navigator properties
    js_code = """
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => %d
    });
    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => %d
    });
    Object.defineProperty(navigator, 'platform', {
        get: () => '%s'
    });
    Object.defineProperty(screen, 'colorDepth', {
        get: () => %d
    });
    """ % (
        fingerprint['hardware_concurrency'],
        fingerprint['device_memory'],
        fingerprint['platform'],
        fingerprint['color_depth']
    )
    
    # Execute the JavaScript code
    driver.execute_script(js_code)
    
    # Set additional headers using CDP
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
        'headers': {
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9',
                'fr-FR,fr;q=0.9',
                'de-DE,de;q=0.9',
                'es-ES,es;q=0.9'
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'DNT': random.choice(['0', '1'])
        }
    })
    
    # Randomize WebGL fingerprint
    webgl_vendor_override = """
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Open Source Technology Center';
        }
        if (parameter === 37446) {
            return 'Mesa DRI Intel(R) HD Graphics (SSH)';
        }
        return getParameter.apply(this, arguments);
    };
    """
    driver.execute_script(webgl_vendor_override)

def extract_report_ids(firstname, lastname, contributor_name, retry_count=1):
    driver = None
    try:
        if retry_count % 5 == 0:
            time.sleep(120)

        logging.info(f"Starting attempt {retry_count} for {firstname} {lastname}")
        
        # Get both chrome_options and fingerprint
        chrome_options, fingerprint = setup_chrome_options()
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Enable network tracking
            driver.execute_cdp_cmd('Network.enable', {})
            
            # Inject fingerprint randomization
            inject_fingerprint_js = f"""
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {fingerprint['hardware_concurrency']}
            }});
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {fingerprint['device_memory']}
            }});
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{fingerprint['platform']}'
            }});
            Object.defineProperty(screen, 'colorDepth', {{
                get: () => {fingerprint['color_depth']}
            }});
            """
            driver.execute_script(inject_fingerprint_js)
            
            # Add random behaviors
            add_random_behaviors(driver)
            
            # Hide webdriver
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            
        except Exception as e:
            logging.error(f"Failed to create Chrome driver: {str(e)}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            return [], []
        
        if not driver:
            logging.error("Failed to initialize Chrome driver")
            return [], []
        
        # Add random delays between actions
        time.sleep(random.uniform(1, 3))
        
        driver.get("https://www.mergentonline.com/investextfullsearch.php")
        random_mouse_movement(driver)
        random_scroll(driver)
        
        time.sleep(random.uniform(2, 4))
        
        wait = WebDriverWait(driver, 15)
        
        try:
            # Set date range
            custom_date_radio = wait.until(EC.element_to_be_clickable((By.ID, "customDateChkb")))
            human_like_click(driver, custom_date_radio)
            time.sleep(random.uniform(0.5, 1.5))
            
            driver.execute_script("document.getElementById('textInRangeFrom').value='01/01/1999'")
            driver.execute_script("document.getElementById('textInRangeTo').value='12/31/2022'")
            random_page_interaction(driver)
            
            # Add criteria in sequence
            for criteria_num in [5, 11, 8, 9]:
                driver.execute_script(f"addCriteria(1, {criteria_num})")
                time.sleep(random.uniform(0.8, 1.5))
                random_mouse_movement(driver)
                
                if criteria_num == 5:
                    # Handle Report Style criteria
                    lookup_link = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Use REPORTSTYLE Lookup')]"))
                    )
                    main_window = driver.current_window_handle
                    human_like_click(driver, lookup_link)
                    time.sleep(random.uniform(0.8, 1.5))
                    
                    wait_for_popup(driver, main_window, wait)
                    popup_window = [w for w in driver.window_handles if w != main_window][0]
                    driver.switch_to.window(popup_window)
                    
                    equity_checkbox = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='checkbox' and contains(@value, '150000018-EQUITY')]"))
                    )
                    human_like_click(driver, equity_checkbox)
                    
                    driver.close()
                    driver.switch_to.window(main_window)
                    random_page_interaction(driver)
                
                elif criteria_num == 8:
                    # Handle Contributor criteria
                    handle_contributor_criteria(driver, wait, contributor_name)
                    random_mouse_movement(driver)
                
                elif criteria_num == 9:
                    # Handle Author criteria
                    lastname_input = wait.until(
                        EC.presence_of_element_located((By.NAME, "lastname3"))
                    )
                    lastname_input.clear()
                    lastname_input.send_keys(lastname)
                    
                    driver.execute_script("setAuthorName(3)")
                    time.sleep(random.uniform(0.8, 1.5))
                    random_page_interaction(driver)

            print(f"Attempt {retry_count} to get matches...")
            submit_button = wait.until(
                EC.element_to_be_clickable((By.ID, "submitbtn3"))
            )
            random_mouse_movement(driver)
            human_like_click(driver, submit_button)

            return handle_results(driver, wait, retry_count, firstname, lastname, contributor_name)
                    
        except TimeoutException as te:
            logging.error(f"Timeout occurred: {str(te)}")
            return retry_or_return(driver, retry_count, firstname, lastname, contributor_name)
        
        except Exception as e:
            logging.error(f"Error during execution: {str(e)}")
            return [], []

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return [], []
        
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logging.error(f"Error while quitting driver: {str(e)}")

def wait_for_popup(driver, main_window, wait):
    """Wait for popup window to appear and return its handle"""
    for _ in range(10):  # Try for 10 times
        if len(driver.window_handles) > 1:
            return
        time.sleep(0.5)
    raise TimeoutException("Popup window did not appear")

def handle_contributor_criteria(driver, wait, contributor_name):
    """Handle the contributor criteria section"""
    main_window = driver.current_window_handle
    lookup_link = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Use CONTRIBUTOR Lookup')]"))
    )
    driver.execute_script("arguments[0].click();", lookup_link)
    time.sleep(random.uniform(0.8, 1.5))
    
    wait_for_popup(driver, main_window, wait)
    popup_window = [w for w in driver.window_handles if w != main_window][0]
    driver.switch_to.window(popup_window)
    
    search_form = wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
    search_box = search_form.find_element(By.NAME, "lookupsearch")
    search_box.send_keys(contributor_name)
    search_form.submit()
    time.sleep(random.uniform(0.8, 1.5))
    
    first_result = wait.until(
        EC.presence_of_element_located((By.XPATH, "//table[contains(@style, 'width:100%')]//tr[2]//input[@type='checkbox']"))
    )
    driver.execute_script("arguments[0].click();", first_result)
    
    driver.close()
    driver.switch_to.window(main_window)

def handle_author_criteria(driver, wait, firstname, lastname):
    """Handle the author criteria section"""
    lastname_input = wait.until(EC.presence_of_element_located((By.NAME, "lastname3")))
    lastname_input.clear()
    lastname_input.send_keys(lastname)
    
    driver.execute_script("setAuthorName(3)")
    time.sleep(random.uniform(0.8, 1.5))

def handle_results(driver, wait, retry_count, firstname, lastname, contributor_name):
    """Handle the results page and extraction"""
    try:
        match_element = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "//td[@class='match']//div[@id='matched3' and contains(text(), 'Matches')]"))
        )
        
        view_link = driver.find_element(By.XPATH, "//a[@class='view' and @onclick='selectView(3)']")
        view_link.click()

        wait.until(EC.title_contains("Mergent Online"))
        
        table_ids = []
        table_years = []
        
        while True:
            html_content = driver.page_source
            ids, years = extract_table_ids(html_content)
            table_ids.extend(ids)
            table_years.extend(years)
            
            next_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Next')]")
            if not next_links:
                break
                
            next_links[0].click()
            time.sleep(random.uniform(1.5, 2.5))
            
        return table_ids, table_years
            
    except TimeoutException:
        return retry_or_return(driver, retry_count, firstname, lastname, contributor_name)

def retry_or_return(driver, retry_count, firstname, lastname, contributor_name):
    """Handle retry logic when encounters timeout or NA"""
    try:
        na_element = driver.find_element(By.XPATH, "//td[@class='match']//div[@id='matched3' and contains(text(), 'N/A')]")
        logging.info(f"Got N/A response on attempt {retry_count}, restarting process...")
        return extract_report_ids(firstname, lastname, contributor_name, retry_count + 1)
    except NoSuchElementException:
        logging.error("Unable to find match count or N/A")
        return [], []

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