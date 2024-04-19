import discord
from items.item import Item
from items.types import ItemType


class ShopEmbed(discord.Embed):

    ITEMS_PER_PAGE = 5

    def __init__(
        self,
        guild_name: str,
        user_id: int,
        items: list[Item],
        user_items: dict[ItemType, int] = None,
        start_offset: int = 0,
    ):
        description = "Spend your hard earned beans!\n"
        # description += f"Only <@{user_id}> can interact here.\n"
        # description += "Use `/shop` to open your own shop widget.\n"
        description += (
            "Use `/inventory` or the balance button below to see your inventory. \n"
        )
        super().__init__(
            title=f"Beans Shop for {guild_name}",
            color=discord.Colour.purple(),
            description=description,
        )
        end_offset = min((start_offset + self.ITEMS_PER_PAGE), len(items))
        display = items[start_offset:end_offset]

        for item in display:
            owned = None
            if user_items is not None and item.type in user_items:
                owned = user_items[item.type]
            item.add_to_embed(self, 44, count=owned, show_price=True)

        self.set_image(url="attachment://shop.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
