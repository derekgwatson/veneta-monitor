from datetime import datetime, timedelta
from flask import Flask, render_template, request
from models import db, OrderStatus
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.DATABASE_FILE}'
db.init_app(app)

# MANUAL TABLE CREATION
with app.app_context():
    db.create_all()


@app.route('/')
def dashboard():
    show_hidden = request.args.get('show_hidden') == '1'
    show_invoiced = request.args.get('show_invoiced') == '1'

    orders = OrderStatus.query.order_by(OrderStatus.veneta_ftp_time.desc()).all()

    return render_template(
        'dashboard.html',
        orders=orders,
        show_hidden=show_hidden,
        show_invoiced=show_invoiced,
        now=datetime.utcnow(),
        timedelta=timedelta
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
