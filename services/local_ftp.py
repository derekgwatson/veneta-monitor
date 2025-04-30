import os
import xml.etree.ElementTree as ET
from datetime import datetime
import config
from services.helper import create_or_update_order, log_debug


def poll_local_ftp():
    all_xml_files = []
    log_debug(f"Polling local FTP folder: {config.LOCAL_FTP_FOLDER}")
    for root, dirs, files in os.walk(config.LOCAL_FTP_FOLDER):
        for filename in files:
            if filename.lower().endswith('.xml'):
                all_xml_files.append(os.path.join(root, filename))

    log_debug(f"✅ Found {len(all_xml_files)} XML files in Local FTP folder")

    for filepath in all_xml_files:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            pono_element = root.find('.//PONO')
            if pono_element is None or not pono_element.text:
                log_debug(f"⚠️ No PONO found in {filepath}")
                continue

            order_number = pono_element.text.strip()
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            create_or_update_order(order_number, local_time=mod_time, src='Local')

        except Exception as e:
            log_debug(f"❌ Failed parsing file {filepath}: {e}")
