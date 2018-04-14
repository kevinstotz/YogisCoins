from DimeCoins.models.base import Currency, Coin, Xchange
from DimeCoins.classes import Coins
from DimeCoins.paginations import StandardResultsSetPagination
from DimeCoins.serializer import CurrencySerializer, CurrencyLineChartSerializer, CurrencyDeltaSerializer
import logging, json, calendar
from datetime import datetime, timedelta
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from django.http import JsonResponse
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
            logger.error("{0} Does not exist: {1}".format(self.kwargs['pk'], error))
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
            logger.error("{0} Does not exist: {1}".format(self.kwargs['pk'], error))
            return None
        coins = Coins.Coins(currency.symbol)
        coin = coins.getObject()
        xchange = Xchange.objects.get(pk=XCHANGE['COIN_MARKET_CAP'])
        return coin.objects.filter(xchange=xchange, time__gte=self.request.GET.get('time')).order_by('-time')


class FundPreview(generics.ListAPIView):
    model = Currency
    parser_classes = (JSONParser,)
    permission_classes = (AllowAny,)
    queryset = Currency.objects.all()

    def post(self, request):
        previewFund = json.loads(request.body.decode("utf-8"))
        end_date = datetime.utcnow().replace(hour=0, second=0, minute=0)
        start_date = end_date - timedelta(days=30)
        previewBasket = []
        while start_date < end_date:
            value = 0
            for currency in previewFund['fundPreview']:
                try:
                    currency = Currency.objects.get(active=0, pk=currency['currencyId'])
                except ObjectDoesNotExist as error:
                    logger.error("{0} Does not exist: {1}".format(self.kwargs['pk'], error))
                    return None

                coins = Coins.Coins(currency.symbol)
                xchange = Xchange.objects.get(pk=XCHANGE['COIN_MARKET_CAP'])
                coin = coins.getRecord(xchange=xchange, time=calendar.timegm(start_date.timetuple()))
                value = value + (coin.close * 1.0 / len(previewFund['fundPreview']))

            previewBasket.append({"name": start_date.timestamp(), "value": value})
            start_date = start_date + timedelta(days=1)

        return JsonResponse(previewBasket, safe=False)
