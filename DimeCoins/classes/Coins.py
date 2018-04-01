import logging
import inspect
from os.path import join
from django.core.management import call_command
from django.core.exceptions import ObjectDoesNotExist
from DimeCoins.settings.base import PROJECT_DIR
from DimeCoins.models.coins0 import *
from DimeCoins.models.coins70 import *
from DimeCoins.models.coins140 import *
from DimeCoins.models.coins210 import *
from DimeCoins.models.coins280 import *
from DimeCoins.models.coins350 import *
from DimeCoins.models.coins420 import *
from DimeCoins.models.coins490 import *
from DimeCoins.models.coins560 import *
from DimeCoins.models.coins630 import *
from DimeCoins.models.coins700 import *
from DimeCoins.models.coins770 import *
from DimeCoins.models.coins840 import *
from DimeCoins.models.coins910 import *
from DimeCoins.models.coins980 import *
from DimeCoins.models.coins1050 import *
from DimeCoins.models.coins1120 import *
from DimeCoins.models.coins1190 import *
from DimeCoins.models.coins1260 import *
from DimeCoins.models.coins1330 import *
from DimeCoins.models.coins1400 import *
from DimeCoins.models.coins1470 import *
from DimeCoins.models.coins1540 import *
from DimeCoins.models.coins1610 import *
from DimeCoins.models.coins1680 import *
from DimeCoins.models.coins1750 import *
from DimeCoins.models.coins1820 import *
from DimeCoins.models.coins1890 import *
from DimeCoins.models.coins1960 import *
from DimeCoins.models.coins2030 import *
from DimeCoins.models.coins2100 import *
from DimeCoins.models.coins2170 import *
from DimeCoins.models.coins2240 import *
from DimeCoins.models.coins2310 import *
from DimeCoins.models.coins2380 import *
from DimeCoins.models.coins2450 import *
from DimeCoins.models.coins2520 import *
from DimeCoins.models.coins2590 import *
from DimeCoins.models.coins2660 import *


logger = logging.getLogger(__name__)


class Coins:

    def __init__(self, symbol):
        self.class_name = None
        self.symbol = symbol
        self.createClassName(symbol)

    def getClassName(self):
        if inspect.getmembers(self.class_name):
            try:
                coin_class = eval(self.class_name)
                return coin_class.__class__.__name__
            except ObjectDoesNotExist as error:
                logger.info("Class Does not exist: {0} {1}".format(self.class_name, error))
                return eval(self.symbol)()
            except NameError as error:
                logger.info("Class Name Error: {0} {1}".format(self.class_name, error))
                return None
        else:
            self.class_name = self.createClassName(self.symbol)
        return self.class_name

    def getRecord(self, time, xchange):

        if inspect.getmembers(self.class_name):
            try:
                coin_class = eval(self.class_name)
                # logger.info("Evaluated: {0} to class".format(self.class_name))
                return coin_class.objects.get(time=time, xchange=xchange)
            except ObjectDoesNotExist:
                logger.info("Return empty record for class: {0}".format(self.class_name))
                return eval(self.class_name)()
            except NameError as error:
                logger.error("Class Name Error: {0}".format(error))
                return None
        else:
            logger.error("No members for class: {0}".format(self.class_name))
            return None

    def createClassName(self, symbol):

        new_class_name = ""
        for idx, char in enumerate(symbol):
            if idx == 0:
                if char.isdigit():
                    if int(char) == 1:
                        new_class_name = new_class_name + 'ONE_'
                    elif int(char) == 2:
                        new_class_name = new_class_name + 'TWO_'
                    elif int(char) == 3:
                        new_class_name = new_class_name + 'THREE_'
                    elif int(char) == 4:
                        new_class_name = new_class_name + 'FOUR_'
                    elif int(char) == 5:
                        new_class_name = new_class_name + 'FIVE_'
                    elif int(char) == 6:
                        new_class_name = new_class_name + 'SIX_'
                    elif int(char) == 7:
                        new_class_name = new_class_name + 'SEVEN_'
                    elif int(char) == 8:
                        new_class_name = new_class_name + 'EIGHT_'
                    elif int(char) == 9:
                        new_class_name = new_class_name + 'NINE_'
                    elif int(char) == 0:
                        new_class_name = new_class_name + 'ZERO_'
                    else:
                        pass
                    continue

            if idx == (len(symbol) - 1):
                if char == '*':
                    new_class_name = new_class_name + '_STAR'
                if char == '$':
                    new_class_name = new_class_name + 'DOLLAR'
                elif char == '@':
                    new_class_name = new_class_name + '_AT'
                else:
                    new_class_name = new_class_name + char.upper()
                continue
                
            if char == '*':
                new_class_name = new_class_name + 'STAR_'
            if char == '$':
                new_class_name = new_class_name + 'DOLLAR_'
            elif char == '@':
                new_class_name = new_class_name + 'AT_'
            elif char.isdigit():
                new_class_name = new_class_name + str(char)
            elif char.encode('ascii').isalpha():
                new_class_name = new_class_name + char.upper()
            else:
                pass

        self.class_name = new_class_name.upper()
        return self.class_name

    def createClass(self):
        try:
            coin_class = eval(self.class_name)
            logger.info("Class Exists, not creating: {0} to class".format(self.class_name))
            return coin_class
        except NameError as error:
            file_object = open(join(PROJECT_DIR, 'models', 'coins2660.py'), 'a')
            file_object.write("\nclass {0}(Coin):\n".format(self.class_name))
            file_object.write("\tpass\n\n")
            file_object.close()
            call_command('makemigrations DimeCoins')
            call_command('migrate')
            logger.info("Class Created be sure to migrate: {0}".format(self.class_name))
            return None
        except Exception as error:
            logger.error("Class Creation Failed Name Error: {0}".format(error))
            return None
