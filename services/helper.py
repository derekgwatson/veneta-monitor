import logging
from logging.handlers import RotatingFileHandler
import os
from models import db, OrderStatus
import config


def create_or_update_order(order_number, veneta_time=None, local_time=None, src=None, logger=None):
    if logger is None:
        logger = logging.getLogger("fallback")

    order = OrderStatus.query.filter_by(order_number=order_number).first()
    is_new = order is None
    updated = False

    if is_new:
        order = OrderStatus(order_number=order_number, src=src)
        updated = True  # New order is always an update

    if veneta_time and order.veneta_ftp_time != veneta_time:
        order.veneta_ftp_time = veneta_time
        updated = True

    if local_time and order.local_ftp_time != local_time:
        order.local_ftp_time = local_time
        updated = True

    if is_new or updated:
        db.session.add(order)
        db.session.commit()

        if is_new:
            logger.info(f"✅ Creating new order: {order_number}")
        if veneta_time and (is_new or order.veneta_ftp_time == veneta_time):
            logger.info(f"🕒 Set veneta_ftp_time for {order_number}")
        if local_time and (is_new or order.local_ftp_time == local_time):
            logger.info(f"🕒 Set local_ftp_time for {order_number}")

    return is_new or updated


def get_logger(name: str, log_file: str, level=config.LOG_LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if logger.hasHandlers():
        return logger  # Prevent duplicate handlers

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    handler = RotatingFileHandler(log_file, maxBytes=2 * 1024 * 1024, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
