import datetime
import discord

from MaraBot import MaraBot
from cogs.Jail import Jail
from events.BeansEventType import BeansEventType
from shop.ItemType import ItemType

class ArrestView(discord.ui.View):
    
    def __init__(self, bot: MaraBot, interaction: discord.Interaction):
        self.bot = bot
        self.interaction = interaction
        self.selected: discord.Member = None
        self.event_manager = bot.event_manager
        self.item_manager = bot.item_manager
        self.database = bot.database
        self.logger = bot.logger
        super().__init__(timeout=100)
        self.add_item(UserPicker())
        self.add_item(JailButton())

    async def set_selected(self, interaction: discord.Interaction, member: discord.Member):
        self.selected = member
        await interaction.response.defer()
    
    async def jail(self, interaction: discord.Interaction):
        
        await interaction.response.defer(ephemeral=True)
        
        if self.selected is None:
            await interaction.followup.send('Please select a user first.', ephemeral=True)
            return
        
        if self.selected.guild_permissions.administrator:
            await interaction.followup.send('Administrators cannot be jailed.', ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        item = self.item_manager.get_item(guild_id, ItemType.ARREST)
        
        if user_balance < item.get_cost():
            await interaction.followup.send('You dont have enough beans to buy that.', ephemeral=True)
            return
        
        duration = 30
        jail_cog: Jail = self.bot.get_cog('Jail')
        success = await jail_cog.jail_user(guild_id, member_id, self.selected, duration)
        
        if not success:
            await interaction.followup.send(f'User {self.selected.display_name} is already in jail.', ephemeral=True)
            return
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.SHOP_PURCHASE, 
            member_id,
            -item.get_cost()
        )
        
        log_message = f'{interaction.user.display_name} bought {item.get_name()} for {item.get_cost()} beans and jailed {self.selected.display_name}.'
        self.logger.log(interaction.guild_id, log_message, cog='Shop')
        
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        success_message = f'You successfully bought one **{item.get_name()}** for `🅱️{item.get_cost()}` beans, jailing {self.selected.display_name} for 30 minutes.\n Remaining balance: `🅱️{new_user_balance}`'
        self.clear_items()
        await interaction.followup.send(success_message, ephemeral=True)
        
        timestamp_now = int(datetime.datetime.now().timestamp())
        release = timestamp_now + (duration*60)
        await interaction.channel.send(f'<@{self.selected.id}> was sentenced to Jail by <@{member_id}>. They will be released <t:{release}:R>.', delete_after=(duration*60))
        
        message = await interaction.original_response()
        await message.delete()
        

    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)
    
class UserPicker(discord.ui.UserSelect):
    
    def __init__(self):
        super().__init__(placeholder='Choose a User to jail', min_values=1, max_values=1, row=0)

    
    async def callback(self, interaction: discord.Interaction):
        view: ArrestView = self.view
        await view.set_selected(interaction, self.values[0])
        
class JailButton(discord.ui.Button):
    
    def __init__(self):
        super().__init__(label='Jail', style=discord.ButtonStyle.red, row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view: ArrestView = self.view
        
        await view.jail(interaction)