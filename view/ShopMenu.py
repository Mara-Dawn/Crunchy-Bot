from typing import List
import discord

from MaraBot import MaraBot
from datalayer.UserRankings import UserRankings
from shop.Item import Item
from shop.ItemType import ItemType
from view.RankingEmbed import RankingEmbed
from view.RankingType import RankingType
from view.ShopEmbed import ShopEmbed

class ShopMenu(discord.ui.View):
    
    def __init__(self, bot: MaraBot, interaction: discord.Interaction, items: List[Item]):
        self.interaction = interaction
        self.bot = bot
        self.event_manager = bot.event_manager
        self.item_manager = bot.item_manager
        self.database = bot.database
        super().__init__(timeout=100)
        self.items = items
        self.add_item(Dropdown(items))
        self.selected = None


    @discord.ui.button(label='>       Buy       <', style=discord.ButtonStyle.green, row=1)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.selected is None:
            await interaction.response.send_message('Please select an Item first.', ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        item = self.item_manager.get_item(self.selected)
        
        if user_balance < item.get_cost():
            pass

    async def set_selected(self, interaction: discord.Interaction, item_type: ItemType):
        self.selected = item_type
        await interaction.response.defer()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            embed = discord.Embed(
                description=f"Only the author of the command can perform this action.",
                color=16711680
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
    
    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)

class Dropdown(discord.ui.Select):
    
    def __init__(self, items: List[Item]):
        
        options = []
        
        for item in items:
            option = discord.SelectOption(
                label=item.get_name(),
                description=item.get_description(), 
                emoji=item.get_emoji(), 
                value=item.get_type())
            options.append(option)

        super().__init__(placeholder='Select an item.', min_values=1, max_values=1, options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopMenu = self.view
        
        if await view.interaction_check(interaction):
            await view.set_selected(interaction, self.values[0])