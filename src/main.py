import argparse
from pathlib import Path
import logging

from utils.logger import LoggerManager
from utils.data_extractor import DataExtractor
from utils.rate_limiter import RateLimiter
from core.browser import BrowserManager
from downloaders.pdf_downloader import PDFDownloader

class MergentScraper:
    def __init__(self, config: dict):
        self.config = config
        self.logger = LoggerManager.get_logger()
        self.rate_limiter = RateLimiter(
            max_requests=config.get('max_requests_per_hour', 1000),
            time_window=3600
        )
        self.browser_manager = BrowserManager()
        self.pdf_downloader = PDFDownloader(
            rate_limiter=self.rate_limiter,
            output_dir=config.get('output_dir', 'downloads')
        )

    def process_analyst(self, analyst_data: tuple):
        """Process a single analyst's data"""
        first_name, last_name, analyst_id, ibes_id, company = analyst_data
        
        try:
            self.logger.info(f"Processing analyst: {first_name} {last_name}")
            
            # Initialize browser
            driver = self.browser_manager.create_driver()
            
            # Extract report IDs
            ids, years = self.extract_report_ids(
                driver=driver,
                firstname=first_name,
                lastname=last_name,
                contributor_name=company
            )
            
            if not ids:
                self.logger.warning(f"No reports found for {first_name} {last_name}")
                return
            
            # Download reports
            for i, (report_id, year) in enumerate(zip(ids, years)):
                file_path = self.pdf_downloader.download_pdf(
                    url=self.generate_download_url(report_id),
                    company_name=company,
                    id=analyst_id,
                    last_name=last_name,
                    file_num=len(ids) - i,
                    year=year
                )
                if file_path:
                    self.logger.info(f"Successfully downloaded: {file_path}")
                    
        except Exception as e:
            self.logger.error(f"Error processing {first_name} {last_name}: {str(e)}")
            
        finally:
            self.browser_manager.cleanup()

    def process_all(self):
        """Process all analysts sequentially"""
        try:
            # Extract data
            data_extractor = DataExtractor(self.config['input_file'])
            data = data_extractor.extract_data()
            
            if not data_extractor.validate_data(data):
                self.logger.error("Data validation failed")
                return
            
            # Create analyst data tuples and process each
            analysts = list(zip(*data))
            for analyst in analysts:
                self.process_analyst(analyst)
                
        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")

    @staticmethod
    def generate_download_url(report_id: str) -> str:
        """Generate download URL for a report"""
        base_url = 'https://www.mergentonline.com/investextsearchlive.php'
        return f"{base_url}?opt=loadDocument&docid=%5B%22{report_id}%22%5D&doctype=pdf"

def parse_args():
    parser = argparse.ArgumentParser(description='Mergent Online Report Scraper')
    parser.add_argument('--input', required=True, help='Input Excel file path')
    parser.add_argument('--output', default='downloads', help='Output directory for PDFs')
    parser.add_argument('--rate-limit', type=int, default=1000,
                      help='Maximum requests per hour')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Setup logging
    LoggerManager.setup(
        log_file=Path(args.output) / "scraper.log",
        level=logging.INFO
    )
    
    # Configure scraper
    config = {
        'input_file': args.input,
        'output_dir': args.output,
        'max_requests_per_hour': args.rate_limit
    }
    
    # Run scraper
    scraper = MergentScraper(config)
    scraper.process_all()

if __name__ == "__main__":
    main()