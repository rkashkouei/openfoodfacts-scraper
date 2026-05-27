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

## Usage

Search for products:

```bash
python openfoodfacts_scraper.py chocolate
```

Limit the number of results:

```bash
python openfoodfacts_scraper.py chocolate --limit 5
```

Sort products alphabetically by product name:

```bash
python openfoodfacts_scraper.py chocolate --limit 10 --sort-name
```

Save results to a JSON file:

```bash
python openfoodfacts_scraper.py chocolate --limit 10 --save
```

Save results to a custom file:

```bash
python openfoodfacts_scraper.py chocolate --limit 10 --save --output chocolate_products.json
```
## Technologies Used

- Python
- requests
- urllib3
- argparse
- JSON

## Example Usage

```bash
python openfoodfacts_scraper.py chocolate --limit 5
```

```bash
python openfoodfacts_scraper.py pizza --limit 10 --save
```

## Project Structure

```text
openfoodfacts-scraper/
│
├── openfoodfacts_scraper.py
├── README.md
├── requirements.txt
├── .gitignore
└── sample_output.json
