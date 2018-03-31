from DimeCoins.models.base import Xchange, Currency
from DimeCoins.classes import Coins
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from DimeCoins.settings.base import XCHANGE, PROJECT_NAME
from datetime import datetime, timedelta
import time
import json
import logging
import requests


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )

class Command(BaseCommand):
    xchange = Xchange.objects.get(pk=XCHANGE['COIN_API'])
    comparison_currency = 'USD'

    def handle_noargs(self, **options):
        pass

    def handle(self, *args, **options):

        exchanges = json.loads(self.getExchanges())

        for exchange in exchanges:
            try:
                xchange = Xchange.objects.get(name=exchange['name'])
            except ObjectDoesNotExist as error:
                xchange = Xchange()
            xchange.url = exchange['website']
            xchange.name = exchange['name']
            xchange.number_symbols = exchange['data_symbols_count']
            xchange.start_date = int(time.mktime(datetime.strptime(exchange['data_start'], '%Y-%m-%d').timetuple()))
            xchange.end_date = int(time.mktime(datetime.strptime(exchange['data_end'], '%Y-%m-%d').timetuple()))
            xchange.symbols_count = exchange['data_symbols_count']
            xchange.save()

        xchange_coins = json.loads(self.getCoins())
        idx = 0
        for xchange_coin in xchange_coins:
            try:
                currency = Currency.objects.get(symbol=xchange_coin['asset_id_base'])
                print(xchange_coin['asset_id_base'] + " exists")
            except ObjectDoesNotExist as error:
                print(xchange_coin['asset_id_base'] + " does not exist in our currency list")
                continue

            now = datetime.now()
            end_date = now.replace(second=0, minute=0, hour=0)
            start_date = end_date - timedelta(days=2)
            while end_date > start_date:

                prices = self.getPrice(xchange_coin['symbol_id'], start_date=start_date, end_date=end_date)
                coins = Coins.Coins()
                print(prices)
                if len(prices) > 0:
                    print(prices)
                    for price in prices:
                        coin = coins.get_coin_type(symbol=currency.symbol, time=int(time.mktime(start_date.timetuple())), exchange=self.xchange)
                        coin.time = int(time.mktime(start_date.timetuple()))
                        coin.open = float(price['price_open'])
                        coin.close = float(price['price_close'])
                        coin.high = float(price['price_high'])
                        coin.low = float(price['price_low'])
                        coin.xchange = self.xchange
                        coin.currency = currency
                        coin.save()
                start_date = start_date + timedelta(days=1)

            idx = idx + 1
            if idx > 5:
                return

    @staticmethod
    def __date_to_iso8601(date_time):
        return '{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}'.format(
            year=date_time.year,
            month=date_time.month,
            day=date_time.day,
            hour=date_time.hour,
            minute=date_time.minute,
            second=date_time.second)

    def getPrice(self, currency_symbol, start_date, end_date, limit=300, period_id='1DAY'):
        headers = {'content-type': 'application/json',
                   'user-agent': 'your-own-user-agent/0.0.1',
                   'X-CoinAPI-Key': self.xchange.api_key}
        params = {
                  'period_id': period_id,
                  'time_start': start_date,
                  'limit': limit,
                  'time_end': end_date}
        spot_price = requests.get(self.xchange.api_url + '/ohlcv/' + currency_symbol + '/history', params=params, headers=headers)
        #spot_price = requests.get(self.xchange.api_url + '/ohlcv/BITSTAMP_SPOT_BTC_USD/history', params=params, headers=headers)

        if spot_price.status_code == requests.codes.ok:
            return spot_price.json()
        else:
            return([])

    def getExchanges(self):
        headers = {'content-type': 'application/json',
                   'user-agent': 'your-own-user-agent/0.0.1',
                   'X-CoinAPI-Key': self.xchange.api_key}
        params = {}
        exchanges = requests.get(self.xchange.api_url + '/exchanges', params=params, headers=headers)
        return exchanges.text

    def getCoins(self):
        headers = {'content-type': 'application/json',
                   'user-agent': 'your-own-user-agent/0.0.1',
                   'X-CoinAPI-Key': self.xchange.api_key}
        params = {}
        assets = requests.get(self.xchange.api_url + '/symbols', params=params, headers=headers)
        return assets.text