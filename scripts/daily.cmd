
set WORKING_DIR=C:\Users\kevin\OneDrive\Work\software\dime\DimeCoins
set PYTHONPATH=C:\Users\kevin\OneDrive\Work\software\dime\DimeAPI
set DJANGO_SERVER_TYPE=dev
set DJANGO_SETTINGS_MODULE=DimeCoins.settings.dev

cd %WORKING_DIR%
%PYTHON% manage.py Coinbase
%PYTHON% manage.py CoinMarketCap
%PYTHON% manage.py Bittrex
%PYTHON% manage.py CryptoCompare
%PYTHON% manage.py Gdax
%PYTHON% manage.py Kraken
%PYTHON% manage.py CryptoIndeX

set WORKING_DIR=C:\Users\kevin\OneDrive\Work\software\dime\DimeAPI
set PYTHONPATH=C:\Users\kevin\OneDrive\Work\software\dime\DimeCoins
set DJANGO_SERVER_TYPE=dev
set DJANGO_SETTINGS_MODULE=DimeAPI.settings.dev
cd %WORKING_DIR%
%PYTHON% manage.py GenerateIndexHistory
%PYTHON% manage.py CalculateIndex

cd scripts