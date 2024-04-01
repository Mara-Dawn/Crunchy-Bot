from CrunchyBot import CrunchyBot
from cogs.beans.BeansBasics import BeansBasics
from cogs.beans.Lottery import Lottery
from cogs.beans.RandomLoot import RandomLoot

class Beans(BeansBasics, Lottery, RandomLoot, group_name='beans'):
    
    def __init__(self, bot: CrunchyBot):
        super().__init__(bot)

async def setup(bot):
    await bot.add_cog(Beans(bot))