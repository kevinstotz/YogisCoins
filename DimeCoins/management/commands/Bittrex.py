from bittrex_v2 import Bittrex as Bittrex_mod, BittrexError
from django.core.exceptions import ObjectDoesNotExist
from DimeCoins.models.base import Xchange, Currency
from django.core.management.base import BaseCommand
from DimeCoins.settings.base import XCHANGE
from datetime import datetime
import logging
from decimal import Decimal
from DimeCoins.classes import Coins


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-2s) %(message)s')


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.valid_periods = ("oneMin", "fiveMin", "thirtyMin", "hour", "day")
        self.SHOW_ENDPOINTS = False
        self.TIMEOUT = 30
        self.comparison_currency = 'USD'
        self.xchange = Xchange.objects.get(pk=XCHANGE['BITTREX'])

        try:
            self.bittrex = Bittrex_mod(api_key=self.xchange.api_key,
                                       api_secret=self.xchange.api_secret,
                                       timeout=self.TIMEOUT,
                                       debug_endpoint=self.SHOW_ENDPOINTS,
                                       parse_float=Decimal)
        except ObjectDoesNotExist as error:
            logging.debug('Client does not exist:{0}'.format(error))

        xchange_coins = self.getCoins()

        for xchange_coin in xchange_coins['result']:
            coins = Coins.Coins(xchange_coin['Currency'])
            try:
                currency = Currency.objects.get(symbol=xchange_coin['Currency'])
                logger.info("{0} exists".format(xchange_coin['Currency']))
            except ObjectDoesNotExist as error:
                logger.info("{0} does not exist in our currency list..Adding".format(xchange_coin['Currency'], error))
                coins.createClass()

            prices = self.getPrice(currency.symbol)

            if prices == 0:
                continue

            if prices == {} or prices is None:
                logger.info(currency.symbol + " No prices found")
                continue

            for price in prices:
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
                # coin.save()
        return

    def getPrice(self, currency_symbol):
        try:
            res = self.bittrex.get_ticks(market='USDT-' + currency_symbol, period='day')
            return res['result']
        except:
           return 0

    def getCoins(self):
        return self.bittrex.get_currencies()