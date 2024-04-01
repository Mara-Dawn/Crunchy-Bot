import datetime
import discord

from BotLogger import BotLogger
from datalayer.Database import Database
from datalayer.LootBox import LootBox
from events.BeansEventType import BeansEventType
from events.EventManager import EventManager
from events.LootBoxEventType import LootBoxEventType
from shop.Item import Item

class LootBoxMenu(discord.ui.View):
    
    def __init__(self, event_manager: EventManager, database: Database, logger: BotLogger, item: Item, user_id: int = None):
        self.database = database
        self.event_manager = event_manager
        self.item = item
        self.logger = logger
        self.user_id = user_id
        
        super().__init__()
        self.add_item(ClaimButton())
        
    async def claim(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        
        if self.user_id is not None and member_id != self.user_id:
            await interaction.response.send_message(f'This is a personalized lootbox, only the owner can claim it.', ephemeral=True)
            return

        self.stop()
        await interaction.response.defer()
        
        message = await interaction.original_response()
        loot_box = self.database.get_loot_box_by_message_id(guild_id, message.id)
        
        title = "A Random Treasure has Appeared"
        if self.user_id is not None:
            title = f"{interaction.user.display_name}'s Random Treasure Chest"
            
        description = f"This treasure was claimed by: \n <@{member_id}>"
        description += f"\n\nThey slowly open the chest and reveal..."
        embed = discord.Embed(title=title, description=description, color=discord.Colour.purple()) 
        
        beans = loot_box.get_beans()
        
        if beans < 0:
            bean_balance = self.database.get_member_beans(guild_id, interaction.user.id)
            if bean_balance + beans < 0:
                beans = -bean_balance
            
            embed.add_field(name='Oh no, it\'s a Mimic!', value=f"It munches away at your beans, eating `🅱️{abs(beans)}` of them.", inline=False)
            embed.set_image(url="attachment://mimic.gif")
            attachment = discord.File("./img/mimic.gif", "mimic.gif")
        else:
            embed.add_field(name='A Bunch of Beans!', value=f"A whole  `🅱️{beans}` of them.", inline=False)
            embed.set_image(url="attachment://treasure_open.png")
            attachment = discord.File("./img/treasure_open.png", "treasure_open.png")
        
        log_message = f'{interaction.user.display_name} claimed a loot box containing {beans} beans'
        
        if loot_box.get_item_type() is not None:
            embed.add_field(name='Woah, a Shiny Item!', value='', inline=False)
            self.item.add_to_embed(embed, 37, count=self.item.get_base_amount())
            log_message += f' and 1x {self.item.get_name()}'
            
            self.event_manager.dispatch_inventory_event(
                datetime.datetime.now(), 
                guild_id,
                member_id,
                loot_box.get_item_type(),
                0,
                self.item.get_base_amount()
            )
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.LOOTBOX_PAYOUT, 
            member_id,
            beans
        )
        
        event_type = LootBoxEventType.CLAIM
        if self.user_id is not None:
            event_type = LootBoxEventType.OPEN
        
        self.event_manager.dispatch_loot_box_event(
            datetime.datetime.now(), 
            guild_id,
            loot_box.get_id(),
            member_id,
            event_type
        )
        
        self.logger.log(interaction.guild_id, log_message, cog='Beans')
        
        await interaction.edit_original_response(embed=embed, view=None, attachments=[attachment])
        
class ClaimButton(discord.ui.Button):
    
    def __init__(self):
        super().__init__(label='Mine!', style=discord.ButtonStyle.green)
    
    async def callback(self, interaction: discord.Interaction):
        view: LootBoxMenu = self.view
        
        await view.claim(interaction)