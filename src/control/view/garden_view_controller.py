import datetime
import random

import discord
from datalayer.database import Database
from datalayer.garden import Plot, UserGarden
from datalayer.types import PlantType
from discord.ext import commands
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.garden_event import GardenEvent
from events.inventory_event import InventoryEvent
from events.types import BeansEventType, EventType, GardenEventType, UIEventType
from events.ui_event import UIEvent
from view.garden.plot_view import PlotView
from view.garden.view import GardenView

from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.view.view_controller import ViewController


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

    async def __harvest_plant(
        self, interaction: discord.Integration, plant_type: PlantType
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        reward = random.randint(900, 1100)

        match plant_type:
            case PlantType.BEAN:
                event = BeansEvent(
                    datetime.datetime.now(),
                    guild_id,
                    BeansEventType.BEAN_HARVEST,
                    member_id,
                    reward,
                )
                await self.controller.dispatch_event(event)

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

        view = PlotView(self.controller, interaction, garden, x, y)
        view.set_message(message)
        await message.edit(view=view)
        await view.refresh_ui()

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

        view = GardenView(self.controller, interaction, garden)
        view.set_message(message)
        await message.edit(view=view)
        await view.refresh_ui()

    async def water(
        self,
        interaction: discord.Interaction,
        plot: Plot,
        view_id: int,
    ):
        guild_id = interaction.guild_id
        user_id = interaction.user.id

        event = GardenEvent(
            datetime.datetime.now(),
            guild_id,
            plot.garden_id,
            plot.id,
            user_id,
            GardenEventType.WATER,
        )
        await self.controller.dispatch_event(event)

        garden = await self.database.get_user_garden(guild_id, user_id)
        event = UIEvent(
            UIEventType.GARDEN_PLOT_REFRESH,
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
            UIEventType.GARDEN_PLOT_REFRESH,
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

        event = GardenEvent(
            datetime.datetime.now(),
            guild_id,
            plot.garden_id,
            plot.id,
            user_id,
            GardenEventType.REMOVE,
        )
        await self.controller.dispatch_event(event)

        garden = await self.database.get_user_garden(guild_id, user_id)
        event = UIEvent(
            UIEventType.GARDEN_PLOT_REFRESH,
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

        event = GardenEvent(
            datetime.datetime.now(),
            guild_id,
            plot.garden_id,
            plot.id,
            user_id,
            GardenEventType.HARVEST,
        )
        await self.controller.dispatch_event(event)

        await self.__harvest_plant(interaction, plot.plant.type)

        garden = await self.database.get_user_garden(guild_id, user_id)
        event = UIEvent(
            UIEventType.GARDEN_PLOT_REFRESH,
            garden,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)
