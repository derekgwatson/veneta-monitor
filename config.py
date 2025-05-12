import os

VENETA_FTP_HOST = '116.90.48.20'
VENETA_FTP_USER = 'Newwatson@venetause.com.au'
VENETA_FTP_PASS = 'jR=tm]J;Aa3x'
VENETA_FTP_FOLDER = '/public_html'

BUZ_API_URL = 'https://api.buzmanager.com/reports/WATSO/SalesReport'
BUZ_API_SCHEDULE_URL = 'https://api.buzmanager.com/reports/WATSO/JobsScheduleDetailed'
BUZ_API_USER = 'derek+buzcbr@watsonblinds.com.au'
BUZ_API_PASS = 'Bentknob84'

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_FILE = os.path.join(basedir, 'orders.db')

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")  # Can be set via environment variable

if os.getenv("APP_ENV", "dev") == "prod":
    LOCAL_FTP_FOLDER = '/home/veneta/ftp/files'
    POLL_INTERVAL_SECONDS = 60  # how often to check
    LOG_FILE = "/var/log/veneta_monitor.log"
elif os.getenv("APP_ENV", "dev") == "staging":
    LOCAL_FTP_FOLDER = '/home/veneta/ftp/files'
    POLL_INTERVAL_SECONDS = 60  # how often to check
    LOG_FILE = "/var/log/veneta_monitor_staging.log"
else:
    LOCAL_FTP_FOLDER = 'C:\\Users\\Derek\\Downloads\\ftp_test'
    POLL_INTERVAL_SECONDS = 5
    LOG_FILE = os.path.join(os.getenv("TEMP", "C:\\temp"), "veneta_monitor.log")
