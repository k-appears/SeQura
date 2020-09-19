import decimal

from sqlalchemy import extract
from sqlalchemy.orm import validates

from sequra.database import db


@validates('email')
def validate_email(key, address):
    """ Further work, integration with online email verification service"""
    assert '@' in address
    return address


class Disbursement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _amount = db.Column("amount", db.String(50))
    week = db.Column(db.Integer)
    year = db.Column(db.Integer)

    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)

    merchant = db.relationship('Merchant', backref=db.backref('disbursements', lazy='dynamic'))
    db.UniqueConstraint('week', 'week', name='unique_disbursement_week_year')

    @property
    def amount(self):
        """ SQLite3 does not work with decimal, the built-in representation suitable for currency
        Can be extracted as a type following the 3 times rule. """
        return decimal.Decimal(self._amount)

    @amount.setter
    def amount(self, amount: decimal.Decimal):
        self._amount = str(amount)

    def save(self, year, week, merchant):
        self.merchant_id = merchant.id
        self.week = week
        self.year = year
        # self.amount = self.calculate_amount(merchant_id=self.merchant_id, week=self.week, year=self.year)

        db.session.add(self)
        db.session.commit()

    def asdict(self):
        return {'amount': float(self.amount), 'week': self.week, 'year': self.year, 'merchant': self.merchant.name}

    @staticmethod
    def calculate_amount(merchant_id, week, year):
        orders = Order.amounts_by_merchant_in_week(merchant_id=merchant_id, week=week, year=year)
        disbursed_amount = decimal.Decimal(0.00)
        for order in orders:
            amount = decimal.Decimal(order)
            if order < 50:
                disbursed_amount = disbursed_amount + amount + (amount * decimal.Decimal(0.01))
            elif 50 <= order < 300:
                disbursed_amount = disbursed_amount + amount + (amount * decimal.Decimal(0.0095))
            else:
                disbursed_amount = disbursed_amount + amount + (amount * decimal.Decimal(0.0085))

        return decimal.Decimal(disbursed_amount.quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_HALF_UP))


@db.event.listens_for(Disbursement, "after_insert")
def add_content_to_inventory_contents(mapper, connection, target):
    amount = Disbursement.calculate_amount(merchant_id=target.merchant_id, week=target.week, year=target.year)
    table = Disbursement.__table__
    stm = table.update(). \
        where(table.c.merchant_id == target.merchant_id). \
        where(table.c.week == target.week). \
        where(table.c.year == target.year). \
        values(amount=str(amount))
    connection.execute(stm)


class Merchant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cif = db.Column(db.String(10))  # TODO validation
    email = db.Column(db.String(50))
    name = db.Column(db.String(50), index=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    shopper_id = db.Column(db.Integer, db.ForeignKey('shopper.id'), nullable=False)
    _amount = db.Column("amount", db.String(50))
    created_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    @property
    def amount(self):
        """ SQLite3 does not work with decimal, the built-in representation suitable for currency
        Can be extracted as a type following the 3 times rule. """
        return decimal.Decimal(self._amount)

    @amount.setter
    def amount(self, amount: decimal.Decimal):
        self._amount = str(amount)

    @classmethod
    def amounts_by_merchant_in_week(cls, merchant_id, week, year):
        # extract() it is slow because it uses full table scans,
        # alternative use https://docs.sqlalchemy.org/en/13/orm/composites.html or add columns -week,year- with indexes
        result = Order.query.join(Merchant, Merchant.id == Order.merchant_id).filter(
            Order.completed_at is not None,
            extract('year', Order.completed_at) == year,
            extract('week', Order.completed_at) == week - 1,
            merchant_id == Merchant.id).all()
        return [order.amount for order in result]


class Shopper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    nif = db.Column(db.String(50))  # TODO validation
