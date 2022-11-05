from smellybot.access_control import MasterOnly, StreamerPlus, ModPlus, AdminPlus
from smellybot.config.data import ConfigData
from smellybot.config.definition import ConfigDefinition, ListConfigDefinition
from smellybot.config.schema import ConfigSchema
from smellybot.config.secure_config import ConfigRoot
from smellybot.config.types.bool import CBool
from smellybot.config.types.string import CUsername, CString
from smellybot.smellybot import SmellyBot

from smellybot.logger.smelly_logger import slogger


config_schema = ConfigSchema()
config_data = ConfigData("data/config/config.yaml")
config_data.load()

root_config = ConfigRoot(config_schema, config_data)

root_config.register(ConfigDefinition("access_token", ctype=CString()),
                     read_access_control=MasterOnly(), write_access_control=MasterOnly())

root_config.register(ConfigDefinition("prefix", ctype=CString()),
                     read_access_control=ModPlus(), write_access_control=AdminPlus())
root_config.register(ListConfigDefinition("channels", unique=True, ctype=CString()),
                     read_access_control=ModPlus(), write_access_control=AdminPlus())

root_config.register(ConfigDefinition("bot_username", ctype=CUsername()),
                     read_access_control=ModPlus(), write_access_control=AdminPlus())
root_config.register(ConfigDefinition("master_user", ctype=CUsername()),
                     read_access_control=ModPlus(), write_access_control=MasterOnly())
root_config.register(ListConfigDefinition("admin_users", unique=True, ctype=CUsername()),
                     read_access_control=ModPlus(), write_access_control=MasterOnly())

root_config.register(ListConfigDefinition("mod_users", unique=True, ctype=CUsername()),
                     read_access_control=ModPlus(), write_access_control=StreamerPlus())

root_config.register(ConfigDefinition("enabled", ctype=CBool()),
                     read_access_control=ModPlus(), write_access_control=ModPlus())

smellybot = SmellyBot(root_config, slogger)
smellybot.run()
