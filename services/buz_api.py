import requests
from datetime import datetime, timedelta
from models import db, OrderStatus
import config


def get_yesterday_cutoff():
    """Return UTC midnight for yesterday formatted for OData."""
    now = datetime.utcnow()
    yesterday = datetime(now.year, now.month, now.day) - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')


def poll_buz_api():
    """Poll Buz API for yesterday's Veneta orders onward and update matching OrderStatus records."""
    cutoff = get_yesterday_cutoff()
    url = (
        f"{config.BUZ_API_URL}"
        f"?$filter=startswith(OrderDescn,'Veneta')%20and%20OrderDate%20ge%20{cutoff}"
    )

    response = requests.get(url, auth=(config.BUZ_API_USER, config.BUZ_API_PASS))

    if response.status_code != 200:
        print(f"Failed to query Buz API: Status {response.status_code}")
        print(response.text)  # Good for debugging API errors
        return

    sales_orders = response.json().get('value', [])

    if not sales_orders:
        print("No Veneta orders found from yesterday onwards.")
        return

    open_orders = OrderStatus.query.filter_by(buz_processed_time=None).all()

    for open_order in open_orders:
        for sales_order in sales_orders:
            order_descn = sales_order.get('OrderDescn', '')  # Correct field name
            if open_order.order_number in order_descn:
                open_order.buz_processed_time = datetime.utcnow()
                db.session.commit()
                print(f"✅ Matched and updated: {open_order.order_number}")
                break
