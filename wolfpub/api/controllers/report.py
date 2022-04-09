"""
To handle the Distributor and its account
"""

from datetime import datetime, timedelta

from flask import request
from flask_restplus import Resource

from wolfpub.api.handlers.account import AccountBillHandler
from wolfpub.api.handlers.distributor import DistributorHandler
from wolfpub.api.handlers.report import ReportHandler
from wolfpub.api.models.serializers import REVENUE_REPORT_ARGUMENTS, SALARY_REPORT_ARGUMENTS, \
    TIME_PERIOD_REPORT_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('reports', description='Route admin for report actions.')

mariadb = MariaDBConnector()
distributor_handler = DistributorHandler(mariadb)
report_handler = ReportHandler(mariadb)
account_bill_handler = AccountBillHandler(mariadb)


@ns.route("/monthly")
class MonthlyReport(Resource):
    """
    Focuses on monthly report of WolfPubDB.
    """

    def get(self):
        """
        End-point to get the monthly report of revenue and expenditure
        """
        try:
            today = datetime.today()
            yesterday = today - timedelta(days=1)
            start_date = yesterday.replace(day=1).strftime("%Y-%m-%d")
            end_date = today.strftime('%Y-%m-%d')
            output = {}
            output['total_revenue'] = report_handler.get_revenue(start_date, end_date)
            output['total_expense'] = report_handler.get_salary_expense(start_date, end_date)
            output['total_expense'].update(report_handler.get_shipping_cost_expense(start_date, end_date))
            return CustomResponse(data=output)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/revenue")
class RevenueReport(Resource):
    """
    Focuses on revenue report of WolfPubDB.
    """

    @ns.expect(TIME_PERIOD_REPORT_ARGUMENTS, REVENUE_REPORT_ARGUMENTS, validate=True)
    def get(self):
        """
        End-point to get the report of revenue per_distributor or per_city or per_location
        """
        try:
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)
            stats = request.args.get('stats', 'total')
            output = {stat.strip(): {} for stat in stats.split(',')}
            if 'total' in output:
                output['total'] = report_handler.get_revenue(start_date, end_date)
            if 'distributor_wise' in output:
                output['distributor_wise'] = report_handler.get_revenue_per_distributor(start_date, end_date)
            if 'city_wise' in output:
                output['city_wise'] = report_handler.get_revenue_per_city(start_date, end_date)
            if 'location_wise' in output:
                output['location_wise'] = report_handler.get_revenue_per_location(start_date, end_date)
            return CustomResponse(data={'revenue': output})
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/distributors/active/count")
class DistributorReport(Resource):
    """
    Focuses on active distributor's count of WolfPubDB.
    """

    def get(self):
        """
        End-point to get the report of active distributor
        """
        try:
            count = report_handler.get_active_distributor_count()
            return CustomResponse(data=count)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/salary-payment")
class SalaryReport(Resource):
    """
    Focuses on report for salary paid by WolfPubDB to employees.
    """

    @ns.expect(SALARY_REPORT_ARGUMENTS, validate=True)
    def get(self):
        """
        End-point to get the report of revenue and expenditure
        """
        try:
            stats = request.args.get('stats', 'total')
            output = {stat.strip(): {} for stat in stats.split(',')}
            if 'total' in output:
                output = report_handler.get_salary_expense()
            elif 'per_month' in output and 'per_work_type' in output:
                output = report_handler.get_salary_expense_per_month_per_worktype()
            elif 'per_month' in output:
                output = report_handler.get_salary_expense_per_month()
            elif 'per_work_type' in output:
                output = report_handler.get_salary_expense_per_worktype()
            return CustomResponse(data=output)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
