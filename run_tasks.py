import time
from services.veneta_ftp import poll_veneta_ftp
from services.local_ftp import poll_local_ftp
from services.buz_api import poll_buz_api
from app import app
import config
from services.helper import log_debug
import sys
import io

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    with app.app_context():
        log_debug(f"Polling every {config.POLL_INTERVAL_SECONDS} seconds")
        while True:
            try:
                poll_veneta_ftp()
                poll_local_ftp()
                poll_buz_api()
            except Exception as e:
                log_debug(f"Error: {e}")
            time.sleep(config.POLL_INTERVAL_SECONDS)
