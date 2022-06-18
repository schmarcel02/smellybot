import asyncio
import random
import re
import shlex
import time
from typing import Dict, List, Union

import yaml
from twitchio import Message
from twitchio.ext import commands
from twitchio.ext.commands import Context

from config import ModuleConfig
from smellybot import BotModule, BotChannel

QUOTE_REGEX = re.compile(r"Quote #(\d+) (.+) (\[[^\]]*\] \[\d\d/\d\d/\d{4}\])")


class Quote:
    def __init__(self, channel_name: str, quote_number: int, quote_text: str, quote_appendix: str):
        self.channel_name = channel_name
        self.quote_number = quote_number
        self.quote_text = quote_text
        self.quote_appendix = quote_appendix

    def to_dict(self):
        return {
            "channel_name": self.channel_name,
            "quote_number": self.quote_number,
            "quote_text": self.quote_text,
            "quote_appendix": self.quote_appendix
        }

    @classmethod
    def from_dict(cls, quote_dict: dict):
        return cls(
            str(quote_dict["channel_name"]).lower(),
            int(quote_dict["quote_number"]),
            str(quote_dict["quote_text"]),
            str(quote_dict["quote_appendix"])
        )

    @classmethod
    def parse(cls, channel_name: str, message: str):
        quote_match = QUOTE_REGEX.match(message)
        if quote_match:
            quote_number = int(quote_match[1])
            quote_text = quote_match[2]
            quote_appendix = quote_match[3]
            return cls(channel_name, quote_number, quote_text, quote_appendix)
        return None


class OneQuoteStore:
    def __init__(self, filename: str):
        self.filename = filename
        self.channels: Dict[str, Dict[int, Quote]] = {}

    def load(self):
        with open(self.filename, "r") as quote_file:
            quotes = yaml.safe_load(quote_file)
        quotes = [Quote.from_dict(quote) for quote in quotes]
        self.channels = {}
        for quote in quotes:
            if quote.channel_name not in self.channels:
                self.channels[quote.channel_name] = {}
            self.channels[quote.channel_name][quote.quote_number] = quote

    def save(self):
        quotes = [quote.to_dict() for channel_quotes in self.channels.values() for quote in channel_quotes.values()]
        sorted_quotes = sorted(quotes, key=lambda q: (q['channel_name'], q['quote_number']))
        with open(self.filename, "w+") as quote_file:
            yaml.safe_dump(sorted_quotes, quote_file)

    def set_quote(self, quote: Quote):
        if quote.channel_name not in self.channels:
            self.channels[quote.channel_name] = {}
        channel_quotes = self.channels[quote.channel_name]
        channel_quotes[quote.quote_number] = quote
        self.save()

    def has_channel(self, channel_name: str) -> bool:
        return channel_name.lower() in self.channels

    def get_channel_quotes_dict(self, channel_name: str) -> Dict[int, Quote]:
        if self.has_channel(channel_name):
            return self.channels[channel_name.lower()]
        return {}

    def get_channel_quotes_list(self, channel_name: str) -> List[Quote]:
        return list(self.get_channel_quotes_dict(channel_name).values())

    def has_quote(self, channel_name: str, quote_number: int) -> bool:
        return quote_number in self.channels[channel_name.lower()]

    def get_quote(self, channel_name: str, quote_number: int) -> Union[Quote, None]:
        if self.has_quote(channel_name, quote_number):
            return self.channels[channel_name.lower()][quote_number]
        return None

    def get_random_quote(self, channel_name: str) -> Union[Quote, None]:
        channel_quotes = self.get_channel_quotes_list(channel_name)
        index = random.randint(0, len(channel_quotes))
        return channel_quotes[index]


class OneQuoteContext:
    def __init__(self, quote_store: OneQuoteStore, channel_name: str):
        self.quote_store = quote_store
        self.channel_name = channel_name
        self.active_quote_list: List[Quote] = []
        self.active_quote_list_index = 0

    def get_next_quote(self) -> Union[Quote, None]:
        if self.active_quote_list_index >= len(self.active_quote_list):
            return None
        quote = self.active_quote_list[self.active_quote_list_index]
        self.active_quote_list_index += 1
        return quote

    def set_quote(self, quote: Quote):
        self.quote_store.set_quote(quote)

    def get_channel_quotes_dict(self) -> Dict[int, Quote]:
        return self.quote_store.get_channel_quotes_dict(self.channel_name)

    def get_channel_quotes_list(self) -> List[Quote]:
        return self.quote_store.get_channel_quotes_list(self.channel_name)

    def has_quote(self, quote_number: int) -> bool:
        return self.quote_store.has_quote(self.channel_name, quote_number)

    def get_quote(self, quote_number: int) -> Union[Quote, None]:
        return self.quote_store.get_quote(self.channel_name, quote_number)

    def get_random_quote(self) -> Union[Quote, None]:
        return self.quote_store.get_random_quote(self.channel_name)

    def set_active_quote_list(self, quote_list: List[Quote]):
        self.active_quote_list = quote_list
        self.active_quote_list_index = 0

    def remaining_quotes(self) -> int:
        return len(self.active_quote_list) - self.active_quote_list_index


