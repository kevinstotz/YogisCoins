from DimeCoins.models.base import Xchange, Currency, TopCoins
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from DimeCoins.classes import Coins
from DimeCoins.settings.base import XCHANGE
from datetime import datetime, timedelta
import datetime
import logging
import requests
import calendar
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-2s) %(message)s')


class Command(BaseCommand):
    xchange = Xchange.objects.get(pk=XCHANGE['COIN_MARKET_CAP'])
    comparison_currency = 'USD'

    def add_arguments(self, parser):
        parser.add_argument('--symbol', dest='currency_symbol', required=False, help='Currency Symbol', type=str)

    def handle(self, *args, **options):
        #  instance variable unique to each instance frank whiting x120

        if not self.getCoinList():
            return

        now = datetime.datetime.now()
        end_date = start_date = now.date()
        start_date = start_date - timedelta(days=10)
        if options['currency_symbol']:
            currencies = Currency.objects.filter(active=0, symbol=options['currency_symbol'])
        else:
            currencies = Currency.objects.filter(active=0)

        for currency in currencies:
            if currency.coinmarketcap is None:
                continue
            self.parseHistoricalPage(currency, start_date, end_date)

        start_date = now.replace(year=2018, month=4, day=1, second=0, minute=0, hour=0)
        start_date = start_date - timedelta(days=0)
        end_date = start_date - timedelta(weeks=3)

        while end_date < start_date:
            self.parse(start_date)
            start_date = start_date - timedelta(weeks=1)

    def parseHistoricalPage(self, currency, start_date, end_date):
        try:
            url = 'https://coinmarketcap.com/currencies/{0}/historical-data/?start={1}&end={2}'\
                .format(currency.coinmarketcap,
                        start_date.strftime('%Y%m%d'),
                        end_date.strftime('%Y%m%d'))
            r = requests.get(url)
        except ConnectionError as error:
            logger.error("Connection Error: {0}".format(error))
            return
        if r.status_code != 200:
            logger.error("not found {0}".format(r.url))
            return

        soup = BeautifulSoup(r.content, "html.parser")
        table = soup.find('tbody')

        for row in table.findAll('tr'):
            cells = row.findAll('td')

            try:
                timestamp = datetime.datetime.strptime(cells[0].text.strip(), "%b %d, %Y").date()
            except Exception as error:
                logger.error("Error getting timestamp: {0}: {1}".format(cells[0], error))
                continue

            try:
                open_price = float(cells[1].text.strip().replace(',', ''))
            except Exception as error:
                logger.info("Error getting open price:{0}: {1}".format(cells[1], error))
                open_price = 0

            try:
                high = float(cells[2].text.strip().replace(',', ''))
            except Exception as error:
                logger.info("Error getting high price:{0}: {1}".format(cells[2], error))
                high = 0

            try:
                low = float(cells[3].text.strip().replace(',', ''))
            except Exception as error:
                logger.info("Error getting low price: {0}: {1}".format(cells[3], error))
                low = 0

            try:
                close_price = float(cells[4].text.strip().replace(',', ''))
            except Exception as error:
                logger.info("Error getting close price:{0}: {1}".format(cells[4], error))
                close_price = 0

            try:
                volume = int(cells[5].text.replace(',', ''))
            except Exception as error:
                logger.info("Error getting volume {0}: {1}".format(cells[5], error))
                volume = 0

            try:
                if cells[6].text == '-':
                    market_cap = 0
                else:
                    market_cap = int(cells[6].text.replace(',', ''))
            except Exception as error:
                logger.info("Error getting market cap{0}: {1}".format(cells[6], error))
                market_cap = 0

            coin = Coins.Coins(currency.symbol)
            coin_record = coin.getRecord(time=int(calendar.timegm(timestamp.timetuple())),
                                         xchange=self.xchange)

            if coin_record is not None:
                coin_record.xchange = self.xchange
                coin_record.open = open_price
                coin_record.close = close_price
                coin_record.high = high
                coin_record.low = low
                coin_record.volume = volume
                coin_record.currency = currency
                coin_record.time = int(calendar.timegm(timestamp.timetuple()))
                coin_record.market_cap = market_cap
                coin_record.save()

                try:
                    top_coin = TopCoins.objects.get(currency=currency,
                                                    xchange=self.xchange,
                                                    time=int(calendar.timegm(timestamp.timetuple())))
                except ObjectDoesNotExist as error:
                    logger.error("Top Coin does not exist: {0} {1} -> adding it: error:{2}".format(currency.pk, currency.symbol, error))
                    top_coin = TopCoins()

                top_coin.currency = currency
                top_coin.market_cap = float(market_cap)
                top_coin.price = float(close_price)
                top_coin.xchange = self.xchange
                top_coin.time = int(calendar.timegm(timestamp.timetuple()))
                top_coin.save()
            else:
                logger.error("No class: {0} :not adding".format(currency.class_name))
        return

    def parse(self, start_date):

        r = requests.get('https://coinmarketcap.com/historical/{0}/'.format(start_date.strftime('%Y%m%d')))
        if r.status_code != 200:
            logger.error("not found {0}".format(r.url))
            return
        soup = BeautifulSoup(r.content, "html.parser")

        table = soup.find('tbody')

        for row in table.findAll('tr'):
            cells = row.findAll('td')
            symbol = cells[2].text.strip()

            market_cap = cells[3]['data-usd']
            try:
                market_cap = float(market_cap)
            except Exception as error:
                logger.error("Failed Market Cap: {0}: {1}".format(market_cap, error))
                market_cap = 0

            try:
                p = cells[4].a['data-usd']
                p = p.replace(',', '')
                price = float(p)
            except Exception as error:
                logger.error("Failed Price: {0}: {1}".format(price, error))
                price = 0

            try:
                circulating_supply = cells[5].a['data-supply']
            except Exception as error:
                logger.error("Failed circulating supply: {0}:{1}".format(circulating_supply, error))
                circulating_supply = cells[5].span['data-supply']

            try:
                circulating_supply = int(float(circulating_supply))
            except Exception as error:
                logger.error("Failedcirculating supply: {0}: {1}".format(circulating_supply, error))
                circulating_supply = 0

            try:
                currency = Currency.objects.get(symbol=symbol)
            except ObjectDoesNotExist as error:
                logger.error("{0} does not exist in our currency list..continuing: error: {1}".format(symbol, error))
                continue

            coins = Coins.Coins(symbol)
            coin = coins.getRecord(time=int(calendar.timegm(start_date.timetuple())),
                                   xchange=self.xchange)
            if coin is not None:
                coins.createClass()
                coin.xchange = self.xchange
                coin.close = price
                coin.currency = currency
                coin.time = int(calendar.timegm(start_date.timetuple()))
                coin.market_cap = market_cap
                coin.total_supply = circulating_supply
                coin.save()

            else:
                logger.error("no class for symbol {0}:".format(symbol))
        return

    def getCoinList(self):
        for index in range(0, 1600, 100):
            url = 'https://api.coinmarketcap.com/v1/ticker/?start={0}&limit=100'.format(index)
            response = requests.get(url)
            if response.status_code != 200:
                logger.info("not found: {0}".format(response.url))
                return False

            for coin in response.json():

                try:
                    currency = Currency.objects.get(symbol=coin['symbol'])
                    logger.info("{0}: exists in Currencies, continuing".format(coin['symbol']))
                    coins = Coins.Coins(coin['symbol'])
                    coins.createClass()
                    currency.class_name = coins.class_name
                    if currency.name is None:
                        currency.name = coin['name']
                    if currency.coin_name is None:
                        currency.coin_name = coin['name']
                    if currency.full_name is None:
                        currency.full_name = coin['name']
                    currency.save()

                except ObjectDoesNotExist as error:
                    logger.info("{0}: not found, Adding it to Currencies: {1}".format(coin['symbol'], error))
                    coins = Coins.Coins(coin['symbol'])
                    coins.createClass()

                    currency = Currency(name=coin['name'],
                                        symbol=coin['symbol'],
                                        coin_name=coin['name'],
                                        full_name=coin['name'],
                                        coinmarketcap=coin['id'],
                                        class_name=coins.class_name)
                    currency.save()
        return True
