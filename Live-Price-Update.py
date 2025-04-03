import os
import json
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pyppeteer import launch

# Hardcoded Google Credentials (Not Recommended)
creds_dict = {
    "type": "service_account",
    "project_id": "scraper-69420",
    "private_key_id": "ef274378ee4925034c3c2e051df222870af2edb5",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDp7M3A3h36Jafl
msp2aO+IY0nGYeWdCPwzfSmr5LPHDuGquiiO+U37ifmAdChKpquFfC9BVJZBMs9z
UmOPkdNELLzk+yehFvpXiJYlpGcKiQoP6WYumkmCqXCeEbDDoED0iAVGDDy3smyu
iQuwtaydatHa/iw52sirSjYWIrrLXtaBFjurOH46ac+SmhfA+66lpjl8Adafm+ND
QYA28Tgn5CDK4+JA3ubsABG8oh4WnkFEdBzWreDjm+9EBXdVAOlueelD3QaFUefE
/t/2T2MwR/+MqIaONSNTI5YMITo7PEyxLAf0M2jeble8ykiSf8kaQq6PzBmwdbM+
mI2c3wxDAgMBAAECggEAKMG4BZsNmQhXjPMfxGq7FUXLVFO5OFeY7XWovYjO4+dN
XTwrFeIM+r8K6B0U6hDJAKxm5ViSB1ENgPfBXgHXz+CFltXFjVUeEAM9udg/lb/T
r3sIcSUzmp7f/sJxTFxPBOvwE0jNiWn+cphxH3w/03uJjcDMPtZGMUXwT4IEjqsl
k4wh73tinBGqHtI8xJl7lEYtfuXNjIbFDRT50I3Q1d/O4YxcwEwpZVrlIg7ypY2C
BJp2Hd5+gUajAhfO5CrXTEBwKxqbyUeIOJfWkcbLPk6KrTbAKvUC2fzmtKFR4K0y
PBUlo0Eeqzg0AlLO97rlxF8E2F0eWOxRBNL7CqmyoQKBgQD/41RdEB90xS5y1qNh
9mbumr35OhJGJKLEQbeMBTXnIqiQpEJ7yhCaJ0Ysz+XGctbFPVYplka+26zlONAL
l2ogSrgBjYwT1aDiX+/nlyu4or/7met+tDFiegR3hl50bI15iJ667Mx+6JfOr33S
g9AAxRnvkDK1H4ndpTZEkbX14wKBgQDqBwNs4QpOG7cAwetaPnDUZ7sAe515wwMK
RWREwk12T7r1J7ZeAhzr7+lKNQEFSr81wwR3GEH/V3E2k1K5TWJV4KwXraUO5JKT
NUfYcX4yXpbS9I5YHBToocuOc9MPeo/0by1Fqo5XPOC+EBgSJJJEWkxPaB70LMea
9+T5HSteIQKBgFgTyZAW4pzw2iIRGz+27osmnElS4cNfDN98t07s5DbgySCwSWoO
jVRiPFdkX/TExoQxrpy16zf6qTJlMccroQ3oahmuvQ5+s9f3qb4PXK865dYWjuaX
43+//BWgHJb6Xl/81JYGuATezpIH+ckiMdByB5FcEvghGPU/zsQfW4B9AoGAJFsE
kDSBilLJ4ic97Z4HnyeiKFgLxa+i2EShaAEbUYbfT1hk/0OqxIhXoHyNdQoAnFR4
bBvrnMQzxTurvTelUBwAAAmsu5yMnKvJRnmTFjYVjh4JwuxR3zXLToz1u9DZbiqb
SNhPFoRRkZUkeCUQR+gTNL7DGEGgnJVoD78VTqECgYACL9lx0tXPPziNOAqTJqnt
EkgAd9LoyE1KFA9il+ehKAQy3wPKuPaZrAQlxQZrzNiBmXu4ZqZJCofC6PPXqvAl
oXduN5BvF8ssZCmVyZ4zXD081g03mH1evHX6Rkkgkd+RvCD6Jokvy2Otx4Q/55ow
tykooNrOtQQ8ghzyf9nDfg==
-----END PRIVATE KEY-----""",
    "client_email": "yummyprices@scraper-69420.iam.gserviceaccount.com",
    "client_id": "108347187983876489527",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/yummyprices%40scraper-69420.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}


# Google Sheets Setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SHEET_NAME = "Live_Price_Spreadsheet"
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
    data = sheet.get_all_values()  # Read all rows
    start_row = 2  # Always start from row 2

    for i, row in enumerate(data[start_row - 1:], start=start_row):  # Skip header, start from row 2
        if len(row) < 3 or not row[0] or not row[2]:  # Check if row has enough columns & required data
            print(f"Skipping row {i}: Missing URL or Variant")
            continue

        url = row[0]  # Column A (URLs)
        variant = row[2]  # Column C (Variant Type)

        await scrape_price(url, i, variant)

import nest_asyncio
nest_asyncio.apply()
asyncio.run(main())  # Proper way to call async function
