from ftplib import FTP
from datetime import datetime
from models import db, OrderStatus
import config


def poll_veneta_ftp():
    ftp = FTP(config.VENETA_FTP_HOST)
    ftp.login(config.VENETA_FTP_USER, config.VENETA_FTP_PASS)
    filenames = ftp.nlst()

    for filename in filenames:
        # Just respond to any file, no regex, no order number lookup
        # Find the first order that has no veneta_ftp_time yet
        order = OrderStatus.query.filter_by(veneta_ftp_time=None).order_by(OrderStatus.id.asc()).first()

        if order:
            order.veneta_ftp_time = datetime.utcnow()
            db.session.commit()
            print(f"✅ Marked order {order.order_number} as received from FTP (file: {filename})")
        else:
            print(f"⚠️ No open orders found to match FTP file: {filename}")

    ftp.quit()
