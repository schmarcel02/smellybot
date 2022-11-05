import logging
import os
import sys

from datetime import datetime

default_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', "%Y-%m-%d %H:%M:%S")
channel_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(channel_name)s | %(message)s', "%Y-%m-%d %H:%M:%S")
module_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(channel_name)s | %(module_name)s | %(message)s', "%Y-%m-%d %H:%M:%S")
command_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(channel_name)s | %(module_name)s | %(command_name)s | %(message)s', "%Y-%m-%d %H:%M:%S")
message_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(channel_name)s | %(module_name)s | %(author)s: %(message)s', "%Y-%m-%d %H:%M:%S")


class SmellyFormatter(logging.Formatter):
    def get_formatter(self, record):
        if hasattr(record, 'channel_name'):
            if hasattr(record, 'module_name'):
                if hasattr(record, 'author'):
                    return message_formatter
                if hasattr(record, 'command_name'):
                    return command_formatter
                return module_formatter
            return channel_formatter
        return default_formatter

    def format(self, record):
        formatter = self.get_formatter(record)
        return formatter.format(record)


now = datetime.now()
year = now.strftime("%Y")
month = now.strftime("%Y-%m")
day = now.strftime("%Y-%m-%d")

log_directory = f'logs/{year}/{month}'
log_filename = f'smellybot_{day}.log'

os.makedirs(log_directory, exist_ok=True)

slogger = logging.getLogger("smelly_bot")
slogger.setLevel(logging.DEBUG)

smelly_formatter = SmellyFormatter()

file_handler = logging.FileHandler(os.path.join(log_directory, log_filename), encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(smelly_formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(smelly_formatter)

slogger.addHandler(file_handler)
slogger.addHandler(stream_handler)
