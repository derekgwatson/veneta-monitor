import os
from datetime import datetime
from models import db, OrderStatus
import config


def poll_local_ftp():
    filenames = os.listdir(config.LOCAL_FTP_FOLDER)

    for filename in filenames:
        # Just respond to any file, no regex, no order number lookup
        order = OrderStatus.query.filter_by(local_ftp_time=None).order_by(OrderStatus.id.asc()).first()

        if order:
            order.local_ftp_time = datetime.utcnow()
            db.session.commit()
            print(f"✅ Marked order {order.order_number} as received at Local FTP (file: {filename})")
        else:
            print(f"⚠️ No open orders found to match local FTP file: {filename}")
