import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pyppeteer import launch

# Google Sheets Setup
SHEET_NAME = "Live_Price_Spreadsheet"
CREDENTIALS_FILE = "/content/scraper-69420-0c2fa11c82b0.json"  # Replace with your credentials JSON file

# Authenticate and open Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1  # Use the first sheet

async def scrape_price(url, row_number, expected_variant):
    """Scrape Flipkart and Amazon prices from MySmartPrice and update Google Sheets."""
    print(f"Scraping row {row_number} | URL: {url} | Expected Variant: {expected_variant}")  # Debug print

    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()

    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    )

    await page.goto(url, {"waitUntil": "networkidle2"})

    # Default prices
    found_prices = {"Flipkart": "N/A", "Amazon": "N/A"}

    variant_index = 1
    variant_found = False

    while True:
        try:
            # Select variant name dynamically
            variant_selector = f"#allStores > div > div:nth-child({variant_index}) > div.d-flex.j-c.w-100.prdt_vrnt > div.vrnt_txt.txt-heading.txt-w-b.pos-rel.pos-after.lst_sprite"
            variant_name = await page.querySelectorEval(variant_selector, "(el) => el.innerText.trim()")
            variant_found = True
        except:
            break  # No more variants or no variant exists

        # Extract store names
        store_elements = await page.querySelectorAll(f"#allStores > div > div:nth-child({variant_index}) div.store-logo")
        stores = [await page.evaluate('(el) => el.innerText.trim()', store) for store in store_elements]

        # Extract prices
        price_elements = await page.querySelectorAll(f"#allStores > div > div:nth-child({variant_index}) div.store-price.txt-w-b")
        prices = [await page.evaluate('(el) => el.innerText.trim()', price) for price in price_elements]

        # Ensure stores & prices are aligned
        min_length = min(len(stores), len(prices))
        store_prices = dict(zip(stores[:min_length], prices[:min_length]))

        # If this is the correct variant, extract Flipkart & Amazon prices
        if variant_name == expected_variant:
            found_prices["Flipkart"] = store_prices.get("Flipkart", "N/A")
            found_prices["Amazon"] = store_prices.get("Amazon", "N/A")
            break  # Stop looping since we found the right variant

        variant_index += 1  # Move to next variant

    # If no variant structure exists, extract prices from the default listing
    if not variant_found:
        store_elements = await page.querySelectorAll("#allStores div.store-logo")
        stores = [await page.evaluate('(el) => el.innerText.trim()', store) for store in store_elements]

        price_elements = await page.querySelectorAll("#allStores div.store-price.txt-w-b")
        prices = [await page.evaluate('(el) => el.innerText.trim()', price) for price in price_elements]

        min_length = min(len(stores), len(prices))
        store_prices = dict(zip(stores[:min_length], prices[:min_length]))

        found_prices["Flipkart"] = store_prices.get("Flipkart", "N/A")
        found_prices["Amazon"] = store_prices.get("Amazon", "N/A")

    await browser.close()

    # Debug prints for found prices
    print(f"Row {row_number} - Flipkart: {found_prices['Flipkart']} | Amazon: {found_prices['Amazon']}")

    # Update Google Sheets with the found prices
    sheet.update_cell(row_number, 5, found_prices["Flipkart"])  # Column E (Flipkart)
    sheet.update_cell(row_number, 6, found_prices["Amazon"])  # Column F (Amazon)

    print(f"Updated row {row_number} successfully.")  # Debug print

async def main():
    start_row = int(input("Enter the starting row number: "))  # Prompt user for row input
    data = sheet.get_all_values()  # Read all rows

    for i, row in enumerate(data[start_row - 1:], start=start_row):  # Start from the user-specified row
        url = row[0]  # Column A (URLs)
        variant = row[2]  # Column C (Variant Type)

        if url and variant:
            await scrape_price(url, i, variant)

import nest_asyncio
nest_asyncio.apply()
await main()
