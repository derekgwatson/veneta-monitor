import os
import re
from datetime import datetime
from models import db, OrderStatus
import config


def poll_local_ftp():
    filenames = os.listdir(config.LOCAL_FTP_FOLDER)

    for filename in filenames:
        match = re.search(r'(V\d{5})', filename)
        if match:
            order_number = match.group(1)
            order = OrderStatus.query.filter_by(order_number=order_number).first()
            if order and not order.local_ftp_time:
                order.local_ftp_time = datetime.now()
                db.session.commit()
