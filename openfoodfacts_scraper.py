"""
OpenFoodFacts Product Search Scraper

A small command-line Python application that searches products from the
OpenFoodFacts public API and prints clean product information.

Features:
- Uses a reusable requests session
- Adds retry handling with exponential backoff
- Shows a progress bar while pages are being processed
- Handles HTTP, network, and JSON errors safely
- Can optionally save results to a JSON file

API source:
https://world.openfoodfacts.org/
"""

import argparse
import json
import os
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


API_URL = "https://world.openfoodfacts.org/cgi/search.pl"
DEFAULT_PAGE_SIZE = 20
DEFAULT_MAX_PAGES = 2
DEFAULT_OUTPUT_FILE = "products.json"


class ProductSearchError(Exception):
    """Custom exception for product search related errors."""


def build_session() -> requests.Session:
    """
    Create and configure a requests session.

    A session is useful because it reuses the same connection settings
    and headers for every request.
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=1.2,
        status_forcelist=[403, 429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    contact_email = os.getenv("OPENFOODFACTS_CONTACT", "your-email@example.com")

    session.headers.update(
        {
            "User-Agent": f"OpenFoodFactsProductSearch/1.0 (contact: {contact_email})",
            "Accept": "application/json",
        }
    )

    return session


def print_progress_bar(current: int, total: int, width: int = 30) -> None:
    """
    Print a simple progress bar in the terminal.
    """
    total = max(total, 1)
    current = max(0, min(current, total))
    filled = int(width * current / total)
    bar = "█" * filled + "-" * (width - filled)
    print(f"\rProgress: |{bar}| {current}/{total} pages", end="", flush=True)

    if current == total:
        print()


def fetch_page(
    session: requests.Session,
    query: str,
    page: int,
    page_size: int,
) -> list[dict[str, Any]]:
    """
    Fetch one page of product results from OpenFoodFacts.
    """
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page": page,
        "page_size": page_size,
        "fields": "product_name,brands,code,countries",
    }

    try:
        response = session.get(API_URL, params=params, timeout=25)

        if response.status_code == 403:
            raise ProductSearchError(
                "Access denied by the server. Try again later or use a clearer User-Agent."
            )

        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as error:
        raise ProductSearchError(f"Network or HTTP error: {error}") from error
    except ValueError as error:
        raise ProductSearchError("The server returned invalid JSON.") from error

    products = data.get("products", [])

    if not isinstance(products, list):
        raise ProductSearchError("Unexpected API response format.")

    return products


def search_products(
    query: str,
    page_size: int = DEFAULT_PAGE_SIZE,
    max_pages: int = DEFAULT_MAX_PAGES,
    delay_seconds: float = 0.5,
) -> list[dict[str, Any]]:
    """
    Search products across multiple pages.

    The delay between pages is used to avoid sending requests too aggressively.
    """
    session = build_session()
    all_products: list[dict[str, Any]] = []

    print_progress_bar(0, max_pages)

    for page in range(1, max_pages + 1):
        print(f"\nSearching page {page}/{max_pages}...")
        products = fetch_page(session, query, page, page_size)

        if not products:
            print("No more products found.")
            break

        all_products.extend(products)
        print_progress_bar(page, max_pages)

        if page < max_pages:
            time.sleep(delay_seconds)

    return all_products


def format_product(product: dict[str, Any], index: int) -> str:
    """
    Format a single product dictionary for terminal output.
    """
    name = product.get("product_name") or "Unnamed product"
    brand = product.get("brands") or "Unknown brand"
    code = product.get("code") or "N/A"
    countries = product.get("countries") or "N/A"

    return (
        f"{index}. {name}\n"
        f"   Brand: {brand}\n"
        f"   Barcode: {code}\n"
        f"   Countries: {countries}"
    )


def print_products(products: list[dict[str, Any]]) -> None:
    """
    Print all found products in a readable format.
    """
    if not products:
        print("No products found.")
        return

    print(f"\nFound {len(products)} products:\n")

    for index, product in enumerate(products, start=1):
        print(format_product(product, index))
        print()


def save_products_to_json(
    products: list[dict[str, Any]],
    output_file: str = DEFAULT_OUTPUT_FILE,
) -> None:
    """
    Save product results to a JSON file.
    """
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(products, file, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_file}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Search product data from the OpenFoodFacts public API."
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Product name to search for, for example: chocolate, milk, pasta",
    )

    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"Number of products per page. Default: {DEFAULT_PAGE_SIZE}",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f"Maximum number of pages to fetch. Default: {DEFAULT_MAX_PAGES}",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to a JSON file.",
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output JSON filename. Default: {DEFAULT_OUTPUT_FILE}",
    )

    return parser.parse_args()


def main() -> None:
    """
    Main entry point of the application.
    """
    args = parse_arguments()

    query = args.query or input("Enter product to search: ").strip()

    if not query:
        print("Please enter a valid search term.")
        return

    if args.page_size <= 0 or args.max_pages <= 0:
        print("Page size and max pages must be positive numbers.")
        return

    try:
        products = search_products(
            query=query,
            page_size=args.page_size,
            max_pages=args.max_pages,
        )
        print_products(products)

        if args.save:
            save_products_to_json(products, args.output)

    except ProductSearchError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
