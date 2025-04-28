from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class OrderStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    veneta_ftp_time = db.Column(db.DateTime)
    local_ftp_time = db.Column(db.DateTime)
    buz_processed_time = db.Column(db.DateTime)
