import concurrent.futures
import os
import pandas as pd
from datetime import datetime
import logging
import scraper as scraper
from scraper import extract_report_ids, openfile
import extract_sheets
from extract_sheets import extract_data_from_excel

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )

def process_analyst(analyst_data):
    first_name, last_name, analys_id, IBES_id, company = analyst_data
    logging.info(f"Processing analyst: {first_name} {last_name}")
    
    try:
        ids, years = extract_report_ids(first_name, last_name, company)
        if not ids:
            logging.warning(f"No reports found for {first_name} {last_name}")
            return
            
        for j in range(len(ids)):
            openfile(ids[j], IBES_id, analys_id, last_name, years[j], len(ids) - j)
            
    except Exception as e:
        logging.error(f"Error processing {first_name} {last_name}: {str(e)}")

def parallel_process(file_path, max_workers=None):
    setup_logging()
    
    # Extract data from Excel
    last_name, first_name, analys_id, IBES_id, company = extract_data_from_excel(file_path)
    
    # Create list of analyst data tuples
    analyst_data = list(zip(first_name, last_name, analys_id, IBES_id, company))

    if max_workers is None:
        max_workers = min(1, (os.cpu_count() or 1) * 4)
    
    # Process analysts in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_analyst, data) for data in analyst_data]
        concurrent.futures.wait(futures)
        
    logging.info("All processing completed")

if __name__ == "__main__":
    file_path = "broker_analyst_2_1.xlsx"
    parallel_process(file_path)  # Adjust max_workers as needed