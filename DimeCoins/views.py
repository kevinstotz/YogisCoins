from DimeCoins.models.base import Currency, Coin, Xchange
from DimeCoins.classes import Coins
from DimeCoins.paginations import StandardResultsSetPagination
from DimeCoins.serializer import CurrencySerializer, CurrencyLineChartSerializer, CurrencyDeltaSerializer
import logging
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.parsers import JSONParser
from django.core.exceptions import ObjectDoesNotExist
from DimeCoins.settings.base import XCHANGE


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-2s) %(message)s')


class Index(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    model = Currency
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        pass


class CurrencyList(generics.ListAPIView):
    queryset = Currency.objects.all().filter(active=0)
    permission_classes = (AllowAny, )
    serializer_class = CurrencySerializer
    model = Currency
    parser_classes = (JSONParser,)
    filter_backends = (DjangoFilterBackend,)
    ordering = ('name',)


class CurrencySearch(generics.ListAPIView):
    queryset = Currency.objects.all().filter(active=0)
    permission_classes = (AllowAny, )
    serializer_class = CurrencySerializer
    model = Currency
    parser_classes = (JSONParser,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', 'symbol',)
    ordering = ('name',)


class CurrencyLineChart(generics.ListAPIView):
    permission_classes = (AllowAny, )
    pagination_class = StandardResultsSetPagination
    serializer_class = CurrencyLineChartSerializer
    model = Coin
    parser_classes = (JSONParser,)
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('time',)
    ordering = ('time',)

    def get_queryset(self):
        try:
            currency = Currency.objects.get(active=0, pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            logger.error("{0} Does not exist".format(self.kwargs['pk']))
            return None
        coins = Coins.Coins(currency.symbol)
        coin = coins.getObject()
        xchange = Xchange.objects.get(pk=XCHANGE['COIN_MARKET_CAP'])
        return coin.objects.filter(xchange=xchange, time__gte=self.request.GET.get('time')).order_by('-time')


class CurrencyDelta(generics.ListAPIView):
    permission_classes = (AllowAny, )
    pagination_class = StandardResultsSetPagination
    serializer_class = CurrencyDeltaSerializer
    model = Coin
    parser_classes = (JSONParser,)

    def get_queryset(self):
        try:
            currency = Currency.objects.get(active=0, pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            logger.error("{0} Does not exist".format(self.kwargs['pk']))
            return None
        coins = Coins.Coins(currency.symbol)
        coin = coins.getObject()
        xchange = Xchange.objects.get(pk=XCHANGE['COIN_MARKET_CAP'])
        return coin.objects.filter(xchange=xchange, time__gte=self.request.GET.get('time')).order_by('-time')
