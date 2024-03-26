import datetime
from typing import List
import discord

from MaraBot import MaraBot
from events.BeansEventType import BeansEventType
from shop.Item import Item
from shop.ItemType import ItemType
from view.ShopEmbed import ShopEmbed

class ShopMenu(discord.ui.View):
    
    def __init__(self, bot: MaraBot, interaction: discord.Interaction, items: List[Item]):
        self.interaction = interaction
        self.bot = bot
        self.event_manager = bot.event_manager
        self.item_manager = bot.item_manager
        self.database = bot.database
        self.logger = bot.logger
        super().__init__(timeout=100)
        self.items = items
        self.add_item(Dropdown(items))
        self.selected: ItemType = None


    @discord.ui.button(label='Buy', style=discord.ButtonStyle.green, row=1)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.interaction_check(interaction):
            return
        
        if self.selected is None:
            await interaction.response.send_message('Please select an Item first.', ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        item = self.item_manager.get_item(guild_id, self.selected)
        
        if user_balance < item.get_cost():
            await interaction.response.send_message('You dont have enough beans to buy that.', ephemeral=True)
            return
        
        beans_event_id = self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.SHOP_PURCHASE, 
            member_id,
            -item.get_cost()
        )
        
        self.event_manager.dispatch_inventory_event(
            datetime.datetime.now(), 
            guild_id,
            member_id,
            item.get_type(),
            beans_event_id,
            1
        )
        
        log_message = f'{interaction.user.display_name} bought {item.get_name()} for {item.get_cost()} beans.'
        self.logger.log(interaction.guild_id, log_message, cog='Shop')
        
        success_message = f'You successfully bought one **{item.get_name()}** for `{item.get_cost()}` beans.'
        await interaction.response.send_message(success_message, ephemeral=True)

    async def set_selected(self, interaction: discord.Interaction, item_type: ItemType):
        self.selected = item_type
        await interaction.response.defer()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            await interaction.response.send_message(f"Only the author of the command can perform this action.", ephemeral=True)
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