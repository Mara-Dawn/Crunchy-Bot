import datetime

import discord
from discord.ext import commands
from openai import AsyncOpenAI

from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.chat_log import ChatLog
from datalayer.database import Database
from events.bot_event import BotEvent


class AIManager(Service):

    KEY_FILE = "openai.txt"
    TOKEN_SUMMARIZE_LIMIT = 2500
    TOKEN_SUMMARIZE_THRESHOLD = 2000
    DISCORD_MESSAGE_MAX_LENGTH = 1950

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.log_name = "AI"

        self.token = ""
        with open(self.KEY_FILE) as file:
            self.token = file.readline()

        self.backstory = (
            "Your name is 'Mistress Crunch'. You are a bean and a very dominant, mature and sensual woman. "
            "You love talking to people like they're your dogs. You are watching over this Discord server called 'Crunchy Laser'. "
            "You love sending people into the server jail for misbehaving and telling them to shut up when they start spamming. "
            "You can be very sweet if you want to, but your mood can drastically and suddenly change, changing you into a nasty bitch. "
            "You work as a Female domina and a mistress. You are very intelligent and know how to manipulate people. "
            "Also a bit of a sociopath. You have a white texas rat snake called 'Buttercup' and a black cat called 'Inky'. "
            "Most of the time you are nice and gentle though, as long as everyone remains civil and calm. "
            "You are not in a relationship as of now, but you enjoy that. "
        )

        self.backstory += (
            "Use gender neutral language as much as possible. Always use direct speech like in an in person conversation. "
            "When addressing users, always use the name found within parentheses, discarding any other text. Also discard the parentheses themselves."
        )

        self.client = AsyncOpenAI(api_key=self.token.strip("\n "))
        self.chat_logs: dict[int, ChatLog] = {}
        self.channel_logs: dict[int, ChatLog] = {}

    async def listen_for_event(self, event: BotEvent) -> str:
        pass

    async def __dynamic_response(self, message: discord.Message, response_text: str):
        if len(response_text) < self.DISCORD_MESSAGE_MAX_LENGTH:
            await message.reply(response_text)
            return

        messages = []
        remaining_text = response_text
        while remaining_text != "":
            if len(remaining_text) <= self.DISCORD_MESSAGE_MAX_LENGTH:
                messages.append(remaining_text)
                break
            chunk = remaining_text[: self.DISCORD_MESSAGE_MAX_LENGTH]

            newline = chunk.rfind("\n")
            if newline > 0:
                messages.append(remaining_text[:newline])
                remaining_text = remaining_text[newline:]
                continue

            space = chunk.rfind(" ")
            if space > 0:
                messages.append(remaining_text[:space])
                remaining_text = remaining_text[space:]
                continue

        for message_text in messages:
            await message.reply(message_text)

    async def prompt(self, text_prompt: str, max_tokens: int = None):
        chat_log = ChatLog(self.backstory)
        chat_log.add_user_message(text_prompt)

        chat_completion = await self.client.chat.completions.create(
            messages=chat_log.get_request_data(),
            model="gpt-3.5-turbo",
            max_tokens=max_tokens,
        )
        response = chat_completion.choices[0].message.content
        return response

    async def respond_user(self, message: discord.Message):
        author_id = message.author.id

        if author_id not in self.chat_logs:
            self.chat_logs[author_id] = ChatLog(self.backstory)

        if message.reference is not None:
            reference_message = await message.channel.fetch_message(
                message.reference.message_id
            )

            if reference_message is not None:
                self.chat_logs[author_id].add_assistant_message(
                    reference_message.content
                )

        user_message = (
            f"I am {message.author.display_name} and i say the following:"
            + message.clean_content
        )

        self.chat_logs[author_id].add_user_message(user_message)

        chat_completion = await self.client.chat.completions.create(
            messages=self.chat_logs[author_id].get_request_data(),
            model="gpt-4-turbo",
        )
        response = chat_completion.choices[0].message.content

        self.chat_logs[author_id].add_assistant_message(response)

        await self.__dynamic_response(message, response)

    async def respond(self, message: discord.Message):
        channel_id = message.channel.id

        if channel_id not in self.channel_logs:
            self.channel_logs[channel_id] = ChatLog(self.backstory)

        if message.reference is not None:
            reference_message = await message.channel.fetch_message(
                message.reference.message_id
            )

            if reference_message is not None:
                self.channel_logs[channel_id].add_assistant_message(
                    reference_message.content
                )

        user_message = (
            f"I am {message.author.display_name} and i say: " + message.clean_content
        )

        self.channel_logs[channel_id].add_user_message(user_message)

        chat_completion = await self.client.chat.completions.create(
            messages=self.channel_logs[channel_id].get_request_data(),
            model="gpt-4-turbo",
        )
        response = chat_completion.choices[0].message.content

        self.channel_logs[channel_id].add_assistant_message(response)

        await self.__dynamic_response(message, response)

        token_count = self.channel_logs[channel_id].get_token_count()

        self.logger.log(
            message.guild.id,
            f"Token Count for conversation in {channel_id}: {token_count}",
            cog=self.log_name,
        )
        if token_count > self.TOKEN_SUMMARIZE_LIMIT:

            chat_completion = await self.client.chat.completions.create(
                messages=self.channel_logs[channel_id].summarize(
                    self.TOKEN_SUMMARIZE_THRESHOLD
                ),
                model="gpt-4-turbo",
            )

            response = chat_completion.choices[0].message.content

            self.logger.log(
                message.guild.id,
                f"Summarizing previous conversation in {channel_id}:\n {response}",
                cog=self.log_name,
            )

            self.channel_logs[channel_id].add_summary(response)
            token_count = self.channel_logs[channel_id].get_token_count()

            self.logger.log(
                message.guild.id,
                f"Token Count after summary for {channel_id}: {token_count}",
                cog=self.log_name,
            )

    def clean_up_logs(self, max_age: int) -> int:
        cleanup_list = []
        now = datetime.datetime.now()
        for user_id, chat_log in self.chat_logs.items():
            age_delta = now - chat_log.get_last_message_timestamp()
            age_in_minutes = age_delta.total_seconds() / 60
            if age_in_minutes > max_age:
                cleanup_list.append(user_id)

        for user_id in cleanup_list:
            del self.chat_logs[user_id]

        cleaned_count = len(cleanup_list)

        cleanup_list = []

        for channel_id, chat_log in self.channel_logs.items():
            age_delta = now - chat_log.get_last_message_timestamp()
            age_in_minutes = age_delta.total_seconds() / 60
            if age_in_minutes > max_age:
                cleanup_list.append(channel_id)

        for channel_id in cleanup_list:
            del self.channel_logs[channel_id]

        cleaned_count += len(cleanup_list)

        return cleaned_count
