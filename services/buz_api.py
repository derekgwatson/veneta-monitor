import re
import requests
from datetime import datetime, timedelta
from models import db, OrderStatus
import config


def get_cutoff_days_ago(days=7):
    now = datetime.utcnow()
    cutoff = datetime(now.year, now.month, now.day) - timedelta(days=days)
    return cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')


def debug_open_orders():
    from sqlalchemy import or_

    open_orders = OrderStatus.query.filter(
        or_(
            OrderStatus.buz_processed_time == None,
            OrderStatus.workflow_statuses == None,
            OrderStatus.workflow_statuses == ''
        )
    ).all()

    if not open_orders:
        print("ℹ️ No open orders found.")
    else:
        print(f"✅ Found {len(open_orders)} open orders:")
        for order in open_orders:
            print(f"- Order Number: {order.order_number}, "
                  f"Veneta FTP: {order.veneta_ftp_time}, "
                  f"Local FTP: {order.local_ftp_time}, "
                  f"Buz Processed: {order.buz_processed_time}")


def parse_buz_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        # Try fallback format
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"❌ Unable to parse Buz date: {date_str}")
            return None


def poll_buz_api():
    """Poll Buz API for yesterday's Veneta orders onward and update matching OrderStatus records."""
    cutoff = get_cutoff_days_ago(360)
    url = (
        f"{config.BUZ_API_URL}"  # Use SalesReport now
        f"?$filter=startswith(OrderRef,'Veneta')%20and%20DateDoc%20ge%20{cutoff}"
    )

    response = requests.get(url, auth=(config.BUZ_API_USER, config.BUZ_API_PASS))

    if response.status_code != 200:
        print(f"Failed to query Buz API: Status {response.status_code}")
        print(response.text)
        return

    sales_lines = response.json().get('value', [])

    if not sales_lines:
        print("No Veneta orders found from yesterday onwards.")
        return

    open_orders = OrderStatus.query.filter_by(buz_processed_time=None).all()

    for open_order in open_orders:
        matched_lines = [
            line for line in sales_lines
            if open_order.order_number and open_order.order_number in (line.get('OrderRef') or '')
        ]

        if matched_lines:
            # Pull the first OrderNo (they'll all be the same for the order)
            order_no = matched_lines[0].get('OrderNo', '').strip()

            workflow_statuses = []

            for line in matched_lines:
                status = line.get('Workflow_Job_Tracking_Status') or line.get('Order_Status')
                if status:
                    workflow_statuses.append(status.strip())

            workflow_statuses = sorted(set(workflow_statuses))

            combined_statuses = ', '.join(workflow_statuses)

            open_order.buz_order_number = order_no
            open_order.workflow_statuses = combined_statuses
            raw_date = matched_lines[0].get('DateDoc')
            parsed_date = parse_buz_date(raw_date)
            if parsed_date:
                open_order.buz_processed_time = parsed_date

            db.session.commit()
            print(f"✅ Matched and updated: {open_order.order_number} (statuses: {combined_statuses})")
        else:
            print(f"❌ No matching sales lines for order: {open_order.order_number}")
