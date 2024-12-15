@echo off
echo Mergent Online Report Scraper
echo ===========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed! Please install Python 3.8 or higher.
    echo You can download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Remove existing venv if there are issues
if exist "venv" (
    echo Cleaning up existing virtual environment...
    rmdir /s /q venv
)

REM Create new virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and install requirements
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements
    pause
    exit /b 1
)

REM Check if analysts.xlsx exists
if not exist "analysts.xlsx" (
    echo Error: analysts.xlsx file not found!
    echo Please ensure your Excel file is named 'analysts.xlsx' and is in the same directory.
    pause
    exit /b 1
)

REM Create downloads directory if it doesn't exist
if not exist "downloads" mkdir downloads

echo Starting the scraper...
echo.
echo Note: Make sure your analysts.xlsx file is in the current directory
echo and contains the required columns: name_last, report_author_clean,
echo analys, IBES_id, and report_broker_name
echo.

python src/scraper.py

echo.
echo Scraping completed! Check the downloads folder for your files.
echo Check scraper.log for detailed logging information.
pause