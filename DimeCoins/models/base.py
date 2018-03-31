from __future__ import unicode_literals
from django.db import models
from DimeCoins.settings.base import CURRENCY_SYMBOL_LENGTH, CURRENCY_NAME_LENGTH, CURRENCY_NAME_LENGTH, CURRENCY_FULL_NAME_LENGTH


class Xchange(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="")
    url = models.CharField(max_length=200, default="0", unique=True)
    api_url = models.CharField(max_length=200, default="0")
    api_key = models.CharField(max_length=200, default="0")
    api_secret = models.CharField(max_length=200, default="0")
    start_date = models.BigIntegerField(verbose_name="start date", default=0)
    end_date = models.BigIntegerField(verbose_name="end date", default=0)
    number_symbols = models.IntegerField(verbose_name="number of symbols", default=0)

    objects = models.Manager()

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ('name',)


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CURRENCY_NAME_LENGTH, default="", blank=False)
    description = models.CharField(max_length=255, default="", blank=False)

    objects = models.Manager()

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ('name',)


class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CURRENCY_NAME_LENGTH, default="", blank=False)
    symbol = models.CharField(max_length=CURRENCY_SYMBOL_LENGTH, default="", blank=False)
    category = models.ManyToManyField(Category, related_name="currencyCategory")
    coin_name = models.CharField(max_length=CURRENCY_NAME_LENGTH, default="")
    full_name = models.CharField(max_length=CURRENCY_FULL_NAME_LENGTH, default="")
    class_name = models.CharField(max_length=50, default="", blank=False)
    coinmarketcap = models.CharField(max_length=100, default="", blank=True)
    active = models.BooleanField(default=False, verbose_name="Active Currency")

    objects = models.Manager()

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ('id',)


class TopCoins(models.Model):
    id = models.AutoField(primary_key=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, default=1)
    price = models.FloatField(default=0.0)
    total_supply = models.BigIntegerField(default=0)
    market_cap = models.FloatField(default=0.0)
    xchange = models.ForeignKey(Xchange, on_delete=models.SET_DEFAULT, default=1)
    time = models.BigIntegerField(verbose_name="Date of Price", default=0)

    objects = models.Manager()

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ('currency',)


class Coin(models.Model):
    id = models.AutoField(primary_key=True)
    xchange = models.ForeignKey(Xchange, on_delete=models.SET_DEFAULT, default=1)
    currency = models.ForeignKey(Currency, on_delete=models.SET_DEFAULT, default=1)
    time = models.BigIntegerField(verbose_name="Date of Price", default=0)
    open = models.FloatField(default=0.0)
    close = models.FloatField(default=0.0)
    high = models.FloatField(default=0.0)
    low = models.FloatField(default=0.0)
    total_supply = models.FloatField(default=0.0)
    volume = models.FloatField(default=0.0)
    market_cap = models.FloatField(default=0.0)
    objects = models.Manager()

    class Meta:
        abstract = True
