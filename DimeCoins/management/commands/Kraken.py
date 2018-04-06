from DimeCoins.models.base import Xchange, Currency
from django.core.management.base import BaseCommand
import krakenex
import logging
from django.core.exceptions import ObjectDoesNotExist
from DimeCoins.settings.base import XCHANGE
from DimeCoins.classes import Coins


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )


class Command(BaseCommand):
    def handle(self, *args, **options):

        self.xchange = Xchange.objects.get(pk=XCHANGE['KRAKEN'])
        try:
            self.kraken = krakenex.API()
        except ObjectDoesNotExist as error:
            logging.debug('Client does not exist:{0}'.format( error))
        self.comparison_currency = 'USD'

        xchange_coins = self.getCoins()
        for xchange_coin in xchange_coins:
            try:
                currency = Currency.objects.get(symbol=xchange_coins[xchange_coin]['altname'])
                print(xchange_coins[xchange_coin]['altname'] + " exists")
            except ObjectDoesNotExist as error:
                print(xchange_coins[xchange_coin]['altname'] + " does not exist in our currency list..adding")
                currency = Currency()

            prices = self.getPrice(currency.symbol)
            if prices != 0:
                for price in prices:
                    coins = Coins.Coins(currency.symbol)
                    coin = coins.getRecord(time=int(price[0]), xchange=self.xchange)
                    coin.time = int(price[0])
                    coin.open = float(price[1])
                    coin.close = float(price[4])
                    coin.high = float(price[2])
                    coin.low = float(price[3])
                    coin.volume = float(price[6])
                    coin.xchange = self.xchange
                    coin.currency = currency
                    coin.save()

    def getPrice(self, currency_symbol):
        try:
            pair = 'X' + currency_symbol + 'Z' + self.comparison_currency
            res = self.kraken.query_public('OHLC', data= {'pair': pair, 'interval': 1440 })
            return res['result'][pair]
        except:
           return 0

    def getCoins(self):
        try:
            res = self.kraken.query_public('Assets')
            return res['result']
        except:
           return 0

    def __date_to_iso8601(self, date_time):
        return '{year}-{month:02d}-{day:02d}'.format(
            year=date_time.tm_year,
            month=date_time.tm_mon,
            day=date_time.tm_mday)
