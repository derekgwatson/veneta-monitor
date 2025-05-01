from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean
from datetime import datetime


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

    from datetime import datetime, timedelta

    @property
    def is_stale(self):
        now = datetime.utcnow()
        if self.buz_processed_time:
            return False

        if self.local_ftp_time:
            delta = now - self.local_ftp_time
            if delta.total_seconds() > 86400:
                return True

        if self.veneta_ftp_time:
            delta = now - self.veneta_ftp_time
            if delta.total_seconds() > 86400:
                return True

        return False
