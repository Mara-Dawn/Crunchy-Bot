import discord
from items.item import Item
from items.types import ItemType


class ShopEmbed(discord.Embed):

    ITEMS_PER_PAGE = 5

    def __init__(
        self,
        author_name,
        author_img,
        guild_name: str,
        items: list[Item],
        user_items: dict[ItemType, int] = None,
        start_offset: int = 0,
    ):
        description = "Spend your hard earned beans!\n"
        description += (
            "Use `/inventory` or the balance button below to see your inventory. \n"
        )
        super().__init__(
            title=f"Beans Shop for {guild_name}",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_author(name=author_name, icon_url=author_img)
        end_offset = min((start_offset + self.ITEMS_PER_PAGE), len(items))
        display = items[start_offset:end_offset]

        for item in display:
            owned = None
            if user_items is not None and item.type in user_items:
                owned = user_items[item.type]
            item.add_to_embed(self, 44, count=owned, show_price=True)

        self.set_image(url="attachment://shop.png")
