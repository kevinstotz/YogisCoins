from django.core.exceptions import ObjectDoesNotExist
from DimeCoins.models.base import Xchange, Currency
from django.core.management.base import BaseCommand
from DimeCoins.settings.base import XCHANGE
from datetime import datetime, timedelta
import logging
import calendar
from DimeCoins.classes import Coins
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )


class Command(BaseCommand):
    coin_list_url = 'https://poloniex.com/public?command=returnCurrencies'
    comparison_currency = 'USD'
    xchange = Xchange.objects.get(pk=XCHANGE['POLONIEX'])

    def handle(self, *args, **options):

        xchange_coins = self.getCoins()
        for xchange_coin in xchange_coins:
            coins = Coins.Coins(xchange_coin)
            try:
                currency = Currency.objects.get(symbol=xchange_coin)
                logger.info("{0} exists".format(xchange_coin))
            except ObjectDoesNotExist as error:
                logger.info("{0} does not exist in our currency list..Adding".format(xchange_coin, error))
                coins.createClass()

            start_date = datetime.now().replace(second=0, minute=0, hour=0) - timedelta(days=400)
            end_date = 9999999999
            start_date_ts = calendar.timegm(start_date.timetuple())
            prices = self.getPrice(currency.symbol, start_date_ts, end_date, 14400)

            for price in prices:
                if price == 'error':
                    logger.info("error getting prices")
                    continue
                utc_dt = datetime.strptime(price['T'], '%Y-%m-%dT%H:%M:%S')
                timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds()
                coin = coins.getRecord(time=timestamp, xchange=self.xchange)
                coin.time = int(timestamp)
                coin.open = float(price['O'])
                coin.close = float(price['C'])
                coin.high = float(price['H'])
                coin.low = float(price['L'])
                coin.volume = float(price['V'])
                coin.xchange = self.xchange
                coin.currency = currency
                coin.save()
        return

    def getPrice(self, currency_symbol, start_date, end_date, period):
        # /public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400
        headers = {'content-type': 'application/json', 'user-agent': 'your-own-user-agent/0.0.1'}
        spot_price = requests.get(self.xchange.api_url + 'public?command=returnChartData&currencyPair=' + currency_symbol + '_' +
                                  self.comparison_currency + '&period={0}&start={1}&end={2}'.format(period, start_date, end_date), headers=headers)
        if spot_price.status_code == requests.codes.ok:
            return spot_price.json()
        else:
            return []
        pass

    def getCoins(self):
        headers = {'content-type': 'application/json',
                   'user-agent': 'your-own-user-agent/0.0.1'}
        params = {}
        return requests.get(self.coin_list_url, params=params, headers=headers).json()