from io import BytesIO
from ftplib import FTP, error_perm
import xml.etree.ElementTree as ET
from datetime import datetime
from models import db, OrderStatus
import config


def recursive_list_files(ftp, path):
    file_list = []
    original_path = ftp.pwd()

    try:
        ftp.cwd(path)
        items = ftp.nlst()
    except error_perm:
        if path.lower().endswith('.xml'):
            file_list.append(path)
        ftp.cwd(original_path)
        return file_list

    for item in items:
        if item in ('.', '..'):
            continue

        try:
            ftp.cwd(item)
            # It's a folder → recurse
            file_list.extend(recursive_list_files(ftp, item))
            ftp.cwd('..')
        except error_perm:
            if item.lower().endswith('.xml'):
                full_file_path = f"{ftp.pwd()}/{item}".replace('//', '/')
                file_list.append(full_file_path)

    ftp.cwd(original_path)
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
                veneta_time = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
                new_order = OrderStatus(order_number=order_number, veneta_ftp_time=veneta_time, src='Veneta')
                db.session.add(new_order)
                db.session.commit()
                print(f"✅ Created new order from Veneta FTP: {order_number}")
            else:
                print(f"ℹ️ Order already exists: {order_number}")

        except Exception as e:
            print(f"❌ Failed parsing file {filepath}: {e}")

    ftp.quit()
