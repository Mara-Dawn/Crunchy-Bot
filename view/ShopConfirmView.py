import datetime
import discord

from MaraBot import MaraBot
from cogs.Jail import Jail
from events.BeansEventType import BeansEventType
from shop.IsntantItem import InstantItem
from shop.ItemType import ItemType

class ShopConfirmView(discord.ui.View):
    
    def __init__(self, bot: MaraBot, interaction: discord.Interaction, parent, item: InstantItem):
        self.bot = bot
        self.parent = parent
        self.interaction = interaction
        self.type = item.get_type()
        self.item = item
        self.event_manager = bot.event_manager
        self.item_manager = bot.item_manager
        self.database = bot.database
        self.logger = bot.logger
        self.message = None
        super().__init__(timeout=100)
        self.add_item(ConfirmButton())
        self.add_item(CancelButton())

    
    async def submit(self, interaction: discord.Interaction):
        match self.type:
            case ItemType.BAILOUT:
                await self.jail_interaction(interaction)
    
    async def jail_interaction(self, interaction: discord.Interaction):
        
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        if user_balance < self.item.get_cost():
            await interaction.followup.send('You dont have enough beans to buy that.', ephemeral=True)
            return
        
        jail_cog: Jail = self.bot.get_cog('Jail')
        
        match self.type:
            case ItemType.BAILOUT:
                response = await jail_cog.release_user(guild_id, member_id, interaction.user)
        
                if not response:
                    await interaction.followup.send(f'You are currently not in jail.', ephemeral=True)
                    return
                
                log_message_suffix = f'and freed themselves from jail.'
                message_suffix = f'freeing themselves from jail.'
                jail_announcement = f'<@{member_id}> was released from Jail by bribing the mods with beans. ' + response
                
            case _:
                await interaction.followup.send(f'Something went wrong, please contact a staff member.', ephemeral=True)
                return
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.SHOP_PURCHASE, 
            member_id,
            -self.item.get_cost()
        )
        
        log_message = f'{interaction.user.display_name} bought {self.item.get_name()} for {self.item.get_cost()} beans {log_message_suffix}'
        self.logger.log(interaction.guild_id, log_message, cog='Shop')
        
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        success_message = f'You successfully bought one **{self.item.get_name()}** for `🅱️{self.item.get_cost()}` beans, {message_suffix}.\n Remaining balance: `🅱️{new_user_balance}`'
        
        await interaction.followup.send(success_message, ephemeral=True)
        
        await jail_cog.announce(interaction.guild, jail_announcement)
        
        message = await self.interaction.original_response()
        self.parent.refresh_ui(new_user_balance)
        await message.edit(view=self.parent)
        
        message = await interaction.original_response()
        await message.delete()
    
    def set_message(self, message: discord.Message):
        self.message = message

    async def on_timeout(self):
        try:
            await self.message.delete()
        except:
            pass
        
        guild_id = self.interaction.guild_id
        member_id = self.interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        message = await self.interaction.original_response()
        self.parent.refresh_ui(user_balance)
        await message.edit(view=self.parent)
        
class ConfirmButton(discord.ui.Button):
    
    def __init__(self):
        super().__init__(label='Confirm and Buy', style=discord.ButtonStyle.green, row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopConfirmView = self.view
        
        await view.submit(interaction)

class CancelButton(discord.ui.Button):
    
    def __init__(self):
        super().__init__(label='Cancel', style=discord.ButtonStyle.grey, row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view: ShopConfirmView = self.view
        
        await view.on_timeout()