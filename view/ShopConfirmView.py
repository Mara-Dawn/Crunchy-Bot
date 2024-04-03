import datetime
import discord

from BotUtil import BotUtil
from CrunchyBot import CrunchyBot
from cogs.Jail import Jail
from events.BeansEventType import BeansEventType
from events.JailEventType import JailEventType
from shop.Item import Item
from shop.ItemType import ItemType
from view.ShopResponseView import *

class ShopConfirmView(ShopResponseView):
    
    def __init__(self, bot: CrunchyBot, interaction: discord.Interaction, parent, item: Item):
        super().__init__(bot, interaction, parent, item)
        
        self.add_item(ConfirmButton())
        self.add_item(CancelButton())
        
        self.select_amount = AmountInput()
        if item.get_allow_amount():
            self.add_item(self.select_amount)
    
    async def submit(self, interaction: discord.Interaction):
        match self.type:
            case ItemType.BAILOUT:
                await self.jail_interaction(interaction)
            case ItemType.JAIL_REDUCTION:
                await self.jail_interaction(interaction)
    
    async def jail_interaction(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        user_balance = self.database.get_member_beans(guild_id, member_id)
        
        amount = self.selected_amount
        cost = self.item.get_cost() * amount
        
        if user_balance < cost:
            await interaction.followup.send('You dont have enough beans to buy that.', ephemeral=True)
            return
        
        jail_cog: Jail = self.bot.get_cog('Jail')
        
        match self.type:
            case ItemType.BAILOUT:
                response = await jail_cog.release_user(guild_id, member_id, interaction.user)
        
                if not response:
                    await interaction.followup.send(f'You are currently not in jail.', ephemeral=True)
                    return
                
                jail_announcement = f'<@{member_id}> was released from Jail by bribing the mods with beans. ' + response
            case ItemType.JAIL_REDUCTION:
                
                affected_jails = self.database.get_active_jails_by_member(guild_id, member_id)
                
                if len(affected_jails) == 0:
                    await interaction.followup.send(f'You are currently not in jail.', ephemeral=True)
                    return
                    
                jail = affected_jails[0]
                
                remaining = int(self.event_manager.get_jail_remaining(jail))
                
                total_value = self.item.get_value() * amount
                
                if remaining - total_value <= 0:
                    await interaction.followup.send(f'You cannot reduce your jail sentence by this much.', ephemeral=True)
                    return
                
                if remaining - total_value <= 30:
                    total_value -= (30 - (remaining - total_value))
                
                self.event_manager.dispatch_jail_event(
                    datetime.datetime.now(), 
                    guild_id,
                    JailEventType.REDUCE, 
                    member_id,
                    -total_value,
                    jail.get_id()
                )
                
                jail_announcement = f'<@{member_id}> reduced their own sentence by `{total_value}` minutes by spending `🅱️{cost}` beans.'
                new_remaining = self.event_manager.get_jail_remaining(jail)
                jail_announcement += f'\n `{BotUtil.strfdelta(new_remaining, inputtype='minutes')}` still remain.'
                
            case _:
                await interaction.followup.send(f'Something went wrong, please contact a staff member.', ephemeral=True)
                return
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.SHOP_PURCHASE, 
            member_id,
            -cost
        )
        
        await jail_cog.announce(interaction.guild, jail_announcement)
        await self.finish_transaction(interaction)