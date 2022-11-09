from typing import Type

from smellybot.abstract_classes import AbstractModule
from smellybot.exceptions import ModuleNotFoundException
from smellybot.modules.controller2 import Controller
from smellybot.modules.crumber import Crumber
from smellybot.modules.owoifier import Owoifier
from smellybot.modules.pyramid import Pyramid
from smellybot.modules.switcher import Switcher
from smellybot.modules.tally_competition import TallyComp

from .clapper import Clapper
from .husker import Husker
from .jisho import Jisho
from .quoter import Quoter
from .sasser import Sasser
from .asksmel import AskSmel
from .math import Math
from .numberfacts import NumberFacts
from .relay import Relay
from .tagsniffer import TagSniffer
from .tagnotifier import TagNotifier
from .amogus import Amogus
from .urban_dictionary import UrbanDictionary


class ModuleMaster:
    modules = {}

    @staticmethod
    def add_module(module: Type[AbstractModule]):
        ModuleMaster.modules[module.name().lower()] = module

    @staticmethod
    def get_module_by_name(name: str) -> Type[AbstractModule]:
        module_class = ModuleMaster.modules.get(name)
        if not module_class:
            raise ModuleNotFoundException()
        return module_class


ModuleMaster.add_module(Controller)
ModuleMaster.add_module(Clapper)
ModuleMaster.add_module(Husker)
ModuleMaster.add_module(Jisho)
ModuleMaster.add_module(Quoter)
ModuleMaster.add_module(Sasser)
ModuleMaster.add_module(Math)
ModuleMaster.add_module(AskSmel)
ModuleMaster.add_module(Relay)
ModuleMaster.add_module(TagSniffer)
ModuleMaster.add_module(TagNotifier)
ModuleMaster.add_module(NumberFacts)
ModuleMaster.add_module(Amogus)
ModuleMaster.add_module(Crumber)
ModuleMaster.add_module(Owoifier)
ModuleMaster.add_module(UrbanDictionary)
ModuleMaster.add_module(Pyramid)
ModuleMaster.add_module(TallyComp)
ModuleMaster.add_module(Switcher)
