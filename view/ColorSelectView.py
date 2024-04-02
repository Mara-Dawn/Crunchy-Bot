import datetime
import re
import discord

from CrunchyBot import CrunchyBot
from events.BeansEventType import BeansEventType
from shop.Item import Item
from shop.ItemType import ItemType
from view.ShopConfirmView import AmountInput, CancelButton, ConfirmButton, ShopConfirmView

class ColorSelectView(ShopConfirmView):
    
    def __init__(self, bot: CrunchyBot, interaction: discord.Interaction, parent, item: Item):
        super().__init__(bot, interaction, parent, item)
        self.color: str = None
        self.role_manager = bot.role_manager
        self.clear_items()
        default_color = bot.database.get_custom_color(interaction.guild_id, interaction.user.id)
        self.add_item(ColorInputButton(default_color))
        self.add_item(ConfirmButton())
        self.add_item(CancelButton())
        
        if item.get_allow_amount():
            self.add_item(AmountInput(suffix=' Week(s)'))
        
    async def refresh_embed(self, interaction: discord.Interaction):
        message = await interaction.original_response()
        color = discord.Colour.purple()
        if self.color is not None:
            hex_value = int(self.color, 16)
            color = discord.Color(hex_value)
        
        embed = self.item.get_embed(
            color=color,
            amount_in_cart=self.selected_amount
        )
        
        if self.selected_amount > 1:
            embed.title = f'{self.selected_amount}x {embed.title}'
        if self.color is not None:
            embed.title = f'{embed.title} [{self.color}]'
            
        await message.edit(embed=embed)
    
    async def set_color(self, interaction: discord.Interaction,  color: str):
        self.color = color.lstrip('#')
        await self.refresh_embed(interaction)
    
    async def set_amount(self, interaction: discord.Interaction, amount: int):
        self.selected_amount = amount
        await self.refresh_embed(interaction)
    
    async def submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        if self.color is None:
            await interaction.followup.send('Please select a color first.', ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        amount = self.selected_amount
        cost = self.item.get_cost() * amount
        
        if user_balance < cost:
            await interaction.followup.send('You dont have enough beans to buy that.', ephemeral=True)
            return
        
        beans_event_id = self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.SHOP_PURCHASE, 
            member_id,
            -cost
        )
        
        match self.type:
            case ItemType.NAME_COLOR:
                pass
                self.database.log_custom_color(guild_id, member_id, self.color)
                await self.item.obtain(
                    role_manager=self.role_manager,
                    event_manager=self.event_manager,
                    guild_id=guild_id,
                    member_id=member_id,
                    beans_event_id=beans_event_id,
                    amount=self.item.get_base_amount()*amount
                )
                
            case _:
                await interaction.followup.send(f'Something went wrong, please contact a staff member.', ephemeral=True)
                return
        
        
        
        log_message = f'{interaction.user.display_name} bought {amount} {self.item.get_name()} for {cost} beans'
        self.logger.log(interaction.guild_id, log_message, cog='Shop')
        
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        success_message = f'You successfully bought {amount} **{self.item.get_name()}** for `🅱️{self.item.get_cost()}` beans.\n Remaining balance: `🅱️{new_user_balance}`'
        
        await interaction.followup.send(success_message, ephemeral=True)
        
        message = await self.interaction.original_response()
        self.parent.refresh_ui(new_user_balance)
        await message.edit(view=self.parent)
        
        message = await interaction.original_response()
        await message.delete()

class ColorInputButton(discord.ui.Button):
    
    def __init__(self, default_color: str):
        super().__init__(label='Pick a Color', style=discord.ButtonStyle.green, row=1)
        self.default_color = default_color
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ColorInputModal(self.view, self.default_color))

class ColorInputModal(discord.ui.Modal):

    def __init__(self, view: ColorSelectView, default_color: str):
        super().__init__(title='Choose a Color')
        self.view = view
        if default_color is not None:
            default_color = f'#{default_color}'
        self.hex_color = discord.ui.TextInput(
            label='Hex Color Code',
            placeholder='#FFFFFF',
            default=default_color
        )
        self.add_item(self.hex_color)
    

    async def on_submit(self, interaction: discord.Interaction): 
        await interaction.response.defer()
        hex_string = self.hex_color.value
        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hex_string)
        if not match:                      
            await interaction.followup.send('Please enter a valid hex color value.', ephemeral=True)
            return
        
        await self.view.set_color(interaction, hex_string)