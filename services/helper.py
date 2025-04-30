from models import db, OrderStatus
import config
from datetime import datetime


def create_or_update_order(order_number, veneta_time=None, local_time=None, src=None):
    order = OrderStatus.query.filter_by(order_number=order_number).first()

    if not order:
        order = OrderStatus(order_number=order_number, src=src)
        log_debug(f"✅ Creating new order: {order_number}")

    if veneta_time and not order.veneta_ftp_time:
        order.veneta_ftp_time = veneta_time
        log_debug(f"🕒 Set veneta_ftp_time for {order_number}")

    if local_time and not order.local_ftp_time:
        order.local_ftp_time = local_time
        log_debug(f"🕒 Set local_ftp_time for {order_number}")

    db.session.add(order)
    db.session.commit()


def log_debug(message):
    if config.DEBUG:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        with open(config.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
