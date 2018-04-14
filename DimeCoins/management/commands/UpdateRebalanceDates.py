from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from DimeCoins.settings.base import XCHANGE, FUND_PERIOD
from DimeCoins.models.base import Xchange
from datetime import datetime
from django.apps import apps
from dateutil.relativedelta import relativedelta
import logging
import datetime


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-2s) %(message)s',)
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--fund', dest='fund_id', required=False, help='Fund ID', type=int)
        parser.add_argument('--xchange', dest='xchange_id', required=False, help='Xchange ID', type=int)

    def handle(self, *args, **options):

        xchange = Xchange.objects.get(pk=XCHANGE['COIN_MARKET_CAP'])
        funds = None

        if options['xchange_id']:
            xchange_id = options['xchange_id']
            try:
                xchange = Xchange.objects.get(pk=xchange_id)
            except ObjectDoesNotExist as error:
                logger.error("Xchange does not exist:(0} {1}".format(xchange_id, error))
                return

        try:
            fund_model = apps.get_model(app_label='DimeAPI', model_name='Fund')
        except Exception as error:
            logger.error("Failed getting Fund Model: (0}".format(error))
            return

        if options['fund_id']:
            try:
                funds = fund_model.objects.using('DimeAPI').get(pk=options['fund_id'])
            except ObjectDoesNotExist as error:
                logger.info("Fund: {0} Not Found.".format(options['fund_id']))
                return
        else:
            funds = fund_model.objects.using('DimeAPI').filter(active=1)
            logger.info("{0} Fund(s) Found.".format(len(funds)))

        try:
            fundRebalanceDate_model = apps.get_model(app_label='DimeAPI', model_name='FundRebalanceDate')
        except Exception as error:
            logger.error("Failed getting fund Rebalance Date Model: {0}".format(error))
            return

        for fund in funds:
            try:
                fundRebalanceDates = fundRebalanceDate_model.objects.using('DimeAPI').filter(fund=fund).order_by('-start_date')
                logger.info("{0} Fund Rebalance Dates Found.".format(len(fundRebalanceDates)))
            except Exception as error:
                logger.error("Failed getting Fund Rebalance Dates: {0}:{1}".format(fund.pk, error))
                return

            for fundRebalanceDate in fundRebalanceDates:
                if datetime.datetime.utcnow().date() >= fundRebalanceDate.end_date and datetime.datetime.utcnow().date() > fundRebalanceDate.start_date:
                    self.addRebalanceDate(fund, fundRebalanceDate, fundRebalanceDate_model)
                return

    def addRebalanceDate(self, fund, fundRebalanceDate, fundRebalanceDate_model):

        fund_period_model = apps.get_model(app_label='DimeAPI', model_name='FundPeriod')
        rebalance_frequency = fundRebalanceDate.frequency
        rebalance_period = fund_period_model.objects.using('DimeAPI').get(pk=fundRebalanceDate.period.pk)  # week
        start_date = fundRebalanceDate.end_date + relativedelta(days=+1)

        while start_date <= datetime.datetime.utcnow().date():

            try:
                fund_rebalance_date = fundRebalanceDate_model.objects.using('DimeAPI').get(
                    start_date=start_date, fund=fund)
                logger.info("Start Date {0} Exists for fund {1}: Updating".format(start_date, fund.name))
            except ObjectDoesNotExist as error:
                fund_rebalance_date = fundRebalanceDate_model()
                fund_rebalance_date.start_date = start_date
                logger.info("Start Date {0} Not Found for fund {1}: Creating: {2}".format(start_date, fund.name, error))

            if rebalance_period.pk == FUND_PERIOD['DAY']:
                fund_rebalance_date.end_date = start_date + relativedelta(days=+rebalance_frequency)
            if rebalance_period.pk == FUND_PERIOD['WEEK']:
                fund_rebalance_date.end_date = start_date + relativedelta(weeks=+rebalance_frequency)
            if rebalance_period.pk == FUND_PERIOD['MONTH']:
                fund_rebalance_date.end_date = start_date + relativedelta(months=+rebalance_frequency)
            if rebalance_period.pk == FUND_PERIOD['QUARTER']:
                fund_rebalance_date.end_date = start_date + relativedelta(months=+(rebalance_frequency * 3))
            if rebalance_period.pk == FUND_PERIOD['YEAR']:
                fund_rebalance_date.end_date = start_date + relativedelta(years=+rebalance_frequency)

            fund_rebalance_date.num_of_coins = fundRebalanceDate.num_of_coins
            fund_rebalance_date.period = fundRebalanceDate.period
            fund_rebalance_date.frequency = fundRebalanceDate.frequency
            fund_rebalance_date.fund = fund
            fund_rebalance_date.save(using='DimeAPI')

            logger.info("Created Rebalance Entry")
            start_date = fund_rebalance_date.end_date + relativedelta(days=+1)
