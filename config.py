import os
import tempfile

VENETA_FTP_HOST = '116.90.48.20'
VENETA_FTP_USER = 'Newwatson@venetause.com.au'
VENETA_FTP_PASS = 'jR=tm]J;Aa3x'
VENETA_FTP_FOLDER = '/public_html'

BUZ_API_URL = 'https://api.buzmanager.com/reports/WATSO/SalesReport'
BUZ_API_USER = 'derek+buzcbr@watsonblinds.com.au'
BUZ_API_PASS = 'Bentknob84'

DATABASE_FILE = 'orders.db'

LOG_FILE = os.path.join(tempfile.gettempdir(), "veneta_monitor.log")

if os.getenv("APP_ENV", "dev") == "prod":
    DEBUG = False
    LOCAL_FTP_FOLDER = '/home/veneta/ftp/files'
    POLL_INTERVAL_SECONDS = 60  # how often to check
else:
    DEBUG = True
    LOCAL_FTP_FOLDER = 'C:\\Users\\Derek\\Downloads\\ftp_test'
    POLL_INTERVAL_SECONDS = 5
