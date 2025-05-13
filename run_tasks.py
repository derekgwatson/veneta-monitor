import traceback
import time
from services.veneta_ftp import poll_veneta_ftp
from services.local_ftp import poll_local_ftp
from services.buz_api import poll_buz_api
from app import app
import config
from services.helper import get_logger
import sys
import io


sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    logger = get_logger("tasks", config.TASKS_LOG_FILE)
    with app.app_context():
        logger.info(f"Polling every {config.POLL_INTERVAL_SECONDS} seconds")
        while True:
            try:
                poll_veneta_ftp(logger)
                poll_local_ftp(logger)
                poll_buz_api(logger)
            except Exception as e:
                logger.error(f"Error: {e}")
                logger.debug(traceback.format_exc())
            time.sleep(config.POLL_INTERVAL_SECONDS)
