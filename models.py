from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean


db = SQLAlchemy()


class OrderStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String, unique=True, nullable=False)
    buz_order_number = db.Column(db.String, nullable=True)
    veneta_ftp_time = db.Column(db.DateTime)
    local_ftp_time = db.Column(db.DateTime)
    buz_processed_time = db.Column(db.DateTime)
    src = db.Column(db.String(20))  # 👈 NEW: 'Veneta', 'Local', 'Buz'
    workflow_statuses = db.Column(db.String, nullable=True)
    dismissed = db.Column(Boolean, default=False)
