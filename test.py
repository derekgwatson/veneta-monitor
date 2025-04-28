import requests
from datetime import datetime, timedelta

# --- Configuration ---
BUZ_API_URL = "https://api.buzmanager.com/reports/WATSO/SalesOrders"
BUZ_API_USER = 'derek+buzcbr@watsonblinds.com.au'
BUZ_API_PASS = 'Bentknob84'

# Mock your open orders (normally from database)
open_orders = [
    {"order_number": "V33172"},
    {"order_number": "V33205"},
    {"order_number": "V33333"},
]


# --- Functions ---
def get_yesterday_cutoff():
    """Return UTC midnight for yesterday formatted for OData."""
    now = datetime.utcnow()
    yesterday = datetime(now.year, now.month, now.day) - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')


def poll_buz_api():
    """Poll Buz API for yesterday's Veneta orders onward and find matching orders."""
    cutoff = get_yesterday_cutoff()
    url = (
        f"{BUZ_API_URL}"
        f"?$filter=startswith(OrderDescn,'Veneta')%20and%20OrderDate%20ge%20{cutoff}"
    )

    print(f"Polling Buz API with URL:\n{url}\n")

    response = requests.get(url, auth=(BUZ_API_USER, BUZ_API_PASS))

    if response.status_code != 200:
        print(f"Failed to query Buz API: Status {response.status_code}")
        print(response.text)  # <-- Show the server's error message if any
        return

    sales_orders = response.json().get('value', [])

    if not sales_orders:
        print("No Veneta orders found from yesterday onwards.")
        return

    print(f"Fetched {len(sales_orders)} recent Veneta orders.\n")

    print("Veneta Orders pulled from Buz:")
    for sales_order in sales_orders:
        print(f"- {sales_order.get('OrderDescn', '')}")
    print("\nStarting matching...\n")

    for open_order in open_orders:
        found = False
        for sales_order in sales_orders:
            order_desc = sales_order.get('OrderDescn', '')
            if open_order['order_number'] in order_desc:
                print(f"✅ Match found! {open_order['order_number']} in '{order_desc}'")
                found = True
                break
        if not found:
            print(f"❌ No match found for {open_order['order_number']}")


# --- Run Test ---
if __name__ == "__main__":
    poll_buz_api()
