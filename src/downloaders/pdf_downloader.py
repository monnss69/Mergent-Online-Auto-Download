import requests
from pathlib import Path
import time
import random
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict
from ..utils.rate_limiter import RequestManager

class PDFDownloader:
    def __init__(self, rate_limiter, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.request_manager = RequestManager(rate_limiter)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a session with appropriate headers and settings"""
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        return session

    def _generate_filename(self, company_name: str, id: str, last_name: str, 
                          file_num: int, year: str) -> str:
        """Generate consistent filename for downloaded PDF"""
        # Clean input parameters
        company_name = "".join(c for c in company_name if c.isalnum() or c in "._- ")
        last_name = last_name.split(",")[0].strip()
        return f"{company_name}_{id}_{last_name}_{file_num}_{year}.pdf"

    def download_pdf(self, url: str, company_name: str, id: str, last_name: str,
                    file_num: int, year: str, max_retries: int = 5) -> Optional[str]:
        """
        Download PDF with retry mechanism and human-like behavior
        
        Args:
            url: URL of the PDF
            company_name: Company name for filename
            id: ID for filename
            last_name: Last name for filename
            file_num: File number for filename
            year: Year for filename
            max_retries: Maximum number of retry attempts
        
        Returns:
            Path to downloaded file or None if download failed
        """
        filename = self._generate_filename(company_name, id, last_name, file_num, year)
        output_path = self.output_dir / filename

        current_retry = 0
        while current_retry < max_retries:
            try:
                # Wait for rate limiter
                self.request_manager.pre_request()

                logging.info(f"Downloading {url} (Attempt {current_retry + 1}/{max_retries})")
                response = self.session.get(url, stream=True, timeout=(10, 30))
                response.raise_for_status()

                # Handle redirects
                if "text/html" in response.headers.get("content-type", ""):
                    soup = BeautifulSoup(response.text, "html.parser")
                    if meta_refresh := soup.find("meta", attrs={"http-equiv": "refresh"}):
                        if "url=" in meta_refresh["content"]:
                            redirect_url = meta_refresh["content"].split("url=")[-1]
                            logging.info(f"Following redirect to: {redirect_url}")
                            url = redirect_url
                            continue

                # Verify PDF content
                if "application/pdf" not in response.headers.get("content-type", ""):
                    raise ValueError("Response is not a PDF")

                # Save the PDF with progress tracking
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                wrote = 0

                with open(output_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        wrote += len(data)
                        f.write(data)
                        # Add random delays to simulate human download behavior
                        if random.random() < 0.1:
                            time.sleep(random.uniform(0.1, 0.3))

                if total_size != 0 and wrote != total_size:
                    raise ValueError("Downloaded file size mismatch")

                logging.info(f"Successfully downloaded: {output_path}")
                return str(output_path)

            except Exception as e:
                current_retry += 1
                delay = min(2 ** current_retry + random.uniform(0, 1), 60)
                logging.warning(f"Download failed: {str(e)}. Retrying in {delay:.1f}s...")
                time.sleep(delay)

            finally:
                self.request_manager.post_request()

        logging.error(f"Failed to download PDF after {max_retries} attempts")
        return None

    def batch_download(self, downloads: list[Dict]) -> list[str]:
        """
        Download multiple PDFs with rate limiting
        
        Args:
            downloads: List of dictionaries containing download information
            
        Returns:
            List of successfully downloaded file paths
        """
        successful_downloads = []
        
        for download in downloads:
            if path := self.download_pdf(**download):
                successful_downloads.append(path)
                
        return successful_downloads