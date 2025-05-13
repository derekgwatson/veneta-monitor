from datetime import datetime, timedelta
from flask import Flask, render_template, request
from models import db, OrderStatus
import config
from services.helper import get_logger
import sys
import atexit
import os

# Create dedicated logger for the web app
logger = get_logger("web-app", config.WEBAPP_LOG_FILE)

# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.DATABASE_FILE}'
db.init_app(app)

# Ensure UTF-8 encoding for logs/output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Run once on startup to create tables if needed
with app.app_context():
    db.create_all()
    logger.info("✅ Tables created or already exist")


# Handle 500 errors with logging
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"🔥 Server error, not good: {error}", exc_info=True)
    return "Something went terribly wrong :/ Someone should really do something about that", 500


# Home dashboard route
@app.route('/')
def dashboard():
    show_hidden = request.args.get('show_hidden') == '1'
    show_invoiced = request.args.get('show_invoiced') == '1'
    logger.debug(f"📥 Dashboard request: show_hidden={show_hidden}, show_invoiced={show_invoiced}")

    orders = OrderStatus.query.order_by(OrderStatus.veneta_ftp_time.desc()).all()

    return render_template(
        'dashboard.html',
        orders=orders,
        show_hidden=show_hidden,
        show_invoiced=show_invoiced,
        now=datetime.utcnow(),
        timedelta=timedelta
    )


# Optional: Log shutdown
def on_exit():
    logger.info("🛑 Flask app shutting down")


atexit.register(on_exit)


# Main entry point
if __name__ == "__main__":
    logger.info("🚀 Starting Flask app on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
