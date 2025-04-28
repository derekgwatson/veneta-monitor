from ftplib import FTP
import re
from datetime import datetime
from models import db, OrderStatus
import config


def poll_veneta_ftp():
    ftp = FTP(config.VENETA_FTP_HOST)
    ftp.login(config.VENETA_FTP_USER, config.VENETA_FTP_PASS)
    filenames = ftp.nlst()

    for filename in filenames:
        match = re.search(r'(V\d{5})', filename)
        if match:
            order_number = match.group(1)
            order = OrderStatus.query.filter_by(order_number=order_number).first()
            if not order:
                order = OrderStatus(order_number=order_number, veneta_ftp_time=datetime.now())
                db.session.add(order)
            else:
                if not order.veneta_ftp_time:
                    order.veneta_ftp_time = datetime.now()
            db.session.commit()

    ftp.quit()
