#!/bin/bash
export PYTHONPATH=/opt/www/dime/api/DimeAPI

/usr/local/bin/python /opt/www/dime/coin/YogisCoins/manage.py runserver 172.31.2.86:10007
