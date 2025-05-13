import logging
from logging.handlers import RotatingFileHandler
import os
from models import db, OrderStatus
import config


def create_or_update_order(order_number, veneta_time=None, local_time=None, src=None, logger=None):
    if logger is None:
        logger = logging.getLogger("fallback")  # Won’t have handlers, but avoids crash

    order = OrderStatus.query.filter_by(order_number=order_number).first()

    if not order:
        order = OrderStatus(order_number=order_number, src=src)
        logger.info(f"✅ Creating new order: {order_number}")

    if veneta_time and not order.veneta_ftp_time:
        order.veneta_ftp_time = veneta_time
        logger.info(f"🕒 Set veneta_ftp_time for {order_number}")

    if local_time and not order.local_ftp_time:
        order.local_ftp_time = local_time
        logger.info(f"🕒 Set local_ftp_time for {order_number}")

    db.session.add(order)
    db.session.commit()


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
