from modules import Controller
from modules.asksmel import AskSmel
from modules.husker import Husker
from modules.jisho import Jisho
from modules.math import Math
from modules.numberfacts import NumberFacts
from modules.relay import Relay
from modules.sasser import Sasser
from modules.tagnotifier import TagNotifier
from modules.tagsniffer import TagSniffer
from smellybot import SmellyBot, ModuleMaster
from modules.quoter import Quoter, QuoteFarmer
from modules.clapper import Clapper

from config import BotConfig, smelly_logger

bot_config = BotConfig(smelly_logger)
bot_config.load()

module_master = ModuleMaster()
module_master.add_module(Controller)
module_master.add_module(Clapper)
module_master.add_module(Husker)
module_master.add_module(Jisho)
module_master.add_module(Quoter)
module_master.add_module(Sasser)
module_master.add_module(Math)
module_master.add_module(AskSmel)
module_master.add_module(Relay)
module_master.add_module(TagSniffer)
module_master.add_module(TagNotifier)
module_master.add_module(NumberFacts)

smellybot = SmellyBot(module_master, bot_config, ["SchMarcEL"])
smellybot.run()

# qf = QuoteFarmer(bot_config.get_access_token(), "Nathxn", redo_all=True, start_number=16)
# qf.run()
