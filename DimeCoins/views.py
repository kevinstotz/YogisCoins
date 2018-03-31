from DimeCoins.models.base import Currency
import logging
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from rest_framework.permissions import AllowAny

from rest_framework.parsers import JSONParser

logger = logging.getLogger(__name__)


class Index(generics.GenericAPIView):
    permission_classes = (AllowAny, )
    model = Currency
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        pass
