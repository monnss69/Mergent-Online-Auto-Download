#!/bin/bash

echo "Mergent Online Report Scraper"
echo "==========================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed! Please install Python 3.8 or higher."
    echo "You can download Python from: https://www.python.org/downloads/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if analysts.xlsx exists
if [ ! -f "analysts.xlsx" ]; then
    echo "Error: analysts.xlsx file not found!"
    echo "Please ensure your Excel file is named 'analysts.xlsx' and is in the same directory."
    exit 1
fi

# Create downloads directory if it doesn't exist
mkdir -p downloads

echo "Starting the scraper..."
echo
echo "Note: Make sure your analysts.xlsx file is in the current directory"
echo "and contains the required columns: name_last, report_author_clean,"
echo "analys, IBES_id, and report_broker_name"
echo

python3 src/scraper.py

echo
echo "Scraping completed! Check the downloads folder for your files."
echo "Check scraper.log for detailed logging information."
read -p "Press Enter to exit..."