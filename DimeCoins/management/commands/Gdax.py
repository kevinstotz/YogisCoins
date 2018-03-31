from DimeCoins.models.base import Xchange, Currency
from DimeCoins.classes import Coins, SymbolName
import requests
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from DimeCoins.settings.base import XCHANGE
from datetime import datetime, timedelta
import logging
import json
from time import sleep

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )


class Command(BaseCommand):
    xchange = Xchange.objects.get(pk=XCHANGE['GDAX'])
    comparison_currency = 'USD'
    granularity = 86400
    coin_list_url = 'https://api.gdax.com/currencies'

    def handle(self, *args, **options):
        #  instance variable unique to each instance
        xchange_coins = json.loads(self.getCoins())

        for xchange_coin in xchange_coins:
            if xchange_coin['id'] in ['USD', 'EUR', 'GBP']:
                continue
            try:
                currency = Currency.objects.get(symbol=xchange_coin['id'])
                print(xchange_coin['id'] + " exists")
            except ObjectDoesNotExist as error:
                print(xchange_coin['id'] + " does not exist in our currency list..adding" + error)
                currency = Currency()
                symbol = SymbolName.SymbolName(xchange_coin['id'])
                currency.symbol = symbol.parse_symbol()
                try:
                    currency.save()
                    currency = Currency.objects.get(symbol=symbol)
                    print("added")
                except:
                    print("failed adding {0}".format(xchange_coin['id']))
                    continue

            now = datetime.now()
            start_date = now.replace(second=0, minute=0, hour=0)
            end_date = start_date - timedelta(days=7)

            while end_date < start_date:
                sleep(2)
                prices = self.getPrice(currency.symbol,
                                       start_date=self.__date_to_iso8601(date_time=(start_date - timedelta(days=1)).timetuple()),
                                       end_date=self.__date_to_iso8601(date_time=start_date.timetuple()),
                                       granularity=86400)
                coins = Coins.Coins()
                if len(prices) > 0:
                    for price in prices:
                        coin = coins.get_coin_type(symbol=currency.symbol, time=int(price[0]), exchange=self.xchange)
                        coin.time = int(price[0])
                        coin.low = float(price[1])
                        coin.high = float(price[2])
                        coin.open = float(price[3])
                        coin.close = float(price[4])
                        coin.xchange = self.xchange
                        coin.currency = currency
                        coin.save()

                start_date = start_date - timedelta(days=1)

    def getPrice(self, currency_symbol, start_date, end_date, granularity=86400):
        headers = {'content-type': 'application/json', 'user-agent': 'your-own-user-agent/0.0.1'}
        spot_price = requests.get(self.xchange.api_url + '/products/' + currency_symbol + '-' +
                                  self.comparison_currency + '/candles?granularity={0}&start={1}&end={2}'.format(granularity, start_date, end_date), headers=headers)
        if spot_price.status_code == requests.codes.ok:
            return spot_price.json()
        else:
            return []

    def getCoins(self):
        headers = {'content-type': 'application/json',
                   'user-agent': 'your-own-user-agent/0.0.1'}
        params = {}
        currencies = requests.get(self.coin_list_url, params=params, headers=headers)
        return currencies.text

    @staticmethod
    def __date_to_iso8601(date_time):
        return '{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}'.format(
            year=date_time.tm_year,
            month=date_time.tm_mon,
            day=date_time.tm_mday,
            hour=date_time.tm_hour,
            minute=date_time.tm_min,
            second=date_time.tm_sec)
