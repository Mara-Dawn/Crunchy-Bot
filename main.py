
import discord
import logging
from logging.handlers import TimedRotatingFileHandler

TOKEN_FILE = 'key.txt'

class MommyBot(discord.Client):

    LIMIT_ROLE = 551066138860060682;
    RATE_LIMIT = 60

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.naughty_list = {}

    async def on_message(self, message):
        author_id = message.author.id

        if author_id == self.user.id:
            return
        
        if self.LIMIT_ROLE in [x.id for x in message.author.roles]:
            # user has the right role

            if author_id not in self.naughty_list.keys():
                self.naughty_list[author_id] = {"timestamp": message.created_at, "notified" : False}
                return

            naughty_user = self.naughty_list[author_id]

            difference = message.created_at - naughty_user["timestamp"]

            if difference.total_seconds() < self.RATE_LIMIT:
                if not naughty_user["notified"]:
                    await message.channel.send(f'<@{author_id}> Stop spamming, bitch! try again in {self.RATE_LIMIT - int(difference.total_seconds())} seconds.')
                    self.naughty_list[author_id]["notified"] = True
                await message.delete()
            else:
                self.naughty_list[author_id] = {"timestamp": message.created_at, "notified" : False}




logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.TimedRotatingFileHandler("mommybot.log",'midnight', 1, 5, 'utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True

bot = MommyBot(intents=intents)

token = open(TOKEN_FILE,"r").readline()
bot.run(token, log_handler=None)


#Set-ExecutionPolicy Unrestricted -Scope Process
