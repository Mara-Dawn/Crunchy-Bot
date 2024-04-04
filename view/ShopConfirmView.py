import datetime
import random
import secrets
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
        
        self.amount_select = AmountInput()
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()
        
        self.refresh_elements()
        
    async def submit(self, interaction: discord.Interaction):
        if not await self.start_transaction(interaction):
            return
        match self.type:
            case ItemType.BAILOUT:
                await self.jail_interaction(interaction)
            case ItemType.JAIL_REDUCTION:
                await self.jail_interaction(interaction)
            case ItemType.EXPLOSIVE_FART:
                await self.random_jailing(interaction)
    
    async def random_jailing(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        amount = self.selected_amount
        cost = self.item.get_cost() * amount
        
        bean_data = self.database.get_guild_beans(guild_id)
        users = []
        
        for user_id, amount in bean_data.items():
            if amount >= 500:
                users.append(user_id)
        
        jails = self.database.get_active_jails_by_guild(guild_id)
        
        for jail in jails:
            jailed_member_id = jail.get_member_id()
            if jailed_member_id in users:
                users.remove(jailed_member_id)
        
        victims = random.sample(users, min(5, len(users)))
        jail_cog: Jail = self.bot.get_cog('Jail')
        
        jail_announcement = f'After committing unspeakable atrocities, <@{member_id}> caused innocent bystanders to be banished into the abyss.'
        await jail_cog.announce(interaction.guild, jail_announcement)
        
        for victim in victims:
            duration = random.randint(5*60, 10*60)
            member = interaction.guild.get_member(victim)
            
            if member is None:
                continue
            
            success = await jail_cog.jail_user(guild_id, member_id, member, duration)

            if not success:
                continue
            
            timestamp_now = int(datetime.datetime.now().timestamp())
            release = timestamp_now + (duration*60)
            jail_announcement = f'<@{victim}> was sentenced to Jail. They will be released <t:{release}:R>.'
            await jail_cog.announce(interaction.guild, jail_announcement)
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.SHOP_PURCHASE, 
            member_id,
            -cost
        )
        await self.finish_transaction(interaction)
    
    async def jail_interaction(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        amount = self.selected_amount
        cost = self.item.get_cost() * amount

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