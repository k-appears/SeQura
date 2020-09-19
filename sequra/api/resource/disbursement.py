"""Logic of handling requests to obtain competitors from a business"""
import logging
from datetime import date

from flask import request, abort
from flask_restx import Resource
from marshmallow import Schema, fields
from marshmallow.validate import Length, Range

from sequra.api.restx import api
from sequra.database.models import Disbursement, Merchant

log = logging.getLogger(__name__)

ns = api.namespace('', description='Disbursement API')


class DisbursementQueryAsyncSchema(Schema):
    """Validations are done using marshmallow instead of argparse because argparse is deprecated"""
    merchant_name = fields.Str(required=True, validate=Length(1, 50))
    week = fields.Integer(required=True, validate=Range(min=1, min_inclusive=True, max=53, max_inclusive=True))
    year = fields.Integer(required=True, validate=Range(min=1980, max=3000))


class DisbursementQuerySchema(Schema):
    """Validations are done using marshmallow instead of argparse because argparse is deprecated"""
    merchant_name = fields.Str(required=False, validate=Length(1, 50))
    week = fields.Integer(required=True, validate=Range(min=1, min_inclusive=True, max=53, max_inclusive=True))
    year = fields.Integer(required=True, validate=Range(min=1980, max=3000))


@ns.route('/calculate_disbursement', doc={
    'description': 'Calculate and persist the disbursements per merchant on a given week and year asynchronously.'})
class AsyncBusiness(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Merchant not found')
    @api.doc(params={'year': {'required': True}})
    @api.doc(params={'week': {'required': True}})
    @api.doc(params={'merchant_name': {'description': 'Merchant\'s name', 'max_length': 50, 'required': True}})
    def get(self):
        errors = DisbursementQueryAsyncSchema().validate(request.args)
        if errors:
            abort(400, str(errors))
        merchant_name = request.args.get('merchant_name')
        year = int(request.args.get('year'))
        week = int(request.args.get('week'))

        if week > self.weeks_for_year(year):
            abort(400, f'Input week number {week} is grater that number of weeks of year {year} ')

        disbursement = Disbursement()
        merchant = Merchant.query.filter(Merchant.name == merchant_name).one()
        disbursement.save(week=week, year=year, merchant=merchant)

        return disbursement.id, 201

    @staticmethod
    def weeks_for_year(year):
        last_week = date(year, 12, 28)
        return last_week.isocalendar()[1]


@ns.route('/disbursement', doc={'description': 'Disbursements for a given merchant on a given week. '
                                               'If no merchant is provided return for all of them.'})
@api.response(200, 'Success')
class GetBusiness(Resource):
    @api.doc(params={'year': {'required': True}})
    @api.doc(params={'week': {'required': True}})
    @api.doc(params={'merchant_name': {'description': 'Merchant\'s name', 'max_length': 50, 'required': False}})
    def get(self):
        errors = DisbursementQuerySchema().validate(request.args)
        if errors:
            abort(400, str(errors))
        merchant_name = request.args.get('merchant_name')
        year = request.args.get('year')
        week = request.args.get('week')
        if not merchant_name:
            disbursements = Disbursement.query.join(Merchant, Merchant.id == Disbursement.merchant_id).filter(
                Disbursement.week == week,
                Disbursement.year == year).all()
            return [dis.asdict() for dis in disbursements]

        if not Merchant.query.filter(Merchant.name == merchant_name).scalar():
            return []

        dis = Disbursement.query.join(Merchant, Disbursement.merchant).filter(
            Merchant.name == merchant_name,
            Disbursement.week == week,
            Disbursement.year == year).one()
        return dis.asdict()
