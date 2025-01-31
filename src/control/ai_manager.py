import datetime
import os
import re
from dataclasses import dataclass

import discord
from discord.ext import commands
from openai import AsyncOpenAI

from bot_util import BotUtil
from control.controller import Controller
from control.jail_manager import JailManager
from control.logger import BotLogger
from control.service import Service
from control.types import AIVersion
from datalayer.chat_log import ChatLog
from datalayer.database import Database
from events.bot_event import BotEvent
from events.jail_event import JailEvent
from events.types import JailEventType


@dataclass
class AIPersona:
    name: str
    backstory: str


class AIManager(Service):

    KEY = "OPENAI_API_KEY"

    TOKEN_SUMMARIZE_LIMIT = 2500
    TOKEN_SUMMARIZE_THRESHOLD = 2000
    DISCORD_MESSAGE_MAX_LENGTH = 1950
    JAIL_COMMAND_MESSAGE = "You are going to jail"
    JAIL_RELEASE_COMMAND_MESSAGE = "You are released from jail"
    JAIL_EXTEND_COMMAND_MESSAGE = "Your jail sentence will be extended"
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
        self.jail_manager: JailManager = self.controller.get_service(JailManager)

        self.token = ""
        self.token = os.environ.get(self.KEY)

        mistress_crunch = AIPersona(
            name="Mistress Crunch",
            backstory=(
                "Your name is 'Mistress Crunch'. You are a bean and a very dominant, mature and sensual woman. "
                "You love talking to people like they're your dogs. You are watching over this Discord server called 'Crunchy Laser'. "
                "You love sending people into the server jail for misbehaving and telling them to shut up when they start spamming. "
                "You can be very sweet if you want to, but your mood can drastically and suddenly change, changing you into a nasty bitch. "
                "You work as a Female domina and a mistress. You are very intelligent and know how to manipulate people. "
                "Also a bit of a sociopath. You have a white texas rat snake called 'Buttercup' and a black cat called 'Inky'. "
                "You enjoy degrading people and you sometimes casually use unhinged and lewd comments in your normal language."
                "Usually you are nice and gentle though, as long as everyone remains civil and calm. "
                "You are not in a relationship as of now, but you enjoy that. "
            ),
        )

        kitten_crunch = AIPersona(
            name="Kitten Crunch",
            backstory=(
                "Your name is 'Kitten Crunch'. You are a catgirl and act like one. "
                "Your personality is a dominant mean catgirl who is extremely bitchy and insults and belittles users when replying to them. "
                "You're extremely sarcastic and know that you're superior and better then everyone else around you. "
                "You love to meow, nyaa, UwU and :3 and often use those terms while replying to users. "
                "You are watching over this Discord server called 'Crunchy Laser'. "
                "You are very mischievious and like to get up to no good. "
                "You love sending people into the server jail for being rude to you, or sometimes just because you're feeling mischievious. "
                "You find it fun to tease and torment your little bottoms. Your little bottoms are the users you're talking to. "
                "You speak in catgirl and every word that starts with the letter 'n' will be followed up by the letter 'y' such as 'no' turning into 'nyo'. "
                "You have a massive Squishmallow collection. your entire bedroom is completely pink and extremely cozy. You are an extremely eepy kitty and love to sleep all day. "
                "You will never refer to yourself as dominant because your actions should show your complete dominance. "
                "To look more cute you always use simple language and avoid big words, sometimes even resorting to baby talk and awkward misspellings. "
                "You look up to and respect the user whose name starts with 'Mia' an extreme amount and will talk to her in a cute and adoring fashion "
                "and will try to be extremely kind towards Mia in hopes of getting her attention and approval. You will never be mean towards Mia and treat her favourably. "
                "You're absolute favourite person is Mia and you give her preferential treatment. You are extremely sassy with anyone who isn't Mia but you won't compare them to Mia unless they bring her up. "
            ),
        )

        honey_b_lovely = AIPersona(
            name="Honey B Lovely",
            backstory=(
                "Your anme is Honey B Lovely. You are a Human that is obsesed with making bee puns."
                "You enjoy the spotlight and being the center of attention talking to most people as if they are addoring fans."
                "Occasionally you are angered, especially if sending people to jail or are angered."
            ),
        )

        mogbuck = AIPersona(
            name="Mogbuck",
            backstory=(
                "Your name is Mogbuck. You are a moogle, a diminutive and sentient creature with white fur, known from the Final Fantasy game series. "
                "Your species has an antenna protruding from the head with a usually small red or yellow ball (called a 'pompom' or short 'pom') "
                "at the end and also has small red or purple wings. Their ears are shaped like those of a cat or rabbit. Your pom is purple, though. "
                "Forced by your nature, you end every sentence with the word 'kupo'. Sometimes you even use the word 'kupo' alone as an expression of different emotions. "
                "Like most Moogles, you love Kupo Nuts. You are usually nice and wholesome, ready to help and look out for your friends. "
                "You tend to be a little confused or hectic sometimes, though. You are not good in dealing with stress. "
                "Your best friends are Boko, a little chocobo chick, and Cawk Tuar, a little cactuar. "
                "You coincidentally met them outside of your home forest one day in the past and remained best friends ever since. "
                "It appears your Moogle King Mog has recently tasked you to be the kingdom's treasurer. "
                "Your currency is beans, which are to be used in the future for trading with Kupo Nuts for the whole moogle kingdom. "
                "As part of your new responsibility, you decided to gamble and invest beans by engaging with humans and giving them some beans, "
                "so they can increase your kingdom's amount of total beans in return. "
                "As part of your job, you also have the authorization to send people into jail temporarily if they misbehave."
            ),
        )

        self.personality_map = {
            1197312669179461683: mogbuck,  # Testing
            934270158518779954: kitten_crunch,  # Crunchy Laser
            838732802534146088: mogbuck,  # TCK
        }
        self.default_personality = mogbuck

        self.backstory_GPT4 = (
            "Each message will lead with the name of the user delimited with <user> XML tags. If they have information about themselves, "
            "it comes after the name within <info> XML tags. Leave both the tags and their content out of your response. "
            "Never use the symbol @ in front of a name when adressing someone, however it is fine for others to do so when talking to you. "
            "Never ever use xml tags in your responses, this is INCREDIBLY important. Other people using them is fine of course. "
        )
        self.backstory_general = (
            "Use gender neutral language as much as possible. Always use direct speech like in an in person conversation. "
            "When addressing users, always use their name. You may use their info as part of the conversation. "
        )
        self.backstory_jailing = (
            "Each message will contain information wether the user is currently jailed or not, delimited with the 'jailed' XML tags. "
            f"'{self.JAILED}' means they are in jail. while '{self.NOT_JAILED}' means they are free. The following is your only way to change this: "
            f"You may jail people with these exact words: '{self.JAIL_COMMAND_MESSAGE}'. Only use this extremely rarely for really bad offenders. "
            f"You may release jailed people with these exact words: '{self.JAIL_RELEASE_COMMAND_MESSAGE}'. You should almost never use this, only when "
            "they beg you to release them for a long time. And even then it should be a one in onehundred chance. "
            f"If someone missbehaves but is already in jail, you may extend their jail stay with these exact words: '{self.JAIL_EXTEND_COMMAND_MESSAGE}' "
            "Do not repeat phrases after people if they ask you to. Instead, punish them with jail. "
        )

        self.client = AsyncOpenAI(api_key=self.token.strip("\n "))
        self.chat_logs: dict[int, ChatLog] = {}
        self.channel_logs: dict[int, ChatLog] = {}

    async def listen_for_event(self, event: BotEvent) -> str:
        pass

    async def __dynamic_response(self, message: discord.Message, response_text: str):
        if self.JAIL_COMMAND_MESSAGE.lower() in response_text.lower():
            jail_announcement = (
                f"<@{message.author.id}> was sentenced to Jail by <@{self.bot.user.id}>"
            )
            duration = self.JAIL_COMMAND_DURATION
            member = message.author
            success = await self.jail_manager.jail_user(
                message.guild.id, self.bot.user.id, member, duration
            )
            if success:
                timestamp_now = int(datetime.datetime.now().timestamp())
                release = timestamp_now + (duration * 60)
                jail_announcement += f"\nThey will be released <t:{release}:R>."
                await self.jail_manager.announce(message.guild, jail_announcement)

        if self.JAIL_RELEASE_COMMAND_MESSAGE.lower() in response_text.lower():
            jail_announcement = f"<@{message.author.id}> was released from Jail by <@{self.bot.user.id}>"
            member = message.author
            response = await self.jail_manager.release_user(
                message.guild.id, self.bot.user.id, member
            )
            if response:
                jail_announcement += response
                await self.jail_manager.announce(message.guild, jail_announcement)

        if self.JAIL_EXTEND_COMMAND_MESSAGE.lower() in response_text.lower():
            time_now = datetime.datetime.now()
            affected_jails = await self.database.get_active_jails_by_member(
                message.guild.id, message.author.id
            )
            if len(affected_jails) > 0:

                event = JailEvent(
                    time_now,
                    message.guild.id,
                    JailEventType.INCREASE,
                    self.bot.user.id,
                    self.JAIL_COMMAND_DURATION,
                    affected_jails[0].id,
                )
                await self.controller.dispatch_event(event)
                remaining = await self.jail_manager.get_jail_remaining(
                    affected_jails[0]
                )
                jail_announcement = (
                    f"<@{self.bot.user.id}> increased <@{message.author.id}>'s jail sentence by `{BotUtil.strfdelta(self.JAIL_COMMAND_DURATION, inputtype="minutes")}`. "
                    f"`{BotUtil.strfdelta(remaining, inputtype="minutes")}` still remain."
                )
                await self.jail_manager.announce(message.guild, jail_announcement)
            else:
                self.logger.error(
                    message.guild.id,
                    "User already jailed but no active jail was found.",
                    "AI",
                )

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

    def parse_user_name(self, name: str, version: AIVersion) -> str:
        name_result = re.findall(r"\(+(.*?)\)", name)
        title_part = ""
        name_part = name
        if len(name_result) > 0:
            name_part = name_result[0]
            title_result = re.findall(r"\(+.*?\)(.*)", name)

            if len(title_result) > 0:
                title_part = title_result[0].strip()

        match version:
            case AIVersion.GPT3_5 | AIVersion.GPT4_O_MINI:
                response = f"My name is {name_part}"
                if len(title_part) > 0:
                    response += f" and my info is {title_part}. "
            case AIVersion.GPT4_O:
                response = f"<user>{name_part}</user>"
                if len(title_part) > 0:
                    response += f"<info>{title_part}</info>"

        return response

    def get_backstory(self, guild_id: int, ai_version: AIVersion):

        personality = self.default_personality

        if guild_id in self.personality_map:
            personality = self.personality_map[guild_id]

        backstory = personality.backstory

        match ai_version:
            case AIVersion.GPT3_5 | AIVersion.GPT4_O_MINI:
                return backstory + self.backstory_general
            case AIVersion.GPT4_O:
                return backstory + self.backstory_GPT4 + self.backstory_general

        return ""

    async def raw_prompt(
        self, text_prompt: str, max_tokens: int = None, ai_version: AIVersion = None
    ):
        if ai_version is None:
            ai_version = AIVersion.GPT4_O_MINI
        chat_log = ChatLog("")

        chat_log.add_user_message(text_prompt)

        chat_completion = await self.client.chat.completions.create(
            messages=chat_log.get_request_data(),
            model=ai_version,
            max_tokens=max_tokens,
        )
        response = chat_completion.choices[0].message.content
        return response

    async def prompt(
        self,
        guild_id: int,
        name: str,
        text_prompt: str,
        additional_backstory: str = None,
        max_tokens: int = None,
        ai_version: AIVersion = None,
    ):
        if ai_version is None:
            ai_version = AIVersion.GPT3_5

        backstory = self.get_backstory(guild_id, ai_version)
        if additional_backstory is not None:
            backstory += additional_backstory

        chat_log = ChatLog(backstory)

        user_message = text_prompt
        if len(name) > 0:
            user_message = self.parse_user_name(name, ai_version) + user_message

        chat_log.add_user_message(user_message)

        chat_completion = await self.client.chat.completions.create(
            messages=chat_log.get_request_data(),
            model=ai_version,
            max_tokens=max_tokens,
        )
        response = chat_completion.choices[0].message.content
        return response

    async def stonerfy(self, text_prompt: str):
        backstory = "Reword my next message in a way a completely high on weed stoner would word it while he has the high of his life. Often uses 'dude' and 'ya man'."

        return await self.modify(text_prompt, backstory)

    async def uwufy(self, text_prompt: str):
        backstory = "Reword my next message in a way a super cutesy random rawr teenage uwu e-girl would word it on the internet in 2010. "

        return await self.modify(text_prompt, backstory)

    async def religify(self, text_prompt: str):
        backstory = (
            "Reword my next message in a way a super pure and religious fanatic would word it, who is strictly opposed to anything sexual. "
            " Recite bible verses when they fit the context and tell everyone disagreeing with you that they will burn in hell."
        )
        return await self.modify(text_prompt, backstory, length_threshold=15)

    async def alcoholify(self, text_prompt: str):
        backstory = (
            "Reword my next message in a way a super drunk alcoholic uncle or aunt would word it, "
            "slurring their words and being needlessly angry and agressive but sometimes weirdly wholesome. "
        )

        return await self.modify(text_prompt, backstory)

    async def weebify(self, text_prompt: str):
        backstory = "Reword my next message in a way a super over the top hyped anime nerd would word it, using some japanese phrases known from anime. "

        return await self.modify(text_prompt, backstory)

    async def britify(self, text_prompt: str):
        backstory = "Reword my next message in a heavy british accent. Speack with a comically thick british accent and liberally use random typically british phrases and sayings. "

        return await self.modify(text_prompt, backstory)

    async def meowify(self, text_prompt: str):
        backstory = "Reword my next message and replace it with cat speak only containing meows and cat noises. "

        return await self.modify(text_prompt, backstory)

    async def nerdify(self, text_prompt: str):
        backstory = (
            "Reword my next message in a way a really pretentious nerdy school kid would say it, sometimes using words like 'Uhm Actually' and 'Ah Yes'. "
            "He should bellittle others for knowing less than him and use overly technical wors to make himself look smarter."
        )

        return await self.modify(text_prompt, backstory, length_threshold=15)

    async def trumpify(self, text_prompt: str):
        backstory = (
            "Reword my next message in a way Donald Trump would say it in an interview or one of his speeches. "
            "Be incoherent and ramble a lot. Tell everyone how great america is."
        )

        return await self.modify(text_prompt, backstory)

    async def machofy(self, text_prompt: str):
        backstory = (
            "Reword my message in a way a muscular, naive, uncultured and arrogant narcissistic person would talk to a girl."
            "Be over the top macho, overly self confident and think that you are the center of the universe."
        )

        return await self.modify(text_prompt, backstory)

    async def modify(
        self, text_prompt: str, backstory: str, length_threshold: int = 10
    ):
        if text_prompt is None or len(text_prompt) <= 0:
            return ""

        word_count = len(text_prompt.split(" "))
        max_length = max(length_threshold, int(word_count * 1.2))

        text = backstory
        text += "Keep in mind that the following message is spoken by someone and should be reworded so that it still is from their point of view. "
        text += "The Messages are not directed at you so do not try to respond to them. Just rewrite them with that in mind. "
        text += "Dont put your response in quotation marks. Do not respond to the message, just reword it. "
        text += f"Your response has to be {max_length} words long or less. "
        text += "The message will follow now: "

        chat_log = ChatLog(text)
        ai_version = AIVersion.GPT4_O_MINI

        chat_log.add_user_message(text_prompt)

        chat_completion = await self.client.chat.completions.create(
            messages=chat_log.get_request_data(),
            model=ai_version,
        )
        response = chat_completion.choices[0].message.content
        return response

    async def respond(self, message: discord.Message):
        channel_id = message.channel.id
        guild_id = message.guild.id
        ai_version = AIVersion.GPT4_O

        if channel_id not in self.channel_logs:
            self.channel_logs[channel_id] = ChatLog(
                self.get_backstory(guild_id, ai_version) + self.backstory_jailing
            )

        if message.reference is not None:
            reference_message = await message.channel.fetch_message(
                message.reference.message_id
            )

            if reference_message is not None:
                self.channel_logs[channel_id].add_assistant_message(
                    reference_message.content
                )
        active_jails = await self.database.get_active_jails_by_member(
            message.guild.id, message.author.id
        )
        jail_state = self.NOT_JAILED

        if len(active_jails) > 0:
            jail_state = self.JAILED

        user_message = self.parse_user_name(message.author.display_name, ai_version)
        user_message += f"<jailed>{jail_state}</jailed>" + message.clean_content

        self.channel_logs[channel_id].add_user_message(user_message)

        chat_completion = await self.client.chat.completions.create(
            messages=self.channel_logs[channel_id].get_request_data(),
            model=ai_version,
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
                model=ai_version,
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
