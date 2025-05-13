from io import BytesIO
import xml.etree.ElementTree as ET
from datetime import datetime
import config
from services.helper import create_or_update_order
import ftplib
import os


def recursive_list_files(ftp, path, logger):
    file_list = []
    try:
        ftp.cwd(path)
        logger.debug(f"📁 Entering directory: {ftp.pwd()}")

        items = ftp.nlst()
        for item in items:
            if item in ('.', '..'):
                continue

            full_path = f"{path.rstrip('/')}/{item}"

            try:
                ftp.cwd(full_path)
                # It's a directory
                file_list.extend(recursive_list_files(ftp, full_path, logger))
                ftp.cwd(path)  # Go back to parent dir
            except ftplib.error_perm:
                # Not a directory; check if it's an XML file
                if item.lower().endswith('.xml'):
                    logger.debug(f"📄 Found XML file: {full_path}")
                    file_list.append(full_path)

    except ftplib.all_errors as e:
        logger.error(f"❌ Error accessing {path}: {e}")
    return file_list


def poll_veneta_ftp(logger):
    logger.info(f"🔌 Connecting to Veneta FTP: {config.VENETA_FTP_HOST}")
    ftp = ftplib.FTP(config.VENETA_FTP_HOST)
    ftp.login(config.VENETA_FTP_USER, config.VENETA_FTP_PASS)
    ftp.cwd(config.VENETA_FTP_FOLDER)
    logger.info(f"Accessed folder: {config.VENETA_FTP_FOLDER}")

    all_xml_files = recursive_list_files(ftp, ftp.pwd(), logger)
    logger.info(f"Found {len(all_xml_files)} XML file(s) on Veneta FTP")

    for filepath in all_xml_files:
        logger.debug(f"Downloading file: {filepath}")
        file_buffer = BytesIO()
        ftp.retrbinary(f'RETR {filepath}', file_buffer.write)
        file_buffer.seek(0)

        try:
            tree = ET.parse(file_buffer)
            root = tree.getroot()
            pono_element = root.find('.//PONO')

            if pono_element is None or not pono_element.text:
                logger.warning(f"Skipping file (no PONO found): {filepath}")
                continue

            order_number = pono_element.text.strip()

            # try to get file timestamp
            try:
                timestamp_raw = ftp.sendcmd(f"MDTM {filepath}")
                if not timestamp_raw.startswith("213 "):
                    raise ValueError(f"Unexpected MDTM response: {timestamp_raw}")

                timestamp = timestamp_raw[4:].strip()
                if not timestamp or len(timestamp) != 14:
                    raise ValueError(f"Invalid timestamp format: {timestamp}")

                ftp_time = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
            except Exception as e:
                logger.warning(f"⚠️ Skipping file (could not parse timestamp for {filepath}): {e}")
                continue

            logger.debug(f"Parsed order {order_number}, FTP timestamp: {ftp_time}")
            create_or_update_order(order_number, veneta_time=ftp_time, src='Veneta')
            logger.info(f"Updated or created order {order_number} from Veneta FTP.")

        except Exception as e:
            logger.error(f"Failed parsing file {filepath}: {e}")

    ftp.quit()
    logger.info("🔌 Disconnected from Veneta FTP")
