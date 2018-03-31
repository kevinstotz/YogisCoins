from DimeCoins.models.base import Xchange, Currency
from DimeCoins.classes import Coins
from django.core.exceptions import ObjectDoesNotExist
from DimeCoins.models.base import Xchange, Currency
from django.core.management.base import BaseCommand
from DimeCoins.settings.base import XCHANGE
from datetime import datetime, timedelta
import logging
import calendar
from DimeCoins.classes import Coins, SymbolName
import requests


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )


class Command(BaseCommand):
    coin_list_url = 'https://poloniex.com/public?command=returnCurrencies'
    comparison_currency = 'USD'
    xchange = Xchange.objects.get(pk=XCHANGE['POLONIEX'])

    def handle(self, *args, **options):

        exchange_coins = self.getCoins()
        for exchange_coin in exchange_coins:
            print(exchange_coin)
            try:
                currency = Currency.objects.get(symbol=exchange_coin)
                print(exchange_coin + " exists")
            except ObjectDoesNotExist as error:
                print(exchange_coin + " does not exist in our currency list..adding")
                currency = Currency()
                symbol = SymbolName.SymbolName(exchange_coin)
                currency.symbol = symbol.parse_symbol()
                try:
                    currency.save()
                    print("added")
                except:
                    print("failed adding {0}".format(exchange_coin))
                    continue

            now = datetime.now()
            start_date = now.replace(second=0, minute=0, hour=0)
            end_date = start_date - timedelta(days=5)
            start_date_ts = calendar.timegm(start_date.timetuple())
            prices = self.getPrice(currency.symbol, start_date_ts, 9999999999, 14400)
            coins = Coins.Coin()

            for price in prices:
                print(price)
                utc_dt = datetime.strptime(price['T'], '%Y-%m-%dT%H:%M:%S')
                timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds()
                coin = coins.get_coin_type(symbol=currency.symbol, time=int(timestamp), exchange=self.xchange)
                coin.time = int(timestamp)
                coin.open = float(price['O'])
                coin.close = float(price['C'])
                coin.high = float(price['H'])
                coin.low = float(price['L'])
                coin.volume = float(price['V'])
                coin.xchange = self.xchange
                coin.currency = currency
                #coin.save()
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

    def __date_to_iso8601(self, date_time):
        return '{year}-{month:02d}-{day:02d}'.format(
            year=date_time.tm_year,
            month=date_time.tm_mon,
            day=date_time.tm_mday)

    def getCoins(self):
        headers = {'content-type': 'application/json',
                   'user-agent': 'your-own-user-agent/0.0.1'}
        params = {}
        return requests.get(self.coin_list_url, params=params, headers=headers).json()