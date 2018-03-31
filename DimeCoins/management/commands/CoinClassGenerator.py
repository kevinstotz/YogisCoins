from django.core.management.base import BaseCommand
from os.path import join
from DimeCoins.classes.SymbolName import SymbolName
from DimeCoins.settings.base import PROJECT_NAME
from DimeCoins.settings.local import DATABASES
from DimeCoins.models.base import Currency
from pathlib import Path


class Command(BaseCommand):
    help = 'Generate Coin Classes'
    outfile = join(PROJECT_NAME, 'models', 'coins')
    database = DATABASES['default']['NAME'].lower()
    coin_template_file = join(PROJECT_NAME, 'management', 'commands', 'sample_coin.sql')
    output_dir = join(PROJECT_NAME, 'sql')
    def handle_noargs(self, **options):
        pass

    def handle(self, *args, **options):

        currencies = Currency.objects.all()
        coin_file_class = open(self.outfile + str(0) + ".py", "w+") or quit()
        coin_file_class.writelines("from {0}.models.base import Coin\n\n\n".format(PROJECT_NAME))


        for idx, currency in enumerate(currencies):
            if idx % 200 == 0:
                coin_file_class.close()
                try:
                    coin_file_class = open(self.outfile + str(idx) + ".py", "w+") or quit()
                except:
                    print("Failed creaTinG {0}".format(self.outfile + str(idx) + ".py"))
                    continue
                coin_file_class.writelines("from {0}.models.base import Coin\n\n\n".format(PROJECT_NAME))
            symbolName = SymbolName(currency.symbol)
            class_name = symbolName.parse_symbol()
            try:
                coin_file_class.writelines(self.generate_class(class_name))
            except:
                print("Failed creatiG {0}".format(self.outfile + str(idx) + ".py"))
                continue
            if not self.write_sql(self, currency.symbol):
                print("Failed writinG {0}".format(currency.symbol))
                continue


    @staticmethod
    def generate_class(currency_class_name):
        class_str = 'class {}(Coin):'.format(currency_class_name.upper())
        class_str = '{0}{1}    pass{2}{3}'.format(class_str, '\n', '\n\n', '\n')
        return class_str

    @staticmethod
    def write_sql(self, symbol):
        try:
            with open(self.coin_template_file) as f: coin_template = f.read()
        except:
            print("Failed reading template {0}".format(self.coin_template_file))
            return False
        coin_template = coin_template.replace("__DATABASE__", self.database)
        coin_template = coin_template.replace("__TABLE__", PROJECT_NAME.lower() + '_' + symbol.lower())
        try:
            if symbol.lower() == 'PRN'.lower() or symbol.lower() == 'CON'.lower():
                symbol = symbol + '_1'
            Path(join(self.output_dir, symbol + ".sql")).write_text(coin_template)
        except:
            print("FaileD writing {0}".format(self.output_dir, symbol + ".sql"))
            return False
        return True

