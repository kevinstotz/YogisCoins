from DimeCoins.models.base import Xchange, Currency
from DimeCoins.settings.base import XCHANGE
from DimeCoins.classes import Coins
from django.core.exceptions import ObjectDoesNotExist
import calendar
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import logging
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )


class Command(BaseCommand):

    xchange = Xchange.objects.get(pk=XCHANGE['CRYPTO_COMPARE'])
    comparison_currency = 'USD'
    coin_list_url = 'https://min-api.cryptocompare.com/data/all/coinlist'
    history = '/histoday?fsym=BTC&tsym=USD&limit=60&aggregate=1&toTs=1452680400'

    def handle(self, *args, **options):

        xchange_coins = self.getCoins()
        for xchange_coin in xchange_coins:
            if xchange_coin is None:
                continue
            coins = Coins.Coins(xchange_coins[xchange_coin]['Symbol'])
            try:
                currency = Currency.objects.get(symbol=xchange_coins[xchange_coin]['Symbol'])
                logger.info("{0} exists".format(xchange_coins[xchange_coin]['Symbol']))
            except ObjectDoesNotExist as error:
                logger.info("{0} does not exist in our currency list..Adding".format(xchange_coins[xchange_coin]['Symbol'], error))
                coins.createClass()

            now = datetime.now()
            start_date = now.replace(second=0, minute=0, hour=0)
            end_date = start_date - timedelta(days=300)

            while end_date < start_date:
                start_date_ts = calendar.timegm(start_date.timetuple())
                prices = self.getPrice(currency.symbol.replace('*', ''), start_date_ts)

                if len(prices) > 0:
                    for price in prices:
                        if prices[price] == 'Error':
                            break
                        coin = coins.getRecord(time=start_date_ts, xchange=self.xchange)
                        coin.time = start_date_ts
                        coin.close = float(prices[price]['USD'])
                        coin.xchange = self.xchange
                        coin.currency = currency
                        coin.save()
                start_date = start_date - timedelta(days=1)

        return 0

    def getPrice(self, currency_symbol, start_date):
        url = '{0}/pricehistorical?fsym={1}&tsyms={2}&ts={3}'.format(self.xchange.api_url,
                                                                     currency_symbol,
                                                                     self.comparison_currency,
                                                                     start_date)
        spot_price = requests.get(url)

        if spot_price.status_code == 200:
            return spot_price.json()
        else:
            return {}

    def getCoins(self):
        headers = {'content-type': 'application/json',
                   'user-agent': 'your-own-user-agent/0.0.1'}
        params = {}
        currencies = requests.get(self.coin_list_url, params=params, headers=headers)
        return currencies.json()['Data']

    def getCoinSnapShot(self, currency_symbol):
        url = '{0}/coinsnapshot?fsym={1}&tsym={2}'.format(self.xchange.api_url,
                                                          currency_symbol,
                                                          self.comparison_currency)
        snap_shot_reponse = requests.get(url)
        return snap_shot_reponse.json()

    def getCoinMarketCap(self, currency_symbol):
        coin_snap_shot = self.getCoinSnapShot(currency_symbol)
        return coin_snap_shot.Data.TotalCoinsMined
