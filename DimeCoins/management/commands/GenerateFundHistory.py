from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.base import BaseCommand
from DimeCoins.models.base import Xchange, Currency
from DimeCoins.settings.base import XCHANGE
from DimeCoins.classes.Coins import Coins
from datetime import datetime, timedelta
import calendar
import logging
from django.apps import apps


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',)
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--fund', dest='fund_id', required=True, help='Fund ID', type=int)
        parser.add_argument('--xchange', dest='xchange_id', required=False, help='Xchange ID', type=int)

    def handle(self, *args, **options):
        xchange = Xchange.objects.get(pk=XCHANGE['COIN_MARKET_CAP'])
        fundCurrencies = None
        fund = None
        fundRebalanceDates = None
        fundHistory_model = None
        fundRebalanceDate_model = None

        if options['xchange_id']:
            xchange_id = options['xchange_id']
            try:
                xchange = Xchange.objects.get(pk=xchange_id)
            except ObjectDoesNotExist as error:
                logger.error("Xchange does not exist:(0} {1}".format(xchange_id, error))
                return

        if options['fund_id']:
            fund_id = options['fund_id']
            try:
                fund_model = apps.get_model(app_label='DimeAPI', model_name='Fund')
            except Exception as error:
                logger.error("Failed getting Fund  Model: (0}".format(error))
                return

            try:
                fund = fund_model.objects.using('DimeAPI').get(pk=fund_id)
            except ObjectDoesNotExist as error:
                logger.error("No Fund Instance: {0}:{1}".format(fund_id, error))
            except Exception as error:
                logger.error("Failed getting Fund Instance: {0}:{1}".format(fund_id, error))
                return

            try:
                fundRebalanceDate_model = apps.get_model(app_label='DimeAPI', model_name='FundRebalanceDate')
            except Exception as error:
                logger.error("Failed getting fund Rebalance Date Model: {0}".format(error))
                return

            try:
                fundRebalanceDates = fundRebalanceDate_model.objects.using('DimeAPI').filter(fund=fund)
            except Exception as error:
                logger.error("Failed getting Fund Rebalance Dates: {0}:{1}".format(fund_id, error))
                return

            try:
                fundCurrency_model = apps.get_model(app_label='DimeAPI', model_name='FundCurrency')
            except Exception as error:
                logger.error("Failed getting Fund Currency Model: (0}".format(error))
                return


            try:
                fundHistory_model = apps.get_model(app_label='DimeAPI', model_name='FundHistory')
            except Exception as error:
                logger.error("Failed getting Fund History Model: {0}".format(error))
                return

        for fundRebalanceDate in fundRebalanceDates:
            start_date = fundRebalanceDate.start_date
            end_date = fundRebalanceDate.end_date

            if end_date > datetime.utcnow().date():
                end_date = datetime.utcnow().date()
            while start_date <= end_date:
                start_date_ts = int(calendar.timegm(start_date.timetuple()))
                try:
                    fundCurrencies = fundCurrency_model.objects.using('DimeAPI').filter(fund=fund, rebalance=fundRebalanceDate ).order_by('-rank')
                except Exception as error:
                    logger.error("Failed getting Fund Rebalance Dates: {0}:{1}".format(fundRebalanceDate, error))
                    return

                running_total = 0.0
                for fundCurrency in fundCurrencies:
                    try:
                        currency = Currency.objects.get(pk=fundCurrency.currency)
                        currency_obj = Coins(currency.symbol)
                        currency_instance = currency_obj.getRecord(start_date_ts, xchange)
                    except Exception as error:
                        logger.error("Failed getting Fund Currency ID: {0}:{1}".format(fundCurrency.currency, error))
                        return

                    running_total = running_total + float(fundCurrency.amount) * float(currency_instance.close)

                try:
                    fundHistory = fundHistory_model.objects.using('DimeAPI').get(time=start_date,
                                                                                 xchange__pk=xchange.pk,
                                                                                 fund=fund)
                    fundHistory.value = running_total
                    fundHistory.save()
                    logger.info("Record found for Fund History Instance:{0} exchange:{1}, updating ".format(
                        start_date_ts, xchange.pk))
                except ObjectDoesNotExist:
                    logger.info("No Record for Fund History Instance:{0} exchange:{1}, adding ".format(
                        start_date_ts, xchange.pk))
                    fundHistory = fundHistory_model(time=start_date,
                                                    xchange_id=xchange.pk,
                                                    fund=fund,
                                                    value=running_total)
                    fundHistory.save()

                except MultipleObjectsReturned:
                    logger.error("found multiple entries for: {0} exchange:{1} Fund:{2}".format(start_date_ts, xchange.pk, fund.pk))
                    return
                except TypeError as error:
                    logger.error("Time: {0} exchange:{1} Fund:{2}  value:{3} Error:{4}:".format(start_date_ts, xchange.pk, fund.pk, running_total, error))
                    return
                start_date = start_date + timedelta(days=1)
        return
