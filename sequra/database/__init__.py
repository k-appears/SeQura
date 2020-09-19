import datetime
import json
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _records_from_json(json_path: Path):
    with json_path.open() as file_d:
        data = json.load(file_d)
    return data["RECORDS"]


def init_db_seed():
    from sequra.database.models import Order, Merchant, Shopper
    resources_dir = Path(__file__).parent.parent / './resources'
    orders_file = resources_dir / 'orders.json'
    merchants_file = resources_dir / 'merchants.json'
    shoppers_file = resources_dir / 'shoppers.json'

    for order_dict in _records_from_json(orders_file):
        order = Order(**order_dict)
        if order_dict['completed_at']:
            order.completed_at = datetime.datetime.strptime(order_dict['completed_at'], '%d/%m/%Y %H:%M:%S')
        else:
            order.completed_at = None
        order.created_at = datetime.datetime.strptime(order_dict['created_at'], '%d/%m/%Y %H:%M:%S')
        db.session.add(order)

    for merchant_dict in _records_from_json(merchants_file):
        merchant = Merchant(**merchant_dict)
        db.session.add(merchant)

    for shopper_dict in _records_from_json(shoppers_file):
        shopper = Shopper(**shopper_dict)
        db.session.add(shopper)

    db.session.commit()
