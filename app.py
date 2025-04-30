from datetime import datetime, timedelta
from flask import Flask, render_template, request
from models import db, OrderStatus
import config
from sqlalchemy import or_

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

    now = datetime.utcnow()
    cutoff = now - timedelta(days=5)

    query = OrderStatus.query.filter_by(dismissed=False)

    if not show_hidden:
        query = query.filter(
            or_(
                OrderStatus.buz_processed_time != None,
                OrderStatus.veneta_ftp_time > cutoff
            )
        )

    orders = query.order_by(OrderStatus.veneta_ftp_time.desc()).all()

    for order in orders:
        order.is_stale = (
                not order.buz_processed_time and (
                    (order.local_ftp_time and (now - order.local_ftp_time).days > 2) or
                    (order.veneta_ftp_time and (now - order.veneta_ftp_time).days > 2)
                )
        )

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
