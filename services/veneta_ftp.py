from io import BytesIO
from ftplib import FTP, error_perm
import xml.etree.ElementTree as ET
from datetime import datetime
from models import db, OrderStatus
import config
from services.helper import create_or_update_order


def recursive_list_files(ftp, path):
    file_list = []

    try:
        items = ftp.nlst()
    except error_perm:
        if path.lower().endswith('.xml'):
            file_list.append(path)
        return file_list

    for item in items:
        if item in ('.', '..'):
            continue

        full_path = f"{path}/{item}".replace('//', '/')

        try:
            # Try changing into the item to see if it's a folder
            ftp.cwd(full_path)
            # If success: it's a directory → recurse
            file_list.extend(recursive_list_files(ftp, full_path))
            ftp.cwd('..')  # ← This is critical to return back
        except error_perm:
            # Not a folder, check for .xml
            if item.lower().endswith('.xml'):
                file_list.append(full_path)

    return file_list


def poll_veneta_ftp():
    ftp = FTP(config.VENETA_FTP_HOST)
    ftp.login(config.VENETA_FTP_USER, config.VENETA_FTP_PASS)
    ftp.cwd(config.VENETA_FTP_FOLDER)

    all_xml_files = recursive_list_files(ftp, '.')
    all_xml_files = [f.lstrip('./') for f in all_xml_files]  # Clean up leading ./

    print(f"✅ Found {len(all_xml_files)} XML files on Veneta FTP")

    for filepath in all_xml_files:
        # Download and parse file
        file_buffer = BytesIO()
        ftp.retrbinary(f'RETR {filepath}', file_buffer.write)
        file_buffer.seek(0)

        try:
            tree = ET.parse(file_buffer)
            root = tree.getroot()
            pono_element = root.find('.//PONO')
            if pono_element is None or not pono_element.text:
                print(f"⚠️ No PONO found in {filepath}")
                continue

            order_number = pono_element.text.strip()
            existing = OrderStatus.query.filter_by(order_number=order_number).first()
            if not existing:
                timestamp = ftp.sendcmd(f"MDTM {filepath}")[4:].strip()  # e.g. "20250429040355"
                ftp_time = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
                create_or_update_order(order_number, veneta_time=ftp_time, src='Veneta')
                print(f"✅ Created new order from {ftp_descr} FTP: {order_number}")
#            else:
#                print(f"ℹ️ Order already exists: {order_number}")

        except Exception as e:
            print(f"❌ Failed parsing file {filepath}: {e}")

    ftp.quit()
