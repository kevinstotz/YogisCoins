from DimeCoins.models.base import Xchange, Currency
from DimeCoins.classes import Coins
from django.core.management.base import BaseCommand
import requests
from DimeCoins.settings.base import XCHANGE
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )

class Command(BaseCommand):
    def handle(self, *args, **options):

        self.xchange = Xchange.objects.get(pk=XCHANGE['CRYPTOINDEX'])
        self.comparison_currency = 'USD'
        self.symbol ='CRIX'

        prices = self.getPrice(self.symbol)
        if prices == 0:
            return 0
        coins = Coins.Coins()
        currency = Currency.objects.get(symbol=self.symbol)
        for price in prices:
            utc_dt = datetime.strptime(price['date'], '%Y-%M-%d')
            timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds()
            coin = coins.get_coin_type(symbol=self.symbol, time=int(timestamp), exchange=self.xchange)
            coin.time = int(timestamp)
            coin.close = float(price['price'])
            coin.xchange = self.xchange
            coin.currency = currency
            coin.save()
        return 0

    def getPrice(self, currency_symbol, start_date=datetime.utcnow(), end_date=datetime.utcnow(), granularity=86400):
        headers = {'content-type': 'application/json','user-agent': 'your-own-user-agent/0.0.1'}
        params = {}

        spot_price = requests.get(self.xchange.api_url + 'crix.json', params=params, headers=headers)
        if spot_price.status_code == requests.codes.ok:
            return spot_price.json()
        else:
            return([])