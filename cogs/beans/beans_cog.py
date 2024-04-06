from cogs.beans.beans_basics_cog import BeansBasics
from cogs.beans.lottery_cog import Lottery
from cogs.beans.random_loot_cog import RandomLoot


class Beans(BeansBasics, Lottery, RandomLoot, group_name="beans"):
    pass


async def setup(bot) -> None:
    await bot.add_cog(Beans(bot))
