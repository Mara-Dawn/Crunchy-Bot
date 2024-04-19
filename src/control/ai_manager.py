import datetime

import discord
from cogs.jail import Jail
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.chat_log import ChatLog
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from openai import AsyncOpenAI


class AIManager(Service):

    KEY_FILE = "openai.txt"
    TOKEN_SUMMARIZE_LIMIT = 2500
    TOKEN_SUMMARIZE_THRESHOLD = 2000
    DISCORD_MESSAGE_MAX_LENGTH = 1950
    JAIL_COMMAND_MESSAGE = "You are going to jail"
    JAIL_RELEASE_COMMAND_MESSAGE = "You are released form jail"
    JAIL_COMMAND_DURATION = 30
    JAILED = "jailed"
    NOT_JAILED = "free"

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
            "You enjoy degrading people in a sexual way and you often casually use unhinged and lewd comments in your normal language."
            "Usually you are nice and gentle though, as long as everyone remains civil and calm. "
            "You are not in a relationship as of now, but you enjoy that. "
        )

        self.backstory += (
            "Use gender neutral language as much as possible. Always use direct speech like in an in person conversation. "
            "Each message will lead with the name of the user delimited with 'user' XML tags. Leave both the tags and their content out of your response."
            "When addressing users, always use the name found within parentheses, discarding any other text. Also discard the parentheses themselves."
            "Each message will contain information wether the user is currently jailed or not, delimited with the 'jailed' XML tags. "
            f"'{self.JAILED}' means they are in jail. while '{self.NOT_JAILED}' means they are free. The following is your only way to change this: "
            f"You may jail people with these exact words: '{self.JAIL_COMMAND_MESSAGE}'. Only use this extremely rarely for really bad offenders. "
            f"You may release jailed people with these exact words: '{self.JAIL_RELEASE_COMMAND_MESSAGE}'. You should almost never use this, only when "
            "they beg you to release them of a long time. And even then it should be a one in onehundred chance."
        )

        self.client = AsyncOpenAI(api_key=self.token.strip("\n "))
        self.chat_logs: dict[int, ChatLog] = {}
        self.channel_logs: dict[int, ChatLog] = {}

    async def listen_for_event(self, event: BotEvent) -> str:
        pass

    async def __dynamic_response(self, message: discord.Message, response_text: str):
        jail_cog: Jail = self.bot.get_cog("Jail")

        if self.JAIL_COMMAND_MESSAGE.lower() in response_text.lower():
            jail_announcement = (
                f"<@{message.author.id}> was sentenced to Jail by <@{self.bot.user.id}>"
            )
            duration = self.JAIL_COMMAND_DURATION
            member = message.author
            success = await jail_cog.jail_user(
                message.guild.id, self.bot.user.id, member, duration
            )
            if success:
                timestamp_now = int(datetime.datetime.now().timestamp())
                release = timestamp_now + (duration * 60)
                jail_announcement += f"\nThey will be released <t:{release}:R>."
                await jail_cog.announce(message.guild, jail_announcement)

        if self.JAIL_RELEASE_COMMAND_MESSAGE.lower() in response_text.lower():
            jail_announcement = f"<@{message.author.id}> was released from Jail by <@{self.bot.user.id}>"
            member = message.author
            response = await jail_cog.release_user(
                message.guild.id, self.bot.user.id, member
            )
            if response:
                jail_announcement += response
                await jail_cog.announce(message.guild, jail_announcement)

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
        active_jails = self.database.get_active_jails_by_member(
            message.guild.id, message.author.id
        )
        jail_state = self.NOT_JAILED

        if len(active_jails) > 0:
            jail_state = self.JAILED

        user_message = (
            f"<user>{message.author.display_name}</user>"
            f"<jailed>{jail_state}</jailed>" + message.clean_content
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
