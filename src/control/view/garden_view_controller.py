import datetime
import random
import secrets

import discord
from discord.ext import commands

from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from control.view.view_controller import ViewController
from datalayer.database import Database
from datalayer.garden import Plot, UserGarden
from datalayer.types import LootboxType, PlantType
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.garden_event import GardenEvent
from events.inventory_event import InventoryEvent
from events.types import BeansEventType, EventType, GardenEventType, UIEventType
from events.ui_event import UIEvent
from items import BaseSeed, Debuff
from items.types import ItemType
from view.garden.embed import GardenEmbed
from view.garden.plot_embed import PlotEmbed
from view.garden.plot_view import PlotView
from view.garden.view import GardenView


class GardenViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.item_manager: ItemManager = controller.get_service(ItemManager)
        self.settings_manager: SettingsManager = controller.get_service(SettingsManager)

    async def listen_for_event(self, event: BotEvent) -> None:
        member_id = None
        guild_id = None
        match event.type:
            case EventType.BEANS:
                event: BeansEvent = event
                guild_id = event.guild_id
                member_id = event.member_id
            case EventType.INVENTORY:
                event: InventoryEvent = event
                guild_id = event.guild_id
                member_id = event.member_id

        if member_id is not None and guild_id is not None:
            inventory = await self.item_manager.get_user_inventory(guild_id, member_id)
            event = UIEvent(UIEventType.INVENTORY_USER_REFRESH, inventory)
            await self.controller.dispatch_ui_event(event)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.GARDEN_SELECT_PLOT:
                interaction = event.payload[0]
                garden = event.payload[1]
                x = event.payload[2]
                y = event.payload[3]
                message = event.payload[4]
                await self.open_plot_menu(
                    interaction, garden, x, y, message, event.view_id
                )
            case UIEventType.GARDEN_PLOT_BACK:
                interaction = event.payload[0]
                message = event.payload[1]
                await self.back_to_garden(interaction, message, event.view_id)
            case UIEventType.GARDEN_PLOT_WATER:
                interaction = event.payload[0]
                plot = event.payload[1]
                await self.water(interaction, plot, event.view_id)
            case UIEventType.GARDEN_PLOT_PLANT:
                interaction = event.payload[0]
                plot = event.payload[1]
                seed = event.payload[2]
                await self.plant(interaction, plot, seed, event.view_id)
            case UIEventType.GARDEN_PLOT_REMOVE:
                interaction = event.payload[0]
                plot = event.payload[1]
                await self.remove(interaction, plot, event.view_id)
            case UIEventType.GARDEN_PLOT_HARVEST:
                interaction = event.payload[0]
                plot = event.payload[1]
                await self.harvest(interaction, plot, event.view_id)

    async def __use_seed(self, interaction: discord.Integration, plant_type: PlantType):
        guild_id = interaction.guild_id
        member_id = interaction.user.id
        item_type = None
        match plant_type:
            case PlantType.BEAN:
                event = BeansEvent(
                    datetime.datetime.now(),
                    guild_id,
                    BeansEventType.BEAN_PLANT,
                    member_id,
                    -1,
                )
                await self.controller.dispatch_event(event)
            case _:
                plant_seed_map = {v: k for k, v in BaseSeed.SEED_PLANT_MAP.items()}
                item_type = plant_seed_map[plant_type]

        if item_type is not None:
            event = InventoryEvent(
                datetime.datetime.now(),
                guild_id,
                member_id,
                item_type,
                -1,
            )
            await self.controller.dispatch_event(event)

    async def __harvest_plant(
        self, interaction: discord.Interaction, plant_type: PlantType
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        message = ""
        reward = 0

        match plant_type:
            case PlantType.BEAN:
                reward = random.randint(450, 550)
                message = f"You harvest a Bean Plant and gain `🅱️{reward}`."
            case PlantType.RARE_BEAN:
                reward = random.randint(1900, 2100)
                message = f"You harvest a Rare Bean Plant and gain `🅱️{reward}`."
            case PlantType.CRYSTAL_BEAN:
                reward = random.randint(5000, 6000)
                message = f"You harvest a Crystal Bean Plant and gain `🅱️{reward}`."
            case PlantType.SPEED_BEAN:
                reward = random.randint(90, 110)
                message = f"You harvest a Speed Bean Plant and gain `🅱️{reward}`."
            case PlantType.BOX_BEAN:
                reward = random.randint(900, 1100)
                message = f"You harvest a Treasure Bean Plant and gain `🅱️{reward}`."
                message += "\nIt kind of looks like a lootbox, just way bigger!"
                await self.item_manager.drop_private_loot_box(interaction, size=15)
            case PlantType.CAT_BEAN:
                reward = random.randint(450, 550)
                message = f"You harvest a Catgirl Bean Plant and gain `🅱️{reward}`."

                roll = random.random()
                useful_catgirl_chance = 0.003

                item_type = ItemType.CATGIRL
                message += (
                    "\n You also hear a suspicious meowing coming from your inventory."
                )
                if roll <= useful_catgirl_chance:
                    item_type = ItemType.USEFUL_CATGIRL
                    message += "\n Just as you thought 'Not another useless Catgirl!' you realize that this one"
                    message += "\n is actually cleaning up and helping out with things! You found yourself an ultra rare **Useful Catgirl!**"
                else:
                    message += "\n Looks like you got yourself a useless Catgirl!"

                event = InventoryEvent(
                    datetime.datetime.now(),
                    guild_id,
                    member_id,
                    item_type,
                    1,
                )
                await self.controller.dispatch_event(event)
            case PlantType.YELLOW_BEAN:
                reward = random.randint(450, 550)
                message = f"You harvest a Piss Bean Plant and gain `🅱️{reward}`."
                message += "\nThe soil seems more fertile too! Looks like plants will grow faster on this plot for a while."
            case PlantType.BAKED_BEAN:
                reward = random.randint(420, 690)
                message = f"You harvest a Baked Bean Plant and gain `🅱️{reward}`."
                message += "\nAs soon as you pick them up you feel a sudden hit of absolute dankness smash your brain and sweep you off your feet. Good luck."
                ghost = secrets.choice(Debuff.DEBUFFS)
                event = InventoryEvent(
                    datetime.datetime.now(),
                    guild_id,
                    member_id,
                    ghost,
                    Debuff.DEBUFF_BAKED_DURATION,
                )
                await self.controller.dispatch_event(event)
            case PlantType.GHOST_BEAN:
                reward = random.randint(450, 550)
                message = f"You harvest a Ghost Bean Plant and gain `🅱️{reward}`."
                message += "\nYou also gain a Spooky Bean. Enjoy ruining someones day with this."
                event = InventoryEvent(
                    datetime.datetime.now(),
                    guild_id,
                    member_id,
                    ItemType.SPOOK_BEAN,
                    1,
                )
                await self.controller.dispatch_event(event)
            case PlantType.KEY_BEAN:
                reward = random.randint(450, 550)
                message = f"You harvest a Key Bean Plant and gain `🅱️{reward}`."
                message += "\nIt also drops a whole bunch of keys!"
                key_reward = random.randint(2, 3)
                await self.item_manager.drop_private_loot_box(
                    interaction, size=key_reward, lootbox_type=LootboxType.KEYS
                )
            case PlantType.FLASH_BEAN:
                message = "You remove the dried out Flash bean from the plot and find a small seed!"
                message += "\nA Ghost Bean Seed has been added to your inventory."
                event = InventoryEvent(
                    datetime.datetime.now(),
                    guild_id,
                    member_id,
                    ItemType.GHOST_SEED,
                    1,
                )
                await self.controller.dispatch_event(event)

        roll = random.random()
        rare_seed_chance = 0.1
        speed_seed_chance = 0.1
        crystal_seed_chance = 0.02

        item_type = None
        if roll <= rare_seed_chance:
            item_type = ItemType.RARE_SEED
            message += "\nOh wow, you also find a **Rare Seed**!"
        elif roll > rare_seed_chance and roll <= (rare_seed_chance + speed_seed_chance):
            item_type = ItemType.SPEED_SEED
            message += "\nOh wow, you also find a **Speed Seed**!"
        elif roll > (rare_seed_chance + speed_seed_chance) and roll <= (
            rare_seed_chance + speed_seed_chance + crystal_seed_chance
        ):
            item_type = ItemType.CRYSTAL_SEED
            message += (
                "\nOh wow, you also find a **Crystal Seed**! These must be super rare!"
            )

        if item_type is not None:
            event = InventoryEvent(
                datetime.datetime.now(),
                guild_id,
                member_id,
                item_type,
                1,
            )
            await self.controller.dispatch_event(event)

        if reward > 0:
            event = BeansEvent(
                datetime.datetime.now(),
                guild_id,
                BeansEventType.BEAN_HARVEST,
                member_id,
                reward,
            )
            await self.controller.dispatch_event(event)

        if len(message) > 0:
            await interaction.followup.send(content=message, ephemeral=True)

    async def open_plot_menu(
        self,
        interaction: discord.Interaction,
        garden: UserGarden,
        x: int,
        y: int,
        message: discord.Message,
        view_id: int,
    ):
        event = UIEvent(
            UIEventType.GARDEN_DETACH,
            None,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

        plot = garden.get_plot(x, y)
        status_picture = plot.get_status_image()
        plot_picture = discord.File(f"./img/garden/{status_picture}", "status.png")

        garden_embed = GardenEmbed(self.controller.bot, garden)

        content = garden_embed.get_garden_content()
        embed = PlotEmbed(plot)
        view = PlotView(self.controller, interaction, garden, x, y)
        view.set_message(message)
        await message.edit(
            content=content, embed=embed, view=view, attachments=[plot_picture]
        )

    async def back_to_garden(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        event = UIEvent(
            UIEventType.GARDEN_DETACH,
            None,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

        garden = await self.database.get_user_garden(guild_id, user_id)

        embed = GardenEmbed(self.controller.bot, garden)
        view = GardenView(self.controller, interaction, garden)
        view.set_message(message)
        content = embed.get_garden_content()
        await message.edit(content=content, embed=embed, view=view, attachments=[])

    async def water(
        self,
        interaction: discord.Interaction,
        plot: Plot,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        event = UIEvent(
            UIEventType.GARDEN_PLOT_BLOCK,
            None,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

        event = GardenEvent(
            datetime.datetime.now(),
            guild_id,
            plot.garden_id,
            plot.id,
            user_id,
            GardenEventType.WATER,
            plot.plant.type.value,
        )
        await self.controller.dispatch_event(event)

        garden = await self.database.get_user_garden(guild_id, user_id)
        event = UIEvent(
            UIEventType.GARDEN_REFRESH,
            garden,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def plant(
        self,
        interaction: discord.Interaction,
        plot: Plot,
        seed: PlantType,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        event = UIEvent(
            UIEventType.GARDEN_PLOT_BLOCK,
            None,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

        event = GardenEvent(
            datetime.datetime.now(),
            guild_id,
            plot.garden_id,
            plot.id,
            user_id,
            GardenEventType.PLANT,
            seed.value,
        )
        await self.controller.dispatch_event(event)

        await self.__use_seed(interaction, seed)

        garden = await self.database.get_user_garden(guild_id, user_id)
        event = UIEvent(
            UIEventType.GARDEN_REFRESH,
            garden,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def remove(
        self,
        interaction: discord.Interaction,
        plot: Plot,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        event = UIEvent(
            UIEventType.GARDEN_PLOT_BLOCK,
            None,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

        event = GardenEvent(
            datetime.datetime.now(),
            guild_id,
            plot.garden_id,
            plot.id,
            user_id,
            GardenEventType.REMOVE,
            plot.plant.type.value,
        )
        await self.controller.dispatch_event(event)

        garden = await self.database.get_user_garden(guild_id, user_id)
        event = UIEvent(
            UIEventType.GARDEN_REFRESH,
            garden,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def harvest(
        self,
        interaction: discord.Interaction,
        plot: Plot,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        event = UIEvent(
            UIEventType.GARDEN_PLOT_BLOCK,
            None,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

        event = GardenEvent(
            datetime.datetime.now(),
            guild_id,
            plot.garden_id,
            plot.id,
            user_id,
            GardenEventType.HARVEST,
            plot.plant.type.value,
        )
        await self.controller.dispatch_event(event)

        await self.__harvest_plant(interaction, plot.plant.type)

        garden = await self.database.get_user_garden(guild_id, user_id)

        unlocked_features = await self.settings_manager.get_unlocked_features(guild_id)

        max_plots = max(
            [
                value
                for key, value in UserGarden.PLOT_UNLOCKS.items()
                if key in unlocked_features
            ]
        )
        plot_count = len(garden.plots)
        if plot_count < max_plots:
            garden = await self.database.add_garden_plot(garden)

        event = UIEvent(
            UIEventType.GARDEN_REFRESH,
            garden,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)
