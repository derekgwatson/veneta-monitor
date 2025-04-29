import os
import xml.etree.ElementTree as ET
from datetime import datetime
from models import db, OrderStatus
import config


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
            existing = OrderStatus.query.filter_by(order_number=order_number).first()
            if not existing:
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                new_order = OrderStatus(order_number=order_number, local_ftp_time=mod_time, src='Local')
                db.session.add(new_order)
                db.session.commit()
                print(f"✅ Created new order from Local FTP: {order_number}")
            else:
                print(f"ℹ️ Order already exists: {order_number}")

        except Exception as e:
            print(f"❌ Failed parsing file {filepath}: {e}")
