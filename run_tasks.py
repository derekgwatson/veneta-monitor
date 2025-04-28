import time
from services.veneta_ftp import poll_veneta_ftp
from services.local_ftp import poll_local_ftp
from services.buz_api import poll_buz_api
from app import app

if __name__ == "__main__":
    with app.app_context():
        while True:
            try:
                poll_veneta_ftp()
                poll_local_ftp()
                poll_buz_api()
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(60)  # every 60 seconds
