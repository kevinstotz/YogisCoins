from DimeCoins.models.base import Xchange, Currency
from DimeCoins.classes import Coins
import requests
from django.core.management.base import BaseCommand
from DimeCoins.settings.base import XCHANGE
from datetime import datetime, timedelta
import logging
import time


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-2s) %(message)s',)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        #  instance variable unique to each instance
        self.xchange = Xchange.objects.get(pk=XCHANGE['COINDESK'])
        self.comparison_currency = 'USD'

        start_date = datetime.date(datetime.utcnow())
        end_date = start_date - timedelta(days=600)

        currency = Currency()
        prices = self.getPrice(currency.symbol, end_date=start_date, start_date=end_date)
        coins = Coins.Coins()
        if prices == 0 or prices == 'NoneType' or prices == []:
            logger.info(currency.symbol + "Not found")


        for key in prices['bpi']:
            coin = coins.get_coin_type(symbol=currency.symbol, time=int(time.mktime(start_date.timetuple())), exchange=self.xchange)
            coin.time = int(time.mktime(start_date.timetuple()))
            coin.close = prices['bpi'][key]
            coin.xchange = self.xchange
            coin.currency = currency
            coin.save()
     #   start_date = start_date - timedelta(days=1)

    def getPrice(self, currency_symbol, start_date=datetime.utcnow(), end_date=datetime.utcnow(), granularity=86400):

        headers = {'content-type': 'application/json','user-agent': 'your-own-user-agent/0.0.1'}
        params = {
                  'index': self.comparison_currency,
                  'currency': currency_symbol,
                  'start': start_date,
                  'end': end_date}

        spot_price = requests.get(self.xchange.api_url + '/bpi/historical/close.json', params=params, headers=headers)
        if spot_price.status_code == requests.codes.ok:
            return spot_price.json()
        else:
            return([])
