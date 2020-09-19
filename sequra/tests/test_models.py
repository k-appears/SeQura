import decimal
from unittest import TestCase
from unittest.mock import patch

from sequra.database.models import Disbursement


class Test(TestCase):

    @patch('sequra.database.models.Order.amounts_by_merchant_in_week')
    def test_calculate_amount_1(self, mock_amounts_by_merchant_in_week):
        merchant_id, week, year = 1, 1, 2020
        mock_amounts_by_merchant_in_week.return_value = [decimal.Decimal('1')]

        disbursed_amount = Disbursement.calculate_amount(merchant_id=merchant_id, week=week, year=year)

        self.assertEqual(disbursed_amount, decimal.Decimal('1.01'))

    @patch('sequra.database.models.Order.amounts_by_merchant_in_week')
    def test_calculate_amount_0_99(self, mock_amounts_by_merchant_in_week):
        merchant_id, week, year = 1, 1, 2020
        mock_amounts_by_merchant_in_week.return_value = [decimal.Decimal('0.99')]

        disbursed_amount = Disbursement.calculate_amount(merchant_id=merchant_id, week=week, year=year)

        self.assertEqual(disbursed_amount, decimal.Decimal('1.00'))

    @patch('sequra.database.models.Order.amounts_by_merchant_in_week')
    def test_calculate_amount_0_01(self, mock_amounts_by_merchant_in_week):
        merchant_id, week, year = 1, 1, 2020
        mock_amounts_by_merchant_in_week.return_value = [decimal.Decimal('0.01')]

        disbursed_amount = Disbursement.calculate_amount(merchant_id=merchant_id, week=week, year=year)

        self.assertEqual(disbursed_amount, decimal.Decimal('0.01'))

    @patch('sequra.database.models.Order.amounts_by_merchant_in_week')
    def test_calculate_amount_50_00(self, mock_amounts_by_merchant_in_week):
        merchant_id, week, year = 1, 1, 2020
        mock_amounts_by_merchant_in_week.return_value = [decimal.Decimal('50.00')]

        disbursed_amount = Disbursement.calculate_amount(merchant_id=merchant_id, week=week, year=year)

        self.assertEqual(disbursed_amount, decimal.Decimal('50.00') + decimal.Decimal('0.47'))  # 0.47499999

    @patch('sequra.database.models.Order.amounts_by_merchant_in_week')
    def test_calculate_amount_50_01(self, mock_amounts_by_merchant_in_week):
        merchant_id, week, year = 1, 1, 2020
        mock_amounts_by_merchant_in_week.return_value = [decimal.Decimal('50.01')]

        disbursed_amount = Disbursement.calculate_amount(merchant_id=merchant_id, week=week, year=year)

        self.assertEqual(disbursed_amount, decimal.Decimal('50.00') + decimal.Decimal('0.49'))  # 50.485094

    @patch('sequra.database.models.Order.amounts_by_merchant_in_week')
    def test_calculate_amount_1000(self, mock_amounts_by_merchant_in_week):
        merchant_id, week, year = 1, 1, 2020
        mock_amounts_by_merchant_in_week.return_value = [decimal.Decimal('1000')]

        disbursed_amount = Disbursement.calculate_amount(merchant_id=merchant_id, week=week, year=year)

        self.assertEqual(disbursed_amount, decimal.Decimal('1000') + decimal.Decimal('8.50'))

    @patch('sequra.database.models.Order.amounts_by_merchant_in_week')
    def test_calculate_amount_0_01__0_01(self, mock_amounts_by_merchant_in_week):
        merchant_id, week, year = 1, 1, 2020
        mock_amounts_by_merchant_in_week.return_value = [decimal.Decimal('0.01'), decimal.Decimal('0.01')]

        disbursed_amount = Disbursement.calculate_amount(merchant_id=merchant_id, week=week, year=year)

        self.assertEqual(disbursed_amount, decimal.Decimal('0.02'))

    @patch('sequra.database.models.Order.amounts_by_merchant_in_week')
    def test_calculate_amount_50_00_50_00(self, mock_amounts_by_merchant_in_week):
        merchant_id, week, year = 1, 1, 2020
        mock_amounts_by_merchant_in_week.return_value = [decimal.Decimal('50.00') + decimal.Decimal('50.00')]

        disbursed_amount = Disbursement.calculate_amount(merchant_id=merchant_id, week=week, year=year)

        self.assertEqual(disbursed_amount, decimal.Decimal('100.00') + decimal.Decimal('0.95'))  # 0.94999998
