from services.helper import logger
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
        logger.info("ℹ️ No open orders found.")
    else:
        logger.info(f"✅ Found {len(open_orders)} open orders.")
        for order in open_orders:
            logger.debug(
                f"- Order Number: {order.order_number}, "
                f"Veneta FTP: {order.veneta_ftp_time}, "
                f"Local FTP: {order.local_ftp_time}, "
                f"Buz Processed: {order.buz_processed_time}"
            )


def parse_buz_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            logger.error(f"❌ Unable to parse Buz date: {date_str}")
            return None


def poll_buz_api():
    """Poll Buz API for Veneta orders and update matching OrderStatus records."""
    cutoff = get_cutoff_days_ago(360)

    # Fetch scheduled jobs
    schedule_url = (
        f"{config.BUZ_API_SCHEDULE_URL}"
        f"?$filter=startswith(Descn,'Veneta')%20and%20DateDoc%20ge%20{cutoff}"
    )
    logger.debug(f"Fetching schedule data from: {schedule_url}")
    schedule_response = requests.get(schedule_url, auth=(config.BUZ_API_USER, config.BUZ_API_PASS))

    if schedule_response.status_code != 200:
        logger.error(f"⚠️ Failed to fetch scheduled dates: {schedule_response.status_code}")
        scheduled_lines = []
    else:
        scheduled_lines = schedule_response.json().get('value', [])
        logger.debug(f"Retrieved {len(scheduled_lines)} scheduled job lines.")

    # Fetch sales report
    sales_url = (
        f"{config.BUZ_API_URL}"
        f"?$filter=startswith(OrderRef,'Veneta')%20and%20DateDoc%20ge%20{cutoff}"
    )
    logger.debug(f"Fetching sales report from: {sales_url}")
    response = requests.get(sales_url, auth=(config.BUZ_API_USER, config.BUZ_API_PASS))

    if response.status_code != 200:
        logger.error(f"❌ Failed to query Buz API: Status {response.status_code}")
        logger.debug(response.text)
        return

    sales_lines = response.json().get('value', [])
    logger.info(f"📦 Retrieved {len(sales_lines)} sales lines.")

    if not sales_lines:
        logger.info("No Veneta orders found from cutoff date onward.")
        return

    from sqlalchemy import or_

    open_orders = OrderStatus.query.filter(
        or_(
            OrderStatus.buz_processed_time == None,
            OrderStatus.workflow_statuses == None,
            OrderStatus.workflow_statuses == ''
        )
    ).all()

    logger.debug(f"Processing {len(open_orders)} open orders.")
    for open_order in open_orders:
        matched_lines = [
            line for line in sales_lines
            if open_order.order_number and open_order.order_number in (line.get('OrderRef') or '')
        ]

        if matched_lines:
            order_no = matched_lines[0].get('OrderNo', '').strip()
            logger.debug(f"🔍 Matching DateScheduled for OrderNo: {order_no}")

            for line in scheduled_lines:
                ref_no = (line.get("RefNo") or "").strip()
                if order_no == ref_no:
                    logger.debug(f"✅ Schedule match found: RefNo={ref_no}, DateScheduled={line.get('DateScheduled')}")

            matched_sched = next(
                (line for line in scheduled_lines if order_no == line.get("RefNo") or ""),
                None
            )

            if matched_sched:
                raw_sched_date = matched_sched.get("DateScheduled")
                parsed_sched = parse_buz_date(raw_sched_date)
                if parsed_sched:
                    open_order.date_scheduled = parsed_sched
                    logger.debug(f"🗓️ Set scheduled date: {parsed_sched}")

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
                logger.debug(f"📅 Set processed time: {parsed_date}")

            db.session.commit()
            logger.info(f"✅ Updated order {open_order.order_number} (statuses: {combined_statuses})")

        else:
            logger.warning(f"❌ No matching sales lines for open order: {open_order.order_number}")
