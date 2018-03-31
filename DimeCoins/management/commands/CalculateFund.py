from django.core.exceptions import ObjectDoesNotExist
from DimeAPI.models import Xchange, FundRebalanceDate, Currency, Fund
from django.core.management.base import BaseCommand
from DimeAPI.settings.base import XCHANGE
from datetime import datetime, timedelta
import calendar
from django.apps import apps
from django.db.models import Sum


class Command(BaseCommand):

    def handle(self, *args, **options):

        periods = FundRebalanceDate.objects.all().order_by('start_date')[15:]

        xchange = Xchange.objects.get(pk=XCHANGE['COIN_MARKET_CAP'])

        for period in periods:
            if not self.verify(period, xchange):
                return

        for period in periods:
            self.calculateFund(period, xchange)

    def calculateFund(self, period, xchange):

        period_start_date = period.start_date
        period_end_date = period.end_date

        prior_Fund_Value = Fund.objects.filter(period__pk=(period.pk-1)).aggregate(Sum('end_value'))
        if period.pk == 2:
            level = 10
        else:
            level = prior_Fund_Value['end_value__sum']

        if period_start_date > datetime.utcnow().date():
            return

        if period_end_date > datetime.utcnow().date():
            period_end_date = datetime.utcnow().date() - timedelta(days=1)

        market_cap = dict()
        rebalance_price = dict()
        market_cap_sum = Fund.objects.filter(rebalance_date=period_start_date).aggregate(Sum('market_cap'))

        funds = Fund.objects.filter(rebalance_date=period_start_date).order_by('-market_cap')
        for fund in funds:

            try:
                coin_class = apps.get_model(app_label='DimeCoins', model_name=fund.currency.symbol)
            except Exception as error:
                print(error)
                print("failed getting class")
                continue

            try:
                xchange_model = apps.get_model('DimeCoins', 'Xchange')
                xchange_mod = xchange_model.objects.using('coins').get(pk=xchange.pk)
                coin = coin_class.objects.using('coins').get(time=int(calendar.timegm(period_start_date.timetuple())),
                                                             xchange=xchange_mod)
            except ObjectDoesNotExist as error:
                print("symbol: {0} for time: {1}: not found : {2}".format(fund.currency.symbol,
                                                                          calendar.timegm(period_start_date.timetuple()),
                                                                          error))
                return
            except TypeError as error:
                print(error)
                return
            rebalance_price[fund.currency.pk] = coin.close
            market_cap[coin.pk] = coin.market_cap

        rank = 1

        for fund in funds:
            fund.level = level
            fund.rebalance_price = rebalance_price[fund.currency.pk]
            fund.percent_of = fund.market_cap / market_cap_sum['market_cap__sum'] * 100.0
            fund.amount = (fund.percent_of / 100.0 * fund.level) / fund.rebalance_price
            fund.rebalance_value = fund.rebalance_price * fund.amount
            xchange_model = apps.get_model('DimeCoins', 'Xchange')
            xchange_coins = xchange_model.objects.using('coins').get(pk=xchange.pk)

            currency_model = apps.get_model('DimeCoins', fund.currency.symbol.upper())
            try:
                currency = currency_model.objects.using('coins').get(xchange=xchange_coins, time=int(calendar.timegm(period_end_date.timetuple())))
            except ObjectDoesNotExist as error:
                print("symbol: {0}: time: {1}: error:{2}".format(fund.currency.symbol.upper(), calendar.timegm(period_end_date.timetuple()), error))
                return
            except:
                print("symbol: {0}: time: {1}".format(fund.currency.symbol.upper(), calendar.timegm(period_end_date.timetuple())))
                return

            fund.end_price = currency.close
            fund.end_value = fund.end_price * fund.amount
            fund.rank = rank
            rank = rank + 1
            fund.save()

    def verify(self, period, xchange):

        try:
            records = len(Fund.objects.filter(period__pk=period.pk))
            if records == 10:
                return True
        except Exception as error:
            print(error)
            print("failed len of period")

        topCoins_model = apps.get_model('DimeCoins', 'TopCoins')
        topCoins = topCoins_model.objects.using('coins').filter(time=int(calendar.timegm(period.start_date.timetuple()))).order_by('-market_cap')[:10]

        for idx, topCoin in enumerate(topCoins):
            currency = Currency.objects.get(pk=topCoin.currency.pk)
            fund = Fund()

            if period.pk == 2:
                fund.rebalance_price = topCoin.price
            fund.period = period
            fund.rank = idx
            fund.total_supply = topCoin.total_supply
            fund.market_cap = topCoin.market_cap
            fund.currency = currency
            fund.rebalance_date = period.start_date
            fund.save()
        return True
