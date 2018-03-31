from datetime import datetime
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from DimeCoins.models.base import Xchange



class XchangeSerializer(ModelSerializer):

    class Meta:
        model = Xchange
        fields = ('id', 'currency', 'name', 'url', 'api_url', 'api_key', 'api_secret', 'start_date', 'end_date', 'number_symbols')
