from DimeCoins.models.base import Xchange, Currency
from DimeCoins.classes import Coins
from coinbase.wallet.client import Client
import requests
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from DimeCoins.settings.base import XCHANGE
from datetime import datetime, timedelta
import logging
import json
import calendar


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-2s) %(message)s',)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    comparison_currency = 'USD'
    coin_list_url = 'https://api.coinbase.com/v2/currencies'
    api_version = '2018-02-14'
    xchange = Xchange.objects.get(pk=XCHANGE['COINBASE'])

    def handle(self, *args, **options):
        #  instance variable unique to each instance

        try:
            self.client = Client(self.xchange.api_key, self.xchange.api_secret, api_version='2018-01-14')
        except ObjectDoesNotExist as error:
            logging.debug('Client does not exist:{0}'.format( error))

        xchange_coins = self.client.get_currencies()

        for xchange_coin in xchange_coins['data']:
            if xchange_coin is None:
                continue
            coins = Coins.Coins(xchange_coin['id'])
            try:
                currency = Currency.objects.get(symbol=xchange_coin['id'])
                logger.info("{0} exists".format(xchange_coin['id']))
            except ObjectDoesNotExist as error:
                logger.info("{0} does not exist in our currency list..Adding".format(xchange_coin['id'], error))
                coins.createClass()

            now = datetime.now()
            start_date = now.replace(second=0, minute=0, hour=0)
            end_date = start_date - timedelta(days=10)

            while end_date < start_date:
                start_date_ts = calendar.timegm(start_date.timetuple())
                prices = self.getPrice(xchange_coin['id'], date=start_date.strftime('%Y-%m-%d'))
                if len(prices) != 0:
                    if prices is None:
                        break
                    coin = coins.getRecord(time=start_date_ts, xchange=self.xchange)
                    coin.time = int(calendar.timegm(start_date.timetuple()))
                    coin.close = float(prices['amount'])
                    coin.xchange = self.xchange
                    coin.currency = currency
                    coin.save()
                start_date = start_date - timedelta(days=1)

    def getCoins(self):
        headers = {'content-type': 'application/json',
                   'user-agent': 'your-own-user-agent/0.0.1'}
        params = {}
        currencies = requests.get(self.coin_list_url, params=params, headers=headers)
        return currencies.text

    def getPrice(self, currency_symbol, date):
        try:
            res = self.client.get_spot_price(currency_pair=currency_symbol + '-USD', date=date)
        except Exception as error:
            logger.error('{0}'.format(error))
            res = {}
        return res