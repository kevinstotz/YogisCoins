from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from DimeCoins.settings.base import XCHANGE, FUND_PERIOD
from DimeCoins.models.base import TopCoins, Xchange, Currency
from datetime import datetime
import calendar
from dateutil.relativedelta import relativedelta
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates a Fund.  Defaults to 1 year ago start date, else YYYY-MM-DD   Top 10 coins based on market cap'
    rebalance_price = dict()
    level = 0

    def add_arguments(self, parser):
        parser.add_argument('--coins',
                            dest='specific_coins',
                            nargs='+',
                            required=False,
                            help='Specific Coins to include',
                            type=int)
        parser.add_argument('--frequency',
                            dest='rebalance_frequency',
                            required=False,
                            help='Rebalance Frequency 1 5 7 30 365',
                            type=int)
        parser.add_argument('--value',
                            dest='value_of_fund',
                            required=False,
                            help="Inital value of Fund",
                            type=int)
        parser.add_argument('--start',
                            dest='start_date',
                            required=False,
                            help='Fund Start Date. Default: 12 months ago',
                            type=str)
        parser.add_argument('--period',
                            dest='rebalance_period',
                            required=False,
                            help='Rebalance period {"DAY", "WEEK", "MONTH", "QUARTER", "YEAR"}',
                            type=str)
        parser.add_argument('--name',
                            dest='fund_name',
                            required=True,
                            help="Name of Fund",
                            type=str)
        parser.add_argument('--number',
                            dest='number_of_currencies',
                            required=True,
                            help="Number of Coins",
                            type=int)

    def handle(self, *args, **options):
        fund_period_model = apps.get_model(app_label='DimeAPI', model_name='FundPeriod')
        rebalance_frequency = 1
        value_of_fund = self.level = 10
        rebalance_period = fund_period_model.objects.using('DimeAPI').get(pk=FUND_PERIOD['MONTH'])  # week
        fund_name = options['fund_name']
        number_of_currencies = options['number_of_currencies']

        if options['rebalance_frequency']:
            rebalance_frequency = options['rebalance_frequency']

        if options['value_of_fund']:
            value_of_fund = options['value_of_fund']
            self.level = value_of_fund
        if options['rebalance_period']:
            try:
                rebalance_period = fund_period_model.objects.using('DimeAPI').get(period=options['rebalance_period'])
            except Exception as error:
                logger.error("Period:{0} should be: DAY, WEEK, QUARTER, MONTH, YEAR: {1}".format(options['rebalance_period'], error))
                return

        if options['start_date']:
            try:
                start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
            except Exception as error:
                logger.error("Invalid Date:{0} :{1}".format(options['start_date'], error))
                return
        else:
            start_date = datetime.utcnow().date() + relativedelta(years=-1)
        self.createFund(fund_name, number_of_currencies, start_date, rebalance_period, rebalance_frequency)

    def createFund(self, fund_name, number_of_currencies, start_date, rebalance_period, rebalance_frequency):
        fund = None
        fund_rebalance_date_model = None
        fund_model = None
        xchange = Xchange.objects.get(pk=XCHANGE['COIN_MARKET_CAP'])
        try:
            fund_model = apps.get_model(app_label='DimeAPI', model_name='Fund')
        except Exception as error:
            logger.error("Failed getting fund model: {0} : {1}".format('Fund', error))

        try:
            fund = fund_model.objects.using('DimeAPI').get(name=fund_name)
            logger.info("fund with that name exists: {0}.  Continuing".format(fund.name))
        except ObjectDoesNotExist:
            fund = fund_model(name=fund_name)
            fund.save(using='DimeAPI')
            logger.info("Created Fund: {0}".format(fund_name))

        while start_date <= datetime.utcnow().date():

            try:
                fund_rebalance_date_model = apps.get_model(app_label='DimeAPI', model_name='fundrebalancedate')
            except Exception as error:
                logger.error("Failed getting fund Rebalance Date Model: {0}: {1}".format('fundrebalancedate', error))
                return

            try:
                fund_rebalance_date = fund_rebalance_date_model.objects.using('DimeAPI').get(start_date=start_date, fund=fund)
                logger.info("Start Date {0} Exists for fund {1}: Continuing".format(fund_rebalance_date.start_date, fund.name))

            except ObjectDoesNotExist:
                fund_rebalance_date = fund_rebalance_date_model()
                fund_rebalance_date.start_date = start_date
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
                fund_rebalance_date.end_date = fund_rebalance_date.end_date + relativedelta(days=-1)
                fund_rebalance_date.num_of_coins = number_of_currencies
                fund_rebalance_date.period = rebalance_period
                fund_rebalance_date.frequency = rebalance_frequency
                fund_rebalance_date.fund_id = fund.pk
                fund_rebalance_date.save(using='DimeAPI')

                logger.info("Created Rebalance Entry")

            try:
                top_currencies = TopCoins.objects.filter(time=int(calendar.timegm(start_date.timetuple()))).filter(
                    xchange=xchange).order_by('-market_cap')[:number_of_currencies]
                if len(top_currencies) != number_of_currencies:
                    raise Exception
            except Exception as error:
                logger.error("Failed getting {0} top coins.  Received: {1} : error:{2} ".format(number_of_currencies, str(len(top_currencies)), error))
                return

            market_cap_sum = 0
            level = self.level
            self.level = 0
            for index in range(0, 2):
                rank = 1

                for top_currency in top_currencies:
                    try:
                        top_currency = Currency.objects.get(pk=top_currency.currency.pk)
                        currency_model = apps.get_model("DimeCoins", str(top_currency.symbol).lower())
                        if fund_rebalance_date.end_date > datetime.utcnow().date():
                            end_d = datetime.utcnow().date() + relativedelta(days=-1)
                            end_currency = currency_model.objects.get(xchange=xchange, time=int(
                                calendar.timegm(end_d.timetuple())))
                        else:
                            end_currency = currency_model.objects.get(xchange=xchange, time=int(calendar.timegm(fund_rebalance_date.end_date.timetuple())))
                        start_currency = currency_model.objects.get(xchange=xchange, time=int(calendar.timegm(fund_rebalance_date.start_date.timetuple())))
                    except ObjectDoesNotExist as error:
                        logger.error("Failed getting Currency: {0}: End Date:{1}: error:{2}".format(top_currency.pk, int(calendar.timegm(fund_rebalance_date.end_date.timetuple())), error))
                        return
                    except Exception as error:
                        logger.error("Symbol: {0}: time: {1} error:{2}".format(top_currency.symbol, calendar.timegm(
                            fund_rebalance_date.end_date.timetuple()), error))
                        return

                    try:
                        fund_currency_model = apps.get_model(app_label='DimeAPI', model_name='FundCurrency')
                    except Exception as error:
                        logger.error("Failed getting fund Currency Model:{0} error: {1}".format('FundCurrency', error))

                    if index == 0:
                        market_cap_sum = market_cap_sum + start_currency.market_cap
                    else:
                        try:
                            fund_currency = fund_currency_model.objects.using('DimeAPI').get(
                                rebalance=fund_rebalance_date, fund=fund, currency=top_currency.pk)
                            logger.info("Found fund {0} with rebalance start date: {1}. Updating results".format(fund.name,
                                                                                                                 fund_rebalance_date.start_date))
                        except ObjectDoesNotExist:
                            fund_currency = fund_currency_model()
                            logger.info("Creating currency id:{0}, rebalance Date:{0}".format(top_currency.pk, fund_rebalance_date.pk))
                        self.addCurrency(start_currency, end_currency, fund_currency, fund_rebalance_date, fund, rank, level, market_cap_sum, top_currency)
                        rank = rank + 1

            start_date = fund_rebalance_date.end_date + relativedelta(days=+1)

    def addCurrency(self, start_currency, end_currency, fund_currency, fund_rebalance_date, fund, rank, level, market_cap_sum, top_currency):
        try:
            fund_currency.level = level
            fund_currency.currency = top_currency.pk
            fund_currency.rebalance_price = start_currency.open
            fund_currency.market_cap = start_currency.market_cap
            fund_currency.percent = start_currency.market_cap / market_cap_sum * 100.0
            fund_currency.amount = (fund_currency.percent / 100.0 * level) / start_currency.open
            fund_currency.rebalance_value = start_currency.open * fund_currency.amount
            fund_currency.rebalance = fund_rebalance_date
            fund_currency.end_price = end_currency.close
            fund_currency.end_value = end_currency.close * fund_currency.amount
            fund_currency.rank = rank
            fund_currency.fund = fund
            fund_currency.save(using='DimeAPI')
            self.rebalance_price[fund_currency.pk] = fund_currency.end_price
            self.level = self.level + fund_currency.end_value
        except Exception as error:
            logger.error(error)
            logger.error("level: {0}".format(level))
            logger.error("top_currency pk: {0}".format(top_currency.pk))
            logger.error("start_currency open: {0}".format(start_currency.open))
            logger.error("start_currency market_cap: {0}".format(start_currency.market_cap))
            logger.error("percent: {0}".format(start_currency.market_cap / market_cap_sum * 100.0))
            logger.error("amount: {0}".format((fund_currency.percent / 100.0 * level) / start_currency.open))
            logger.error("value: {0}".format(start_currency.open * fund_currency.amount))
            logger.error("rebalance date: {0}".format(fund_rebalance_date))
            logger.error("close price: {0}".format(end_currency.close))
            logger.error("end value: {0}".format(end_currency.close * fund_currency.amount))
            logger.error("rank: {0}".format(rank))
            logger.error("fund: {0}".format(fund.name))
