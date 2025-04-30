from models import db, OrderStatus


def create_or_update_order(order_number, veneta_time=None, local_time=None, src=None):
    order = OrderStatus.query.filter_by(order_number=order_number).first()

    if not order:
        order = OrderStatus(order_number=order_number, src=src)
        print(f"✅ Creating new order: {order_number}")

    if veneta_time and not order.veneta_ftp_time:
        order.veneta_ftp_time = veneta_time
        print(f"🕒 Set veneta_ftp_time for {order_number}")

    if local_time and not order.local_ftp_time:
        order.local_ftp_time = local_time
        print(f"🕒 Set local_ftp_time for {order_number}")

    db.session.add(order)
    db.session.commit()