master_quote_store = OneQuoteStore("data/quotes/allquotes.yaml")
master_quote_store.load()


class QuoteFarmer(commands.Bot):
    DELAY_BETWEEN_REQUESTS = 10
    RESPONSE_TIMEOUT = 10
    MAX_CONSECUTIVE_TIMEOUTS = 3

    def __init__(self, access_token: str, channel_name: str, redo_all: bool = False, start_number: int = None, prefix: str = "!"):
        super().__init__(token=access_token, prefix=prefix, initial_channels=[channel_name])
        self.quote_context = OneQuoteContext(master_quote_store, channel_name.lower())
        self.channel_name = channel_name
        self.start_number = start_number
        self.last_received_quote = 0
        self.redo_all = redo_all
        self.channel = None

    async def event_join(self, channel, user):
        if self.channel is None:
            print(f'Joined channel: {channel.name}')
            self.channel = channel
            await self.request_loop()

    def find_next_missing_quote(self, quote_number: int):
        while not self.redo_all and self.quote_context.has_quote(quote_number):
            quote_number += 1
        return quote_number

    async def event_message(self, message):
        if message.echo:
            return

        if message.author.name.lower() in ["streamlabs", "schmarcel"]:
            print(f"{message.author.name} Message: {message.content}")
            quote = Quote.parse(self.channel_name.lower(), message.content)
            if quote:
                self.last_received_quote = quote.quote_number
                self.quote_context.set_quote(quote)
                self.run_event("received_quote", quote.quote_number)

    async def request_loop(self):
        quote_number = self.start_number

        channel_quotes = self.quote_context.get_channel_quotes_list()
        max_quote_number = max(quote.quote_number for quote in channel_quotes) if len(channel_quotes) > 0 else 0
        consecutive_timeouts = 0
        while True:
            quote_number = self.find_next_missing_quote(quote_number)
            await self.request_quote(quote_number)
            try:
                await self.wait_for("received_quote", lambda qn: qn == quote_number, timeout=self.RESPONSE_TIMEOUT)
            except asyncio.TimeoutError:
                if self.last_received_quote == quote_number:
                    print("Timeout, but ok")
                    consecutive_timeouts = 0
                else:
                    print("Timeout")
                    if quote_number > max_quote_number:
                        print("Consecutive")
                        consecutive_timeouts += 1
                        if consecutive_timeouts >= self.MAX_CONSECUTIVE_TIMEOUTS:
                            print("End")
                            await self.close()
                            break
            else:
                print("Success")
                consecutive_timeouts = 0
            quote_number += 1
            time.sleep(self.DELAY_BETWEEN_REQUESTS)

    async def request_quote(self, quote_number: int):
        message = f"!quote {quote_number}"
        print(f"Sending: {message}")
        await self.channel.send(message)


