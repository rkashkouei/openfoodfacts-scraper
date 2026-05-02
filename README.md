# OpenFoodFacts Product Scraper

## Overview

This project is a Python command-line tool that searches for food products using the OpenFoodFacts public API.

It demonstrates API interaction, error handling, retry strategies, pagination, progress display, and clean data processing.

## Features

- Search products by keyword
- Fetch multiple pages of results
- Retry mechanism with exponential backoff
- Error handling for network and API issues
- Progress bar in the terminal
- Optional JSON export

## Technologies Used

- Python
- requests
- urllib3
- argparse
- JSON

## Project Structure

```text
openfoodfacts-scraper/
│
├── openfoodfacts_scraper.py
├── README.md
├── requirements.txt
├── .gitignore
└── sample_output.json