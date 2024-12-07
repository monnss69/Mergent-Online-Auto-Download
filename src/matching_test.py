import pandas as pd
import numpy as np
import scraper as scraper
from scraper import extract_report_ids
from extract_sheets import extract_data
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

# First, let's create a function that processes a single author
def process_single_author(author_data: Tuple[str, str, str, int], author_index: int, total_authors: int) -> Tuple[bool, str, str]:
    """
    Process a single author and compare their scraped report count with expected count.
    
    Args:
        author_data: Tuple containing (first_name, last_name, company, expected_report_count)
        author_index: Current author's index for logging
        total_authors: Total number of authors for logging
    
    Returns:
        Tuple containing:
        - Boolean indicating if there's a mismatch
        - Author's full name
        - Error message if there's a mismatch, empty string otherwise
    """
    first_name, last_name, company, expected_count = author_data
    full_name = f"{first_name} {last_name}"
    
    logging.info(f"Processing analyst {author_index}/{total_authors}: {full_name}")
    
    # Get report IDs from scraper
    ids, years = extract_report_ids(first_name, last_name, company)
    
    if not ids:
        logging.warning(f"No reports found for {full_name}")
        return True, full_name, f"No reports found for {full_name} (expected {expected_count})"
        
    if expected_count != len(ids):
        logging.warning(f"Number mismatch for {full_name}: expected {expected_count}, found {len(ids)}")
        return True, full_name, f"Report count mismatch for {full_name}: expected {expected_count}, found {len(ids)}"
        
    return False, full_name, ""

def test_parallel(max_workers: int = 5) -> List[str]:
    """
    Test authors in parallel using ThreadPoolExecutor.
    
    Args:
        max_workers: Maximum number of concurrent workers
    
    Returns:
        List of authors with mismatched report counts
    """
    file_path = "broker_analyst_2_1.xlsx"
    authors_data = extract_data(file_path)
    error_authors = []
    total_authors = len(authors_data)
    
    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and store futures
        future_to_author = {
            executor.submit(
                process_single_author, 
                author_data, 
                idx + 1, 
                total_authors
            ): author_data 
            for idx, author_data in enumerate(authors_data)
        }
        
        # Process completed futures as they finish
        for future in as_completed(future_to_author):
            has_error, full_name, error_msg = future.result()
            if has_error:
                error_authors.append(full_name)
                logging.error(error_msg)
    
    return error_authors

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run parallel test with 5 concurrent workers
    error_authors = test_parallel(max_workers=16)
    print("\nAuthors with mismatched report counts:")
    for author in error_authors:
        print(f"- {author}")

if __name__ == "__main__":
    main()