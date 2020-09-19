from datetime import date
from decimal import Decimal
from unittest import TestCase

from sequra import app as flask_app
from sequra.database import db
from sequra.database.models import Disbursement, Merchant, Order, Shopper


class TestCompetitionInfo(TestCase):

    @classmethod
    def setUpClass(cls):
        flask_app.initialize_app(flask_app=flask_app.app)
        db.init_app(flask_app.app)

    def setUp(self):
        with flask_app.app.app_context():
            db.drop_all()
            db.create_all()
            merchant = Merchant(cif='11111111H', email='merchant_1@test.org', name='merchant_1')
            shopper = Shopper(email='shopper_1@test.org', name='shopper 1', nif='9999999G')
            db.session.add(merchant)
            db.session.commit()
            db.session.add(shopper)
            db.session.commit()
            order = Order(merchant_id=merchant.id, shopper_id=shopper.id, amount=Decimal('1.00'),
                          created_at=date(2020, 1, 1),
                          completed_at=date(2020, 1, 1))
            db.session.add(order)
            db.session.commit()

    def tearDown(self):
        with flask_app.app.app_context():
            db.drop_all()

    def test_get_calculate_disbursement(self):
        with flask_app.app.test_client() as client:
            data = {'week': 1, 'year': 2020, 'merchant_name': 'merchant_1'}
            client.get("/calculate_disbursement", query_string=data)
            response = client.get("/disbursement", query_string=data)

            self.assertDictEqual(response.json, {'amount': 1.01, 'week': 1, 'year': 2020, 'merchant': 'merchant_1'})

    def test_get_no_disbursement(self):
        with flask_app.app.test_client() as client:
            response = client.get("/disbursement", query_string={'week': 1, 'year': 2020})

            self.assertListEqual(response.json, [])

    def test_get_disbursement(self):
        with flask_app.app.app_context():
            db.session.add(Disbursement(amount=Decimal('1.00'), week=1, year=2020, merchant_id=1))
            db.session.commit()
        with flask_app.app.test_client() as client:
            response = client.get("/disbursement", query_string={'week': 1, 'year': 2020})

            self.assertEqual(response.json[0]['amount'], 1.01)

    def test_get_disbursement_invalid_name(self):
        with flask_app.app.app_context():
            db.session.add(Disbursement(amount=Decimal('1.00'), week=1, year=2020, merchant_id=1))
            db.session.commit()
        with flask_app.app.test_client() as client:
            response = client.get("/disbursement", query_string={'week': 1, 'year': 2020, 'merchant_name': 'invalid'})

            self.assertListEqual(response.json, [])

    def test_get_disbursements(self):
        with flask_app.app.app_context():
            db.session.add(Disbursement(amount=Decimal('1.00'), week=1, year=2020, merchant_id=1))

            db.session.add(Merchant(id=2, cif='222222222I', email='merchant_2@test.org', name='merchant_2'))
            db.session.add(Shopper(id=2, email='shopper_2@test.org', name='shopper 2', nif='22222222G'))
            db.session.add(Order(merchant_id=2, shopper_id=2, amount=Decimal('1.00'),
                                 created_at=date(2020, 1, 1),
                                 completed_at=date(2020, 1, 1)))
            db.session.commit()
            db.session.add(Disbursement(amount=Decimal('1.00'), week=1, year=2020, merchant_id=2))
            db.session.commit()
        with flask_app.app.test_client() as client:
            response = client.get("/disbursement", query_string={'week': 1, 'year': 2020})

            self.assertListEqual(response.json, [{'amount': 1.01, 'week': 1, 'year': 2020, 'merchant': 'merchant_1'},
                                                 {'amount': 1.01, 'week': 1, 'year': 2020, 'merchant': 'merchant_2'}])
