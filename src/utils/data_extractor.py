import pandas as pd
from typing import Tuple, List
import logging
from pathlib import Path

class DataExtractor:
    """Handle Excel data extraction and preprocessing"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.logger = logging.getLogger("MergentScraper.DataExtractor")
        
    def validate_file(self) -> bool:
        """Validate input file existence and format"""
        if not self.file_path.exists():
            self.logger.error(f"File not found: {self.file_path}")
            return False
            
        if self.file_path.suffix not in ['.xlsx', '.xls']:
            self.logger.error(f"Invalid file format: {self.file_path.suffix}")
            return False
            
        return True
        
    def clean_company_name(self, name: str) -> str:
        """Clean and standardize company names"""
        if pd.isna(name):
            return ""
            
        name = str(name).strip()
        if name == "BMO Capital Markets":
            return name
            
        return name.split(' ', 1)[1] if ' ' in name else name
        
    def clean_author_name(self, name: str) -> Tuple[str, str]:
        """Extract first and last name from author field"""
        if pd.isna(name):
            return "", ""
            
        name = str(name).strip()
        parts = name.split()
        if len(parts) >= 2:
            return parts[0], parts[-1]
        return name, name
        
    def extract_data(self) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        """
        Extract and process data from Excel file
        
        Returns:
            Tuple of (last_names, first_names, analyst_ids, IBES_ids, companies)
        """
        if not self.validate_file():
            return [], [], [], [], []
            
        try:
            # Read Excel file
            df = pd.read_excel(self.file_path)
            
            # Initialize lists
            last_names = []
            first_names = []
            analyst_ids = []
            ibes_ids = []
            companies = []
            
            # Process rows
            for _, row in df.iterrows():
                # Process company name first
                if pd.isna(row['report_broker_name']):
                    break
                    
                company_name = self.clean_company_name(row['report_broker_name'])
                if not company_name:
                    break
                    
                # Extract names
                first, last = self.clean_author_name(row['report_author_clean'])
                
                # Add to lists
                companies.append(company_name)
                first_names.append(first)
                last_names.append(str(row['name_last']) if not pd.isna(row['name_last']) else last)
                analyst_ids.append(str(row['analys']) if not pd.isna(row['analys']) else '')
                ibes_ids.append(str(row['IBES_id']) if not pd.isna(row['IBES_id']) else '')
            
            self.logger.info(f"Processed {len(companies)} rows with valid company names")
            return last_names, first_names, analyst_ids, ibes_ids, companies
            
        except Exception as e:
            self.logger.error(f"Error extracting data: {str(e)}")
            return [], [], [], [], []
            
    def validate_data(self, data: Tuple[List[str], ...]) -> bool:
        """Validate extracted data for consistency"""
        if not all(len(lst) == len(data[0]) for lst in data):
            self.logger.error("Inconsistent data lengths in extracted lists")
            return False
            
        if not all(data):
            self.logger.error("Empty data lists found")
            return False
            
        return True