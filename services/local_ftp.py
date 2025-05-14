import os
import xml.etree.ElementTree as ET
from datetime import datetime
import config
from services.helper import create_or_update_order


def poll_local_ftp(logger):
    all_xml_files = []
    logger.debug(f"📂 Polling local FTP folder: {config.LOCAL_FTP_FOLDER}")

    for root, dirs, files in os.walk(config.LOCAL_FTP_FOLDER):
        for filename in files:
            if filename.lower().endswith('.xml'):
                full_path = os.path.join(root, filename)
                all_xml_files.append(full_path)
                logger.debug(f"🧾 Found XML file: {full_path}")

    logger.info(f"✅ Found {len(all_xml_files)} XML file(s) in Local FTP folder")

    any_changes = False

    for filepath in all_xml_files:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            pono_element = root.find('.//PONO')

            if pono_element is None or not pono_element.text:
                logger.warning(f"⚠️ Skipping file (no PONO found): {filepath}")
                continue

            order_number = pono_element.text.strip()
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            logger.debug(f"📦 Processing order {order_number} (last modified {mod_time}) from {filepath}")

            if create_or_update_order(order_number, local_time=mod_time, src='Local', logger=logger):
                logger.info(f"📝 Updated or created order {order_number} from local FTP.")
                any_changes = True

        except Exception as e:
            logger.error(f"❌ Failed parsing file {filepath}: {e}")

    if not any_changes:
        logger.debug("✔️ No changes made from Local FTP.")
