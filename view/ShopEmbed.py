import discord

from BotUtil import BotUtil
from MaraBot import MaraBot
from shop.Item import Item
from shop.ItemType import ItemType
from view.RankingType import RankingType

class ShopEmbed(discord.Embed):
    
    TITLES = {
        RankingType.SLAP: "Slap Rankings",
        RankingType.PET: "Pet Rankings",
        RankingType.FART: "Fart Rankings",
        RankingType.SLAP_RECIEVED: "Slaps Recieved Rankings",
        RankingType.PET_RECIEVED: "Pets Recieved  Rankings",
        RankingType.FART_RECIEVED: "Farts Recieved  Rankings",
        RankingType.TIMEOUT_TOTAL: "Total Timeout Duration Rankings",
        RankingType.TIMEOUT_COUNT: "Timeout Count Rankings",
        RankingType.JAIL_TOTAL: "Total Jail Duration Rankings",
        RankingType.JAIL_COUNT: "Jail Count Rankings",
        RankingType.SPAM_SCORE: "Spam Score Rankings",
    }
    
    def __init__(self, bot: MaraBot,  interaction: discord.Interaction):
        super().__init__(
            title=f"Beans Shop for {interaction.guild.name}",
            color=discord.Colour.purple(),
            description='Spend your hard earned beans here!'
        )
        
        self.item_manager = bot.item_manager
        items = [x.value for x in ItemType]
        
        self.add_field(name='', value='', inline=False)
        max_len = 49
        for item_name in items:
            item: Item = self.item_manager.get_item(interaction.guild_id, item_name)
            
            title = f'> ~*  {item.get_name()}  *~'
            description = item.get_description()
            cost = f'🅱️{item.get_cost()}'
            spacing = max_len - len(cost)
            info_block = f'```{description}\n\n{' '*spacing}{cost}```'
            
            self.add_field(name=title, value=info_block, inline=False)
            
        self.set_image(url="attachment://shop.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
