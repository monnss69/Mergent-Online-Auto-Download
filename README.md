# Mergent Online Report Downloader

An intelligent web scraper for downloading research reports from Mergent Online with advanced anti-detection features and human-like behavior simulation.

## Features

- Advanced anti-detection mechanisms
- Human-like browsing behavior simulation
- Intelligent rate limiting and request distribution
- Natural timing patterns
- Robust error handling and retry mechanisms
- Comprehensive logging system
- Configurable browser fingerprinting

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mergent-online-auto-download.git
cd mergent-online-auto-download
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `config.json` file to customize behavior:

```json
{
    "max_requests_per_hour": 1000,
    "chrome_options": {
        "headless": false,
        "disable_gpu": true
    },
    "human_behavior": {
        "min_action_delay": 0.5,
        "max_action_delay": 3.0,
        "scroll_probability": 0.7,
        "mouse_movement_probability": 0.8
    }
}
```

## Usage

### Basic Usage

```bash
python src/main.py --input data/analysts.xlsx --output downloads
```

### Advanced Usage

```bash
python src/main.py \
    --input data/analysts.xlsx \
    --output downloads \
    --rate-limit 1000
```

### Arguments

- `--input`: Path to Excel file containing analyst data (required)
- `--output`: Output directory for downloaded PDFs (default: "downloads")
- `--rate-limit`: Maximum requests per hour (default: 1000)

## Project Structure

```
mergent-online-auto-download/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── browser.py        # Browser management
│   │   ├── fingerprint.py    # Browser fingerprinting
│   │   └── human_behavior.py # Behavior simulation
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py         # Logging configuration
│   │   ├── rate_limiter.py   # Rate limiting
│   │   └── data_extractor.py # Data extraction
│   ├── downloaders/
│   │   ├── __init__.py
│   │   └── pdf_downloader.py # PDF download logic
│   ├── config.py            # Configuration management
│   └── main.py             # Entry point
├── requirements.txt
└── README.md
```

## Anti-Detection Features

1. Browser Fingerprinting
   - Random screen resolutions
   - Variable color depths
   - Platform rotation
   - Hardware concurrency variation
   - Canvas fingerprint randomization

2. Human Behavior Simulation
   - Natural mouse movements
   - Random scrolling patterns
   - Variable typing speeds
   - Realistic click patterns
   - Page interaction simulation

3. Request Management
   - Intelligent rate limiting
   - Natural request distribution
   - Header variation
   - Response handling delays

## Error Handling

- Automatic retries with exponential backoff
- Session recovery
- Comprehensive error logging
- Graceful failure handling

## Excel File Format

The input Excel file should contain the following columns:
- `name_last`: Last name of the analyst
- `report_author_clean`: Full name of the report author
- `analys`: Analyst ID
- `IBES_id`: IBES identifier
- `report_broker_name`: Name of the brokerage firm

## Output Format

Downloaded files will be saved with the following naming convention:
```
[output_directory]/[company_name]_[analyst_id]_[last_name]_[file_num]_[year].pdf
```

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is intended for authorized users of Mergent Online and should be used in compliance with their terms of service. Please ensure you have proper authorization before using this tool.

## Troubleshooting

Common issues and solutions:

1. Chrome Driver Issues
   - Ensure Chrome is installed
   - Update Chrome to the latest version
   - Check ChromeDriver compatibility

2. Rate Limiting
   - Adjust max_requests_per_hour in config
   - Monitor scraper.log for rate limit warnings
   - Increase delays in human_behavior settings

3. Download Failures
   - Check network connectivity
   - Verify file permissions
   - Review error messages in logs

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in your output directory
3. Open an issue on GitHub with:
   - Full error message
   - Relevant log snippets
   - Configuration being used