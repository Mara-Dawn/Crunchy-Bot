import datetime
import discord

from MaraBot import MaraBot
from cogs.Jail import Jail
from events.BeansEventType import BeansEventType
from shop.ItemType import ItemType

class ReleaseView(discord.ui.View):
    
    def __init__(self, bot: MaraBot, interaction: discord.Interaction, parent):
        self.bot = bot
        self.parent = parent
        self.interaction = interaction
        self.selected: discord.Member = None
        self.event_manager = bot.event_manager
        self.item_manager = bot.item_manager
        self.database = bot.database
        self.logger = bot.logger
        self.message = None
        super().__init__(timeout=100)
        self.add_item(UserPicker())
        self.add_item(ReleaseButton())
        self.add_item(CancelButton())

    async def set_selected(self, interaction: discord.Interaction, member: discord.Member):
        self.selected = member
        await interaction.response.defer()
    
    async def release(self, interaction: discord.Interaction):
        
        await interaction.response.defer(ephemeral=True)
        
        if self.selected is None:
            await interaction.followup.send('Please select a user first.', ephemeral=True)
            return
        
        if self.selected.id == interaction.user.id:
            await interaction.followup.send('You cannot free yourself using this item.', ephemeral=True)
            return
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        item = self.item_manager.get_item(guild_id, ItemType.RELEASE)
        
        if user_balance < item.get_cost():
            await interaction.followup.send('You dont have enough beans to buy that.', ephemeral=True)
            return
        
        jail_cog: Jail = self.bot.get_cog('Jail')
        response = await jail_cog.release_user(guild_id, member_id, self.selected)
        
        if not response:
            await interaction.followup.send(f'User {self.selected.display_name} is currently not in jail.', ephemeral=True)
            return
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.SHOP_PURCHASE, 
            member_id,
            -item.get_cost()
        )
        
        log_message = f'{interaction.user.display_name} bought {item.get_name()} for {item.get_cost()} beans and freed {self.selected.display_name} from jail.'
        self.logger.log(interaction.guild_id, log_message, cog='Shop')
        
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        success_message = f'You successfully bought one **{item.get_name()}** for `🅱️{item.get_cost()}` beans, releasing {self.selected.display_name} from jail.\n Remaining balance: `🅱️{new_user_balance}`'
        
        await interaction.followup.send(success_message, ephemeral=True)
        
        response = f'<@{self.selected.id}> was generously released from Jail by <@{interaction.user.id}> using a **{item.get_name()}**. ' + response
        await jail_cog.announce(interaction.guild, response)
        
        message = await self.interaction.original_response()
        self.parent.refresh_ui(new_user_balance)
        await message.edit(view=self.parent)
        
        message = await interaction.original_response()
        await message.delete()
    
    def set_message(self, message: discord.Message):
        self.message = message

    async def on_timeout(self):
        # remove message
        await self.message.delete()
        
        guild_id = self.interaction.guild_id
        member_id = self.interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        message = await self.interaction.original_response()
        self.parent.refresh_ui(user_balance)
        await message.edit(view=self.parent)
    
class UserPicker(discord.ui.UserSelect):
    
    def __init__(self):
        super().__init__(placeholder='Choose a User to Release', min_values=1, max_values=1, row=0)

    
    async def callback(self, interaction: discord.Interaction):
        view: ReleaseView = self.view
        await view.set_selected(interaction, self.values[0])
        
class ReleaseButton(discord.ui.Button):
    
    def __init__(self):
        super().__init__(label='Release', style=discord.ButtonStyle.green, row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view: ReleaseView = self.view
        
        await view.release(interaction)

class CancelButton(discord.ui.Button):
    
    def __init__(self):
        super().__init__(label='Cancel', style=discord.ButtonStyle.grey, row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view: ReleaseView = self.view
        
        await view.on_timeout()