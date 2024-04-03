import datetime
import discord

from CrunchyBot import CrunchyBot
from events.BeansEventType import BeansEventType
from shop.Item import Item
from shop.ItemType import ItemType
from view.ShopResponseView import *

class ShopReactionSelectView(ShopResponseView):
    
    def __init__(self, bot: CrunchyBot, interaction: discord.Interaction, parent, item: Item):
        super().__init__(bot, interaction, parent, item)

        default_user, default_emoji  = bot.database.get_bully_react(interaction.guild_id, interaction.user.id)
        
        self.selected_emoji: discord.Emoji|str = default_emoji
        self.selected_emoji_type: EmojiType = EmojiType.DEFAULT if isinstance(default_emoji, str) else EmojiType.CUSTOM
        
        self.user_select = UserPicker()
        self.amount_select = AmountInput(suffix=' x 10 Reactions')
        self.reaction_input_button = ReactionInputButton()
        self.confirm_button = ConfirmButton()
        self.cancel_button = CancelButton()
        
        self.refresh_elements()
    
    async def submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        if self.selected_user is None:
            await interaction.followup.send('Please select a user first.', ephemeral=True)
            return
        
        if self.selected_emoji is None:
            await interaction.followup.send('Please select a reaction emoji first.', ephemeral=True)
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
            case ItemType.REACTION_SPAM:
                pass
                self.database.log_bully_react(guild_id, member_id, self.selected_user.id, self.selected_emoji_type, self.selected_emoji)
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
        
        await self.finish_transaction(interaction)

