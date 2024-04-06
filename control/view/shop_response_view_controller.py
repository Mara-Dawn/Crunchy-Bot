import datetime
import random
from typing import Tuple
import discord
from bot_util import BotUtil
from cogs import Jail
from control.view import ViewController
from events import BatEvent, BeansEvent, BotEvent, InventoryEvent, JailEvent, UIEvent
from events.types import BeansEventType, JailEventType, UIEventType
from items.types import ItemType
from view.types import EmojiType
from view import ShopResponseView

class ShopResponseViewController(ViewController):
        
    async def listen_for_event(self, event: BotEvent):
        pass
    
    async def refresh_shop_view(self, guild_id: int, member_id: int):
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        event = UIEvent(guild_id, member_id, UIEventType.REFRESH_SHOP, new_user_balance)
        await self.controller.dispatch_ui_event(event)
    
    async def refresh_shop_response_view(self, guild_id: int, member_id: int):
        event = UIEvent(guild_id, member_id, UIEventType.REFRESH_SHOP_RESPONSE, True)
        await self.controller.dispatch_ui_event(event)
    
    async def start_transaction(self, interaction: discord.Interaction, view: ShopResponseView) -> bool:
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        
        if view.item is not None:
            user_balance = self.database.get_member_beans(guild_id, member_id)
            
            amount = view.selected_amount
            cost = view.item.get_cost() * amount
            
            if user_balance < cost:
                await interaction.followup.send('You dont have enough beans to buy that.', ephemeral=True)
                return False
        
        if view.selected_user is not None and view.selected_user.bot:
            await interaction.followup.send("You cannot select bot users.", ephemeral=True)
            return False

        if view.user_select is not None and view.selected_user is None:
            await interaction.followup.send('Please select a user first.', ephemeral=True)
            return False
        
        if view.reaction_input_button is not None and view.selected_emoji is None:
            await interaction.followup.send('Please select a reaction emoji first.', ephemeral=True)
            return False
        
        if view.color_input_button is not None and view.selected_color is None:
            await interaction.followup.send('Please select a color first.', ephemeral=True)
            return False
        
        return True
    
    async def finish_transaction(self, interaction: discord.Interaction, view: ShopResponseView):
        amount = view.selected_amount
        cost = view.item.get_cost() * amount
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        
        log_message = f'{interaction.user.display_name} bought {amount} {view.item.get_name()} for {cost} beans.'
        
        arguments = []
        
        if view.selected_user is not None:
            arguments.append(f'selected_user: {view.selected_user.display_name}')
        
        if view.selected_color is not None:
            arguments.append(f'selected_color: {view.selected_color}')
            
        if view.selected_emoji is not None:
            arguments.append(f'selected_emoji: {str(view.selected_emoji)}')
        
        if len(arguments) > 0:
            log_message += ' arguments[' + ', '.join(arguments) + ']'
        
        self.logger.log(interaction.guild_id, log_message, cog='Shop')
        
        new_user_balance = self.database.get_member_beans(guild_id, member_id)
        success_message = f'You successfully bought {amount} **{view.item.get_name()}** for `🅱️{cost}` beans.\n Remaining balance: `🅱️{new_user_balance}`'
        
        await interaction.followup.send(success_message, ephemeral=True)
        
        event = UIEvent(guild_id, member_id, UIEventType.REFRESH_SHOP, new_user_balance)
        await self.controller.dispatch_ui_event(event)
        
        message = await interaction.original_response()
        await message.delete()
    
    async def submit_reaction_selection(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer()
        
        user_emoji = None
        emoji_type = None
        
        message = await interaction.channel.fetch_message(message.id)
        
        for reaction in message.reactions:
            reactors = [user async for user in reaction.users()]
            if interaction.user in reactors:
                if user_emoji is not None:
                    await interaction.followup.send('Please react with a single emoji.', ephemeral=True)
                    return
                
                user_emoji = reaction.emoji
                emoji_type = EmojiType.CUSTOM if reaction.is_custom_emoji() else EmojiType.DEFAULT
        
        if user_emoji is None:
            await interaction.followup.send('Please react with any emoji.', ephemeral=True)
            return
        
        if emoji_type == EmojiType.CUSTOM:
            emoji_obj = discord.utils.get(self.bot.emojis, name=user_emoji.name)
            if emoji_obj is None:                      
                await interaction.followup.send('I do not have access to this emoji. I can only see the emojis of the servers i am a member of.', ephemeral=True)
                return
        
        event = UIEvent(interaction.guild_id, interaction.user.id, UIEventType.UPDATE_SHOP_RESPONSE_EMOJI, (user_emoji, emoji_type))
        await self.controller.dispatch_ui_event(event)
        
        await interaction.followup.delete_message(message.id)
    
    async def submit_confirm_view(self, interaction: discord.Interaction, view: ShopResponseView):
        if not await self.start_transaction(interaction, view):
            return
        
        match view.type:
            case ItemType.BAILOUT:
                await self.jail_interaction(interaction, view)
            case ItemType.JAIL_REDUCTION:
                await self.jail_interaction(interaction, view)
            case ItemType.EXPLOSIVE_FART:
                await self.random_jailing(interaction, view)
    
    async def submit_user_view(self, interaction: discord.Interaction, view: ShopResponseView):
        if not await self.start_transaction(interaction, view):
            return
        
        match view.type:
            case ItemType.ARREST:
                await self.jail_interaction(interaction, view)
            case ItemType.RELEASE:
                await self.jail_interaction(interaction, view)
            case ItemType.ROULETTE_FART:
                await self.jail_interaction(interaction, view)
            case ItemType.BAT:
                await self.bat_attack(interaction, view)
    
    async def jail_interaction(self, interaction: discord.Interaction, view: ShopResponseView):
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        amount = view.selected_amount
        cost = view.item.get_cost() * amount

        jail_cog: Jail = self.bot.get_cog('Jail')
        
        match view.type:
            case ItemType.ARREST:
                duration = 30
                success = await jail_cog.jail_user(guild_id, member_id, view.selected_user, duration)
                
                if not success:
                    await interaction.followup.send(f'User {view.selected_user.display_name} is already in jail.', ephemeral=True)
                    return
                
                timestamp_now = int(datetime.datetime.now().timestamp())
                release = timestamp_now + (duration*60)
                jail_announcement = f'<@{view.selected_user.id}> was sentenced to Jail by <@{member_id}> using a **{view.item.get_name()}**. They will be released <t:{release}:R>.'
                
            case ItemType.RELEASE:
                if view.selected_user.id == interaction.user.id:
                    await interaction.followup.send('You cannot free yourself using this item.', ephemeral=True)
                    return
                
                response = await jail_cog.release_user(guild_id, member_id, view.selected_user)

                if not response:
                    await interaction.followup.send(f'User {view.selected_user.display_name} is currently not in jail.', ephemeral=True)
                    return
                
                jail_announcement = f'<@{view.selected_user.id}> was generously released from Jail by <@{interaction.user.id}> using a **{view.item.get_name()}**. ' + response
                
            case ItemType.ROULETTE_FART:
                duration = 30
                
                member = interaction.user
                selected = view.selected_user
                
                timestamp_now = int(datetime.datetime.now().timestamp())
                release = timestamp_now + (duration*60)
                target = selected
                jail_announcement = f'<@{selected.id}> was sentenced to Jail by <@{member_id}> using a **{view.item.get_name()}**. They will be released <t:{release}:R>.'
                
                if random.choice([True, False]):
                    jail_announcement = f'<@{member_id}> shit themselves in an attempt to jail <@{selected.id}> using a **{view.item.get_name()}**, going to jail in their place. They will be released <t:{release}:R>.'
                    target = member
                
                success = await jail_cog.jail_user(guild_id, member_id, target, duration)
                
                if not success:
                    await interaction.followup.send(f'User {view.selected_user.display_name} is already in jail.', ephemeral=True)
                    return
            case ItemType.BAILOUT:
                response = await jail_cog.release_user(guild_id, member_id, interaction.user)
        
                if not response:
                    await interaction.followup.send('You are currently not in jail.', ephemeral=True)
                    return
                
                jail_announcement = f'<@{member_id}> was released from Jail by bribing the mods with beans. ' + response
            case ItemType.JAIL_REDUCTION:
                
                affected_jails = self.database.get_active_jails_by_member(guild_id, member_id)
                
                if len(affected_jails) == 0:
                    await interaction.followup.send('You are currently not in jail.', ephemeral=True)
                    return
                    
                jail = affected_jails[0]
                
                remaining = int(self.event_manager.get_jail_remaining(jail))
                
                total_value = view.item.get_value() * amount
                
                if remaining - total_value <= 0:
                    await interaction.followup.send('You cannot reduce your jail sentence by this much.', ephemeral=True)
                    return
                
                if remaining - total_value <= 30:
                    total_value -= (30 - (remaining - total_value))
                    
                event = JailEvent(datetime.datetime.now(), guild_id, JailEventType.REDUCE, member_id, -total_value, jail.get_id())
                await self.controller.dispatch_event(event)
                
                jail_announcement = f'<@{member_id}> reduced their own sentence by `{total_value}` minutes by spending `🅱️{cost}` beans.'
                new_remaining = self.event_manager.get_jail_remaining(jail)
                jail_announcement += f'\n `{BotUtil.strfdelta(new_remaining, inputtype='minutes')}` still remain.'
                
            case _:
                await interaction.followup.send('Something went wrong, please contact a staff member.', ephemeral=True)
                return
        
        event = BeansEvent(datetime.datetime.now(), guild_id, BeansEventType.SHOP_PURCHASE, member_id, -cost)
        await self.controller.dispatch_event(event)
        
        await jail_cog.announce(interaction.guild, jail_announcement)
        await self.finish_transaction(interaction, view)
       
    async def bat_attack(self, interaction: discord.Interaction, view: ShopResponseView):
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        target = view.selected_user
        last_bat_event = self.database.get_last_bat_event_by_target(guild_id, target.id)
        
        last_bat_time = datetime.datetime.min
        if last_bat_event is not None:
            last_bat_time = last_bat_event.get_datetime()
        
        diff = datetime.datetime.now() - last_bat_time
        if int(diff.total_seconds()/60) <= view.item.get_value():
            await interaction.followup.send("Targeted user is already stunned by a previous bat attack.", ephemeral=True)
            return
        
        event = BatEvent(datetime.datetime.now(), guild_id, member_id, target.id)
        await self.controller.dispatch_event(event)
        
        amount = view.selected_amount
        cost = view.item.get_cost() * amount
        
        event = BeansEvent(datetime.datetime.now(), guild_id, BeansEventType.SHOP_PURCHASE, member_id, -cost)
        await self.controller.dispatch_event(event)
        
        await self.finish_transaction(interaction, view)
        
    async def random_jailing(self, interaction: discord.Interaction, view: ShopResponseView):
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        amount = view.selected_amount
        cost = view.item.get_cost() * amount
        
        bean_data = self.database.get_guild_beans(guild_id)
        users = []
        
        for user_id, amount in bean_data.items():
            if amount >= 100:
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
        
        event = BeansEvent(datetime.datetime.now(), guild_id, BeansEventType.SHOP_PURCHASE, member_id, -cost)
        await self.controller.dispatch_event(event)

        await self.finish_transaction(interaction, view)
        
    def get_custom_color(self, interaction: discord.Interaction) -> str:
        return self.database.get_custom_color(interaction.guild_id, interaction.user.id)

    def get_bully_react(self, interaction: discord.Interaction) -> Tuple[int,discord.Emoji|str]:
        return self.database.get_bully_react(interaction.guild_id, interaction.user.id)

    async def submit_generic_view(self, interaction: discord.Interaction, view: ShopResponseView):
        if not await self.start_transaction(interaction, view):
            return
        
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        amount = view.selected_amount
        cost = view.item.get_cost() * amount

        event = BeansEvent(datetime.datetime.now(), guild_id, BeansEventType.SHOP_PURCHASE, member_id, -cost)
        await self.controller.dispatch_event(event)
        
        match view.type:
            case ItemType.NAME_COLOR:
                self.database.log_custom_color(guild_id, member_id, view.selected_color)
                event = InventoryEvent(datetime.datetime.now(), guild_id, member_id, view.type, view.item.get_base_amount()*amount)
                await self.controller.dispatch_event(event)
            case ItemType.REACTION_SPAM:
                self.database.log_bully_react(guild_id, member_id, view.selected_user.id, view.selected_emoji_type, view.selected_emoji)
                event = InventoryEvent(datetime.datetime.now(), guild_id, member_id, view.type, view.item.get_base_amount()*amount)
                await self.controller.dispatch_event(event)
            case _:
                await interaction.followup.send('Something went wrong, please contact a staff member.', ephemeral=True)
                return
        
        await self.finish_transaction(interaction, view)
