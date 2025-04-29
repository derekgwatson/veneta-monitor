import time
from services.veneta_ftp import poll_veneta_ftp
from services.local_ftp import poll_local_ftp
from services.buz_api import poll_buz_api
from app import app
import config


if __name__ == "__main__":
    with app.app_context():
        print(f"Polling every {config.POLL_INTERVAL_SECONDS} seconds")
        while True:
            try:
                poll_veneta_ftp()
                poll_local_ftp()
                poll_buz_api()
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(config.POLL_INTERVAL_SECONDS)
