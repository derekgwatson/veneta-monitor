import os
import xml.etree.ElementTree as ET
from datetime import datetime
from models import db, OrderStatus
import config
from services.helper import create_or_update_order


def poll_local_ftp():
    all_xml_files = []
    for root, dirs, files in os.walk(config.LOCAL_FTP_FOLDER):
        for filename in files:
            if filename.lower().endswith('.xml'):
                all_xml_files.append(os.path.join(root, filename))

    print(f"✅ Found {len(all_xml_files)} XML files in Local FTP folder")

    for filepath in all_xml_files:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            pono_element = root.find('.//PONO')
            if pono_element is None or not pono_element.text:
                print(f"⚠️ No PONO found in {filepath}")
                continue

            order_number = pono_element.text.strip()
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))

            order = OrderStatus.query.filter_by(order_number=order_number).first()

            if not order:
                create_or_update_order(order_number, local_time=mod_time, src='Local')
                print(f"✅ Created new order from Local FTP: {order_number}")
            elif not order.local_ftp_time:
                order.local_ftp_time = mod_time
                db.session.commit()
                print(f"✅ Updated local_ftp_time for order: {order_number}")
            else:
                print(f"ℹ️ Order already exists with local_ftp_time: {order_number}")

        except Exception as e:
            print(f"❌ Failed parsing file {filepath}: {e}")
