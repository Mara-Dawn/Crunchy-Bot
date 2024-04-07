from cogs.beans.beans_basics import BeansBasics
from cogs.beans.lottery import Lottery
from cogs.beans.random_loot import RandomLoot


class Beans(BeansBasics, Lottery, RandomLoot, group_name="beans"):
    pass


async def setup(bot) -> None:
    await bot.add_cog(Beans(bot))