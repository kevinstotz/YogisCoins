from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from DimeCoins.models.base import Xchange, Currency
from DimeCoins.models.coins0 import ADB
from DimeCoins.classes.Coins import Coins
from DimeCoins.settings.base import XCHANGE
from django.core.exceptions import ObjectDoesNotExist
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-2s) %(message)s')


class XchangeSerializer(ModelSerializer):

    class Meta:
        model = Xchange
        fields = ('id', 'currency', 'name', 'url', 'api_url',
                  'api_key', 'api_secret', 'start_date', 'end_date', 'number_symbols')


class CurrencySerializer(ModelSerializer):
    name = serializers.SerializerMethodField(source='coin_name')
    history = serializers.SerializerMethodField(source='id')
    market_cap = serializers.SerializerMethodField(source='symbol')

    class Meta:
        model = Currency
        fields = ('id', 'name', 'symbol', 'market_cap', 'history',)

    def get_history(self, obj: Currency):
        return obj.id

    def get_market_cap(self, obj: Currency):
        coins = Coins(obj.symbol)
        coin = coins.getLatest(XCHANGE['COIN_MARKET_CAP'])
        if coin is None:
            return 0
        else:
            return coin.market_cap

    def get_name(self, obj: Currency):
        return obj.coin_name


class CurrencyLineChartSerializer(ModelSerializer):
    name = serializers.SerializerMethodField(source='time')
    value = serializers.SerializerMethodField(source='close')

    class Meta:
        model = ADB
        fields = ('name', 'value',)

    def get_value(self, obj: ADB):
        return obj.close

    def get_name(self, obj: ADB):
        return obj.time


class CurrencyDeltaSerializer(ModelSerializer):
    delta = serializers.SerializerMethodField(source='close')
    start_date = serializers.SerializerMethodField(source='close')
    end_date = serializers.SerializerMethodField(source='close')

    class Meta:
        model = ADB
        fields = ('id', 'delta', 'start_date', 'start_date',)

    def get_delta(self, obj: ADB):
        return obj.close


class FundPreviewSerializer(ModelSerializer):
    value = serializers.SerializerMethodField(source='id')
    name = serializers.SerializerMethodField(source='id')

    class Meta:
        model = Currency
        fields = ('value', 'name',)

    def to_value(self, obj):
        try:
            currency = Currency.objects.using('coins').get(id=obj)
        except ObjectDoesNotExist as error:
            logger.error("{0}".format(error))
            return
        except Exception as error:
            logger.error("{0}".format(error))
            return
        return currency.symbol

    def to_name(self, obj):
        try:
            currency = Currency.objects.using('coins').get(id=obj)
        except ObjectDoesNotExist as error:
            logger.error("{0}".format(error))
            return
        except Exception as error:
            logger.error("{0}".format(error))
            return
        return currency.symbol