class Quoter(BotModule):
    def __init__(self, bot_channel: BotChannel, module_config: ModuleConfig):
        super().__init__(bot_channel, module_config)
        self.command_list()
        self.quote_context = OneQuoteContext(master_quote_store, self.bot_channel.channel_name)

    @classmethod
    def name(cls):
        return "quoter"

    def command_list(self):
        self.add_command(self.fakequote)
        self.add_command(self.crossquote)
        self.add_command(self.searchquote)
        self.add_command(self.searchcrossquote)
        self.add_command(self.nextquote)

    async def handle_message(self, message: Message):
        if message.author.name.lower() == "streamlabs":
            quote = Quote.parse(self.bot_channel.channel_name.lower(), message.content)
            if quote:
                self.logger.info(f"{message.author.name}: {message.content}")
                self.quote_context.set_quote(quote)

    def findquotes(self, arguments: list, channel_name: str = None) -> List[Quote]:
        matching_quotes = []

        channel_name = channel_name or self.bot_channel.channel_name
        channel_quotes = master_quote_store.get_channel_quotes_list(channel_name)

        regexes = [re.compile(argument, re.IGNORECASE) for argument in arguments]
        for quote in channel_quotes:
            match = True
            for regex in regexes:
                if not regex.search(quote.quote_text):
                    match = False
                    break
            if match:
                matching_quotes.append(quote)
        return matching_quotes

    async def fakequote(self, ctx: Context):
        command_split = ctx.message.content.split(" ", 2)
        if len(command_split) == 0:
            self.logger.warning("No... command provided?")
            return
        if len(command_split) == 1:
            self.logger.warning("No quote number provided")
            return

        try:
            quote_number = int(command_split[1])
        except:
            self.logger.warning("Quote number is not a number")
            return
        quote = self.quote_context.get_quote(quote_number)
        if not quote:
            self.logger.warning("Quote %s not found in %s's quotes", quote_number, self.quote_context.channel_name)
            return

        if len(command_split) > 2:
            arguments = command_split[2]
        else:
            arguments = ""
        arguments_split = shlex.split(arguments)
        if len(arguments_split) % 2 != 0:
            self.logger.warning("Uneven number of arguments provided")
            return

        await self.dispatch_fakequote(quote, arguments_split)

    async def crossquote(self, ctx: Context):
        command_split = ctx.message.content.split(" ")
        if len(command_split) == 0:
            self.logger.warning("No... command provided?")
            return
        if len(command_split) == 1:
            self.logger.warning("No channel name provided")
            return

        cross_channel_name = command_split[1]

        if not master_quote_store.has_channel(cross_channel_name):
            self.logger.warning(f"Channel %s not found", cross_channel_name)
            return

        if len(command_split) == 2:
            quote = master_quote_store.get_random_quote(cross_channel_name)
            if not quote:
                self.logger.warning(f"%s has no quotes", cross_channel_name)
        else:
            try:
                quote_number = int(command_split[2])
            except:
                self.logger.warning("Quote number is not a number")
                return
            quote = master_quote_store.get_quote(cross_channel_name, quote_number)
            if not quote:
                self.logger.warning(f"Quote %s not found in %s's quotes", quote_number, cross_channel_name)
                return
        await self.send_quote(quote)

    async def searchquote(self, ctx: Context):
        command_split = ctx.message.content.split(" ", 1)
        if len(command_split) == 0:
            self.logger.warning("No... command provided?")
            return
        if len(command_split) == 1:
            self.logger.warning("No keywords provided")
            return
        arguments = command_split[1]
        arguments_split = shlex.split(arguments)
        matching_quotes = self.findquotes(arguments_split)
        self.quote_context.set_active_quote_list(matching_quotes)

        await self.dispatch_next_quote()

    async def searchcrossquote(self, ctx: Context):
        command_split = ctx.message.content.split(" ", 2)
        if len(command_split) == 0:
            self.logger.warning("No... command provided?")
            return
        if len(command_split) == 1:
            self.logger.warning("No channel name provided")
            return
        if len(command_split) == 2:
            self.logger.warning("No keywords provided")
            return
        channel_name = command_split[1]
        arguments = command_split[2]
        arguments_split = shlex.split(arguments)
        matching_quotes = self.findquotes(arguments_split, channel_name)
        self.quote_context.set_active_quote_list(matching_quotes)

        await self.dispatch_next_quote()

    async def nextquote(self, ctx: Context):
        await self.dispatch_next_quote()

    async def dispatch_next_quote(self):
        quote = self.quote_context.get_next_quote()
        if not quote:
            return

        more = self.quote_context.remaining_quotes()
        await self.send_quote(quote, more)

    async def dispatch_fakequote(self, quote: Quote, arguments: list = None):
        quote_text = quote.quote_text
        if arguments:
            for i in range(0, len(arguments), 2):
                regex = re.compile(arguments[i], re.IGNORECASE)
                quote_text = regex.sub(arguments[i + 1], quote_text)

        message = f"Fakequote #{quote.quote_number} {quote_text} {quote.quote_appendix}"
        await self.bot_channel.send(message)

    async def send_quote(self, quote: Quote, more: int = 0):
        channel_name_string = ""
        if quote.channel_name != self.bot_channel.channel_name.lower():
            channel_name_string = f"{quote.channel_name}'s "

        more_string = ""
        if more > 0:
            more_string = f" {more} more... !nextquote"

        message = f"{channel_name_string}Quote #{quote.quote_number} {quote.quote_text} {quote.quote_appendix}{more_string}"
        await self.bot_channel.send(message)
