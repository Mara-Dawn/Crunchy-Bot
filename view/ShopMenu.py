import datetime
from typing import List
import discord

from MaraBot import MaraBot
from events.BeansEventType import BeansEventType
from shop.IsntantItem import InstantItem
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from view.InventoryEmbed import InventoryEmbed
from view.ShopEmbed import ShopEmbed

from view.ShopUserSelectView import ShopUserSelectView
from view.ShopConfirmView import ShopConfirmView

class ShopMenu(discord.ui.View):
    
    def __init__(self, bot: MaraBot, interaction: discord.Interaction, items: List[Item]):
        self.interaction = interaction
        self.bot = bot
        self.event_manager = bot.event_manager
        self.item_manager = bot.item_manager
        self.database = bot.database
        self.logger = bot.logger
        self.current_page = 0
        self.selected: ItemType = None
        super().__init__(timeout=200)
        self.items = items
        self.items.sort(key=lambda x:x.get_cost())
        self.item_count = len(self.items)
        self.page_count = int(self.item_count / ShopEmbed.ITEMS_PER_PAGE) + (self.item_count % ShopEmbed.ITEMS_PER_PAGE > 0)
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        self.refresh_ui(user_balance)
        
    async def buy(self, interaction: discord.Interaction):
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
        
        if item.get_group() == ItemGroup.IMMEDIATE_USE:
            await interaction.response.defer(ephemeral=True)
        
            item: InstantItem = item
            embed = item.get_embed()
            view_class_name = item.get_view_class()
            
            view_class = globals()[view_class_name]
            view = view_class(self.bot, interaction, self, item)
            
            message = await interaction.followup.send(f"", embed=embed, view=view, ephemeral=True)
            view.set_message(message)
            
            self.refresh_ui(user_balance, disabled=True)
            await interaction.message.edit(view=self)
            
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
            item.get_base_amount()
        )
        
        log_message = f'{interaction.user.display_name} bought {item.get_name()} for {item.get_cost()} beans.'
        self.logger.log(interaction.guild_id, log_message, cog='Shop')
        
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        success_message = f'You successfully bought one **{item.get_name()}** for `🅱️{item.get_cost()}` beans. Remaining balance: `🅱️{new_user_balance}`\n Use */inventory* to check your inventory.'
        
        await interaction.response.send_message(success_message, ephemeral=True)
        
        self.refresh_ui(new_user_balance)
        await interaction.message.edit(view=self)
    
        
    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        self.current_page = (self.current_page +(1 if right else -1)) % self.page_count
        start = ShopEmbed.ITEMS_PER_PAGE * self.current_page
        
        embed = ShopEmbed(self.bot, interaction, self.items, start)

        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        self.refresh_ui(user_balance)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    def refresh_ui(self, user_balance: int, disabled: bool = False):
        start = ShopEmbed.ITEMS_PER_PAGE * self.current_page
        end = min((start + ShopEmbed.ITEMS_PER_PAGE), self.item_count)
        page_display = f'Page {self.current_page + 1}/{self.page_count}'
        self.clear_items()
        self.add_item(Dropdown(self.items[start:end], self.selected, disabled))
        self.add_item(PageButton("<", False, disabled))
        self.add_item(BuyButton(disabled))
        self.add_item(PageButton(">", True, disabled))
        self.add_item(CurrentPageButton(page_display))
        self.add_item(BalanceButton(self.bot, user_balance))
    
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

class BuyButton(discord.ui.Button):
    
    def __init__(self, disabled: bool = False):
        super().__init__(label='Buy', style=discord.ButtonStyle.green, row=1, disabled=disabled)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopMenu = self.view
        
        if await view.interaction_check(interaction):
            await view.buy(interaction)

class PageButton(discord.ui.Button):
    
    def __init__(self, label: str, right: bool, disabled: bool = False):
        self.right = right
        super().__init__(label=label, style=discord.ButtonStyle.grey, row=1, disabled=disabled)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopMenu = self.view
        
        if await view.interaction_check(interaction):
            await view.flip_page(interaction, self.right)
            
class CurrentPageButton(discord.ui.Button):
    
    def __init__(self, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.grey, row=1, disabled=True)
        
class BalanceButton(discord.ui.Button):
    
    def __init__(self, bot: MaraBot, balance: int):
        self.bot = bot
        self.database = bot.database
        self.balance = balance
        super().__init__(label=f'🅱️{balance}', style=discord.ButtonStyle.blurple, row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopMenu = self.view
        
        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)
            
            police_img = discord.File("./img/police.png", "police.png")
        
            member_id = interaction.user.id
            guild_id = interaction.guild_id
            inventory = self.database.get_inventory_by_user(guild_id, member_id)
            
            embed = InventoryEmbed(self.bot, interaction, inventory, self.balance)
            
            await interaction.followup.send(f"", embed=embed, files=[police_img], ephemeral=True)
    

class Dropdown(discord.ui.Select):
    
    def __init__(self, items: List[Item], selected: ItemType, disabled: bool = False):
        
        options = []
        
        for item in items:
            option = discord.SelectOption(
                label=item.get_name(),
                description='', 
                emoji=item.get_emoji(), 
                value=item.get_type(),
                default=(selected==item.get_type())
            )
            
            options.append(option)

        super().__init__(placeholder='Select an item.', min_values=1, max_values=1, options=options, row=0, disabled=disabled)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopMenu = self.view
        
        if await view.interaction_check(interaction):
            await view.set_selected(interaction, self.values[0])