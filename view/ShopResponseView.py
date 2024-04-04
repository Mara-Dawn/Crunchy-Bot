import datetime
import re
from typing import List
import discord

from CrunchyBot import CrunchyBot
from events.BeansEventType import BeansEventType
from shop.Item import Item
from view import ShopMenu
from view.EmojiType import EmojiType

class ShopResponseView(discord.ui.View):
    
    def __init__(self, bot: CrunchyBot, interaction: discord.Interaction, parent: ShopMenu, item: Item):
        self.bot = bot
        self.parent = parent
        self.interaction = interaction
        self.type = None
        if item is not None:
            self.type = item.get_type()
        self.item = item
        self.event_manager = bot.event_manager
        self.item_manager = bot.item_manager
        self.role_manager = bot.role_manager
        self.database = bot.database
        self.logger = bot.logger
        self.message = None
        
        self.selected_user: discord.Member = None
        self.selected_amount: int = 1
        self.selected_color: str = None
        self.selected_emoji: discord.Emoji|str = None
        self.selected_emoji_type: EmojiType = None
        
        self.confirm_button: ConfirmButton = None
        self.cancel_button: CancelButton = None
        self.user_select: UserPicker = None
        self.color_input_button: ColorInputButton = None
        self.amount_select: AmountInput = None
        self.reaction_input_button: ReactionInputButton = None
        
        super().__init__(timeout=200)

    async def submit(self, interaction: discord.Interaction):
        pass

    async def start_transaction(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        
        if self.item is not None:
            user_balance = self.database.get_member_beans(guild_id, member_id)
            
            amount = self.selected_amount
            cost = self.item.get_cost() * amount
            
            if user_balance < cost:
                await interaction.followup.send('You dont have enough beans to buy that.', ephemeral=True)
                return False
        
        if self.selected_user is not None and self.selected_user.bot:
            await interaction.followup.send(f"You cannot select bot users.", ephemeral=True)
            return False

        if self.user_select is not None and self.selected_user is None:
            await interaction.followup.send('Please select a user first.', ephemeral=True)
            return False
        
        if self.reaction_input_button is not None and self.selected_emoji is None:
            await interaction.followup.send('Please select a reaction emoji first.', ephemeral=True)
            return False
        
        if self.color_input_button is not None and self.selected_color is None:
            await interaction.followup.send('Please select a color first.', ephemeral=True)
            return False
        
        return True
        
    
    async def finish_transaction(self, interaction: discord.Interaction):
        amount = self.selected_amount
        cost = self.item.get_cost() * amount
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        
        log_message = f'{interaction.user.display_name} bought {amount} {self.item.get_name()} for {cost} beans.'
        
        arguments = []
        
        if self.selected_user is not None:
            arguments.append(f'selected_user: {self.selected_user.display_name}')
        
        if self.selected_color is not None:
            arguments.append(f'selected_color: {self.selected_color}')
            
        if self.selected_emoji is not None:
            arguments.append(f'selected_emoji: {str(self.selected_emoji)}')
        
        if len(arguments) > 0:
            log_message += ' arguments[' + ', '.join(arguments) + ']'
        
        self.logger.log(interaction.guild_id, log_message, cog='Shop')
        
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        success_message = f'You successfully bought {amount} **{self.item.get_name()}** for `🅱️{cost}` beans.\n Remaining balance: `🅱️{new_user_balance}`'
        
        await interaction.followup.send(success_message, ephemeral=True)
        
        message = await self.interaction.original_response()
        self.parent.refresh_ui(new_user_balance)
        await message.edit(view=self.parent)
        
        message = await interaction.original_response()
        await message.delete()
    
    def refresh_elements(self, disabled: bool = False):
        elements: List[discord.ui.Item] = [
            self.user_select,
            self.amount_select,
            self.color_input_button,
            self.reaction_input_button,
            self.confirm_button,
            self.cancel_button
        ]
        
        self.clear_items()
        for element in elements:
            if element is self.amount_select and not self.item.get_allow_amount():
                continue
            if element is not None:
                element.disabled = disabled
                self.add_item(element)
    
    async def refresh_ui(self, disabled: bool = False):
        color = discord.Colour.purple()
        if self.selected_color is not None:
            hex_value = int(self.selected_color, 16)
            color = discord.Color(hex_value)
        
        embed = self.item.get_embed(
            color=color,
            amount_in_cart=self.selected_amount
        )
        
        embed.title = f'{self.item.get_emoji()} {self.item.get_name()} {self.item.get_emoji()}'
        
        if self.selected_amount > 1:
            embed.title = f'{self.selected_amount}x {embed.title}'
        if self.selected_color is not None:
            embed.title = f'{embed.title} [#{self.selected_color}]'
        if self.selected_emoji is not None:
            embed.title = f'{embed.title} - Selected: {str(self.selected_emoji)}'
            
        embed.title = f'> {embed.title}'
        
        if self.amount_select is not None:
            self.amount_select.options[self.selected_amount-1].default = True
        
        self.refresh_elements(disabled)
        
        self.timeout = 210
        if disabled:
            self.timeout = 300
            
        await self.message.edit(embed=embed, view=self)
        
    async def set_amount(self, amount: int):
        self.amount_select.options[self.selected_amount-1].default = False
        self.selected_amount = amount
        await self.refresh_ui()

    async def set_selected(self, member: discord.Member):
        self.selected_user = member
        await self.refresh_ui()
    
    async def set_color(self, color: str):
        self.selected_color = color.lstrip('#')
        await self.refresh_ui()
    
    async def set_emoji(self, emoji: discord.Emoji|str, type: EmojiType):
        self.selected_emoji = emoji
        self.selected_emoji_type = type
        await self.refresh_ui()
    
    def set_message(self, message: discord.Message):
        self.message = message

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            await interaction.response.send_message(f"Only the author of the command can perform this action.", ephemeral=True)
            return False
    
    async def on_timeout(self):
        try:
            await self.message.delete()
            
            guild_id = self.interaction.guild_id
            member_id = self.interaction.user.id
            user_balance = self.database.get_member_beans(guild_id, member_id)
            
            message = await self.interaction.original_response()
            self.parent.refresh_ui(user_balance)
            await message.edit(view=self.parent)
        except:
            self.logger.log(self.interaction.guild_id, f'TIMEOUT: Interaction Lost.', cog='Shop')
        
class UserPicker(discord.ui.UserSelect):
    
    def __init__(self):
        super().__init__(placeholder='Select a user.', min_values=1, max_values=1, row=0)

    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        await interaction.response.defer()
        
        if await view.interaction_check(interaction):
            await view.set_selected(self.values[0])

class CancelButton(discord.ui.Button):
    
    def __init__(self):
        super().__init__(label='Cancel', style=discord.ButtonStyle.red, row=2)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        
        if await view.interaction_check(interaction):
            await view.on_timeout()

class ConfirmButton(discord.ui.Button):
    
    def __init__(self, label: str = 'Confirm and Buy'):
        super().__init__(label=label, style=discord.ButtonStyle.green, row=2)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        
        if await view.interaction_check(interaction):
            await view.submit(interaction)

class AmountInput(discord.ui.Select):
    
    def __init__(self, suffix: str = ''):
        options = []
        
        for i in range(1,20):
            options.append(discord.SelectOption(label=f'{i}{suffix}', value=i, default=(i==1)))

        super().__init__(placeholder='Choose the amount.', min_values=1, max_values=1, options=options, row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        await interaction.response.defer()
        if await view.interaction_check(interaction):
            await view.set_amount(int(self.values[0]))

class ColorInputButton(discord.ui.Button):
    
    def __init__(self, default_color: str):
        super().__init__(label='Pick a Color', style=discord.ButtonStyle.green, row=2)
        self.default_color = default_color
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopResponseView = self.view
        if await view.interaction_check(interaction):
            await interaction.response.send_modal(ColorInputModal(self.view, self.default_color))

class ColorInputModal(discord.ui.Modal):

    def __init__(self, view: ShopResponseView, default_color: str):
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
        
        await self.view.set_color(hex_string)

class ReactionInputButton(discord.ui.Button):
    
    def __init__(self):
        super().__init__(label='Select Emoji', style=discord.ButtonStyle.green, row=2)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        parent: ShopResponseView = self.view
        if await parent.interaction_check(interaction):
            await parent.refresh_ui(disabled=True)
            
            content = f"<@{interaction.user.id}> please react to this message with the emoji of your choice."
            view = ReactionInputView(parent.bot, interaction, parent, parent.item)
            message = await interaction.followup.send(content, view=view)
            view.set_message(message)

class ReactionInputView(ShopResponseView):
    
    def __init__(self, bot: CrunchyBot, interaction: discord.Interaction, parent, item: Item):
        super().__init__(bot, interaction, parent, item)
        self.parent: ShopResponseView = parent
        
        self.confirm_button = ConfirmButton("Confirm")
        self.cancel_button = CancelButton()
        
        self.refresh_elements()
    
    async def submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_emoji = None
        emoji_type = None
        
        message = await interaction.channel.fetch_message(self.message.id)
        
        for reaction in message.reactions:
            reactors = [user async for user in reaction.users()]
            if interaction.user in reactors:
                if user_emoji is not None:
                    await interaction.followup.send(f'Please react with a single emoji.', ephemeral=True)
                    return
                
                user_emoji = reaction.emoji
                emoji_type = EmojiType.CUSTOM if reaction.is_custom_emoji() else EmojiType.DEFAULT
        
        if user_emoji is None:
            await interaction.followup.send(f'Please react with any emoji.', ephemeral=True)
            return
        
        if emoji_type == EmojiType.CUSTOM:
            emoji_obj = discord.utils.get(self.bot.emojis, name=user_emoji.name)
            if emoji_obj is None:                      
                await interaction.followup.send(f'I do not have access to this emoji. I can only see the emojis of the servers i am a member of.', ephemeral=True)
                return
        
        await self.parent.set_emoji(user_emoji, emoji_type)
        await interaction.followup.delete_message(self.message.id)
        
    async def on_timeout(self):
        try:
            await self.message.delete()
            await self.parent.refresh_ui()
        except:
            self.logger.log(self.interaction.guild_id, f'TIMEOUT: Interaction Lost.', cog='Shop')