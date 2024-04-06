from cogs.beans import BeansBasics, Lottery, RandomLoot


class Beans(BeansBasics, Lottery, RandomLoot, group_name="beans"):
    pass


async def setup(bot) -> None:
    await bot.add_cog(Beans(bot))
