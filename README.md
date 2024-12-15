# Mergent Online Report Scraper - User Guide

This tool helps you automatically download research reports from Mergent Online based on analyst information provided in an Excel file.

## Prerequisites

1. Python 3.8 or higher installed on your computer
2. Google Chrome browser installed
3. Excel file named `analysts.xlsx` with the following columns:
   - name_last
   - report_author_clean
   - analys
   - IBES_id
   - report_broker_name

## Quick Start Guide

### For Windows Users:

1. Download this folder to your computer
2. Place your `analysts.xlsx` file in the same folder as the scripts
3. Double-click `run_scraper.bat`
4. Follow the prompts on screen

### For Mac/Linux Users:

1. Download this folder to your computer
2. Place your `analysts.xlsx` file in the same folder as the scripts
3. Open Terminal in this folder
4. Run the following commands:
   ```bash
   chmod +x run_scraper.sh
   ./run_scraper.sh
   ```
5. Follow the prompts on screen

## Excel File Format

Your `analysts.xlsx` file should be formatted as follows:
- Each row represents one analyst
- Required columns:
  - name_last: Analyst's last name
  - report_author_clean: Full name of the analyst
  - analys: Analyst ID
  - IBES_id: IBES identifier
  - report_broker_name: Name of the brokerage firm

## Output

- Downloaded reports will be saved in the `downloads` folder
- Each report will be named in the format: `CompanyName_AnalystID_LastName_ReportNumber_Year.pdf`
- A log file (`scraper.log`) will be created with detailed information about the scraping process

## Troubleshooting

1. If you get a Python error:
   - Make sure Python 3.8 or higher is installed
   - Try running the installer again

2. If you get a Chrome error:
   - Make sure Google Chrome is installed
   - Try updating Chrome to the latest version

3. If no reports are downloaded:
   - Check your Excel file format
   - Verify your internet connection
   - Check the log file for detailed error messages

## Support

If you encounter any issues:
1. Check the log file (scraper.log)
2. Verify your Excel file format
3. Ensure all prerequisites are met
4. Contact technical support if issues persist