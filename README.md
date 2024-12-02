# Mergent Online Report Downloader

This project automates the process of downloading research reports from Mergent Online, specifically focusing on extracting reports from financial institutions and analysts. The application handles authentication, search criteria configuration, and bulk downloading of PDF reports.

## Project Overview

The application streamlines the following workflow:
1. Extracts analyst information from Excel spreadsheets
2. Automatically navigates Mergent Online's search interface
3. Sets specific search criteria including date ranges, report styles, and author information
4. Downloads matching reports in PDF format
5. Organizes downloaded files with consistent naming conventions

## Requirements

### Python Dependencies
```
selenium==4.16.0
beautifulsoup4==4.12.2
requests==2.31.0
urllib3==2.1.0
pandas==2.1.4
pathlib==1.0.1
certifi==2023.11.17
charset-normalizer==3.3.2
soupsieve==2.5
idna==3.6
```

### System Requirements
- Python 3.8 or higher
- Chrome WebDriver compatible with your Chrome browser version
- Sufficient storage space for downloaded PDF files

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mergent-online-auto-download.git
cd mergent-online-auto-download
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Ensure Chrome WebDriver is installed and in your system PATH.

## Usage

### Excel Data Extraction
The program reads analyst information from an Excel file with the following required columns:
- name_last
- report_author_clean
- analys
- IBES_id
- report_broker_name

### Running the Script
```python
# Extract data from Excel
last_name, first_name, analys_id, IBES_id, company = extract_data_from_excel("broker_analyst_2_1.xlsx")

# Extract report IDs and years
report_ids, report_years = extract_report_ids(first_name[0], last_name[0], company[0])

# Download reports
openfile(report_ids, company[0], analys_id[0], last_name[0], report_years[0])
```

### Output Structure
Downloaded files are saved in the following format:
```
downloads/
    CompanyName_AnalystID_LastName_ReportID_Year.pdf
```

## Features

- Robust retry mechanism for handling network issues and server responses
- Parallel processing capabilities using GitHub Actions
- Automatic handling of pagination in search results
- Comprehensive error handling and logging
- Efficient file naming and organization system

## Error Handling

The application includes multiple layers of error handling:
- Network connection issues
- Invalid search responses
- File download failures
- Data validation checks

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments

- Mergent Online for providing the research report database
- The Selenium and BeautifulSoup communities for their excellent documentation
- Contributors who have helped improve this project

## Contact

For any questions or concerns, please open an issue in the GitHub repository.

---
**Note**: This tool is intended for authorized users of Mergent Online and should be used in compliance with their terms of service.
