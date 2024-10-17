import datetime

import discord
from discord.ext import commands

from combat.enchantments.enchantment import Enchantment
from combat.enchantments.enchantment_handler import EnchantmentCraftHandler
from combat.enchantments.types import EnchantmentEffect
from combat.gear.gear import Gear
from combat.gear.types import Base, EquipmentSlot
from combat.skills.skill import Skill
from config import Config
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.encounter_manager import EncounterManager
from control.controller import Controller
from control.event_manager import EventManager
from control.forge_manager import ForgeManager
from control.logger import BotLogger
from control.view.view_controller import ViewController
from datalayer.database import Database
from events.bot_event import BotEvent
from events.equipment_event import EquipmentEvent
from events.inventory_event import InventoryEvent
from events.types import EquipmentEventType, EventType, UIEventType
from events.ui_event import UIEvent
from forge.forgable import ForgeInventory
from forge.recipe import RecipeHandler
from items.types import ItemType
from view.combat.elements import MenuState
from view.combat.embed import (
    SelectGearHeadEmbed,
    SelectSkillHeadEmbed,
)
from view.combat.enchantment_view import EnchantmentView
from view.combat.equipment_select_view import EquipmentSelectView
from view.combat.skill_select_view import SkillSelectView, SkillViewState
from view.combat.special_shop_view import SpecialShopView


class EquipmentViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.event_manager: EventManager = controller.get_service(EventManager)
        self.actor_manager: CombatActorManager = controller.get_service(
            CombatActorManager
        )
        self.encounter_manager: EncounterManager = controller.get_service(
            EncounterManager
        )
        self.embed_manager: CombatEmbedManager = controller.get_service(
            CombatEmbedManager
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.forge_manager: ForgeManager = self.controller.get_service(ForgeManager)
        self.log_name = "Equipment"

    async def listen_for_event(self, event: BotEvent) -> None:
        member_id = None
        guild_id = None
        match event.type:
            case EventType.INVENTORY:
                event: InventoryEvent = event
                guild_id = event.guild_id
                member_id = event.member_id

        if (
            member_id is not None
            and guild_id is not None
            and event.item_type == ItemType.SCRAP
        ):
            user_items = await self.database.get_item_counts_by_user(
                guild_id, member_id, item_types=[ItemType.SCRAP]
            )
            scrap_balance = 0
            if ItemType.SCRAP in user_items:
                scrap_balance = user_items[ItemType.SCRAP]

            event = UIEvent(
                UIEventType.SCRAP_BALANCE_CHANGED, (guild_id, member_id, scrap_balance)
            )
            await self.controller.dispatch_ui_event(event)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.GEAR_OPEN_SELECT:
                interaction = event.payload[0]
                slot = event.payload[1]
                await self.open_gear_select(interaction, slot, event.view_id)
            case UIEventType.GEAR_EQUIP:
                interaction = event.payload[0]
                selected = event.payload[1]
                await self.equip_gear(interaction, selected, event.view_id)
            case UIEventType.GEAR_LOCK:
                interaction = event.payload[0]
                selected = event.payload[1]
                await self.update_gear_lock(
                    interaction, selected, lock=True, view_id=event.view_id
                )
            case UIEventType.GEAR_UNLOCK:
                interaction = event.payload[0]
                selected = event.payload[1]
                await self.update_gear_lock(
                    interaction, selected, lock=False, view_id=event.view_id
                )
            case UIEventType.GEAR_DISMANTLE:
                interaction = event.payload[0]
                selected = event.payload[1]
                scrap_all = event.payload[2]
                gear_slot = event.payload[3]
                await self.dismantle_gear(
                    interaction, selected, scrap_all, event.view_id, gear_slot=gear_slot
                )
            case UIEventType.SKILL_EQUIP_VIEW:
                interaction = event.payload
                await self.open_skill_view(
                    interaction, SkillViewState.EQUIP, event.view_id
                )
            case UIEventType.SKILL_MANAGE_VIEW:
                interaction = event.payload
                await self.open_skill_view(
                    interaction, SkillViewState.MANAGE, event.view_id
                )
            case UIEventType.SKILLS_EQUIP:
                interaction = event.payload[0]
                skills = event.payload[1]
                await self.set_selected_skills(interaction, skills, event.view_id)
            case UIEventType.FORGE_USE:
                interaction = event.payload[0]
                level = event.payload[1]
                slot = event.payload[2]
                await self.use_forge(interaction, level, slot)
            case UIEventType.FORGE_OPEN_SHOP:
                interaction = event.payload
                await self.open_forge_shop(interaction, event.view_id)
            case UIEventType.FORGE_SHOP_BUY:
                interaction = event.payload[0]
                selected = event.payload[1]
                await self.buy_gear(interaction, selected, event.view_id)
            case UIEventType.FORGE_CLEAR:
                interaction = event.payload
                await self.clear_forge_inventory(interaction, event.view_id)
            case UIEventType.FORGE_COMBINE:
                interaction = event.payload[0]
                forge_inventory = event.payload[1]
                await self.combine_forge_inventory(
                    interaction, forge_inventory, event.view_id
                )
            case UIEventType.ENCHANTMENTS_OPEN:
                interaction = event.payload[0]
                gear = event.payload[1]
                await self.open_enchantment_view(interaction, gear, event.view_id)
            case UIEventType.ENCHANTMENTS_APPLY:
                interaction = event.payload[0]
                gear = event.payload[1]
                enchantments = event.payload[2]
                await self.apply_gear_enchantment(
                    interaction, gear, enchantments, event.view_id
                )

    async def encounter_check(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        member_id = interaction.user.id
        encounters = await self.database.get_encounter_participants(guild_id)

        for _, participants in encounters.items():
            if member_id in participants:
                await interaction.followup.send(
                    "You cannot change your gear or skills while you are involved in an active combat.",
                    ephemeral=True,
                )
                return False
        return True

    async def refresh_gear_select(
        self, interaction: discord.Interaction, slot: EquipmentSlot, view_id: int
    ):

        guild_id = interaction.guild.id
        member_id = interaction.user.id

        if not await self.encounter_check(interaction):
            return

        gear_inventory = await self.database.get_user_armory(guild_id, member_id)
        default_gear = await self.gear_manager.get_default_gear()
        gear_inventory.extend(default_gear)
        currently_equipped = await self.database.get_user_equipment_slot(
            guild_id, member_id, slot
        )

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        view: EquipmentSelectView = self.controller.get_view(view_id)
        await view.refresh_ui(
            gear_inventory=gear_inventory,
            currently_equipped=currently_equipped,
            scrap_balance=scrap_balance,
        )

    async def refresh_special_shop(
        self, interaction: discord.Interaction, view_id: int
    ):
        guild_id = interaction.guild.id
        member_id = interaction.user.id

        if not await self.encounter_check(interaction):
            return

        user_daily_items = await self.gear_manager.get_member_daily_items(
            member_id, guild_id
        )
        item_values = {}

        for item in user_daily_items:
            scrap_value = (
                await self.gear_manager.get_gear_scrap_value(item)
                * Config.SCRAP_SHOP_MULTI
            )
            item_values[item.id] = scrap_value

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        view = SpecialShopView(
            self.controller,
            interaction,
            user_daily_items,
            item_values,
            scrap_balance,
        )

        view: SpecialShopView = self.controller.get_view(view_id)
        await view.refresh_ui(
            items=user_daily_items,
            scrap_balance=scrap_balance,
        )

    async def open_gear_select(
        self, interaction: discord.Interaction, slot: EquipmentSlot, view_id: int
    ):
        guild_id = interaction.guild.id
        member_id = interaction.user.id

        if not await self.encounter_check(interaction):
            return

        gear_inventory = await self.database.get_user_armory(guild_id, member_id)
        default_gear = await self.gear_manager.get_default_gear()
        gear_inventory.extend(default_gear)

        currently_equipped = await self.database.get_user_equipment_slot(
            guild_id, member_id, slot
        )

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        view = EquipmentSelectView(
            self.controller,
            interaction,
            gear_inventory,
            currently_equipped,
            scrap_balance,
            slot,
        )

        embeds = []
        embeds.append(SelectGearHeadEmbed(interaction.user))

        loading_embed = discord.Embed(
            title="Loading Gear", color=discord.Colour.light_grey()
        )
        self.embed_manager.add_text_bar(loading_embed, "", "Please Wait...")
        loading_embed.set_thumbnail(url=self.bot.user.display_avatar)
        embeds.append(loading_embed)

        message = await interaction.original_response()
        await message.edit(embeds=embeds, view=view, attachments=[])
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def open_forge_shop(self, interaction: discord.Interaction, view_id: int):
        guild_id = interaction.guild.id
        member_id = interaction.user.id

        if not await self.encounter_check(interaction):
            return

        user_daily_items = await self.gear_manager.get_member_daily_items(
            member_id, guild_id
        )
        item_values = {}

        for item in user_daily_items:
            scrap_value = (
                await self.gear_manager.get_gear_scrap_value(item)
                * Config.SCRAP_SHOP_MULTI
            )
            item_values[item.id] = scrap_value

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        view = SpecialShopView(
            self.controller,
            interaction,
            user_daily_items,
            item_values,
            scrap_balance,
        )

        message = await interaction.original_response()
        await message.edit(view=view, attachments=[])
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def buy_gear(
        self, interaction: discord.Interaction, selected: Gear | None, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        if not await self.encounter_check(interaction):
            return

        if selected is None:
            return

        scrap_value = (
            await self.gear_manager.get_gear_scrap_value(selected)
            * Config.SCRAP_SHOP_MULTI
        )

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        if scrap_balance < scrap_value:
            await interaction.followup.send(
                "You don't have enough scrap for this. Go and scrap some equipment you no longer need and come back.",
                ephemeral=True,
            )
            return

        event = InventoryEvent(
            datetime.datetime.now(),
            guild_id,
            member_id,
            ItemType.SCRAP,
            -scrap_value,
        )
        await self.controller.dispatch_event(event)

        event = EquipmentEvent(
            datetime.datetime.now(),
            guild_id,
            member_id,
            EquipmentEventType.SHOP_BUY,
            selected.id,
        )
        await self.controller.dispatch_event(event)

        await self.database.log_user_drop(
            guild_id=guild_id,
            member_id=member_id,
            drop=selected,
            generator_version=CombatGearManager.GENERATOR_VERSION,
        )

        message = f"{interaction.user.display_name} bought {selected.rarity.value} {selected.name} for {scrap_value} scrap."
        self.logger.log(interaction.guild_id, message, self.log_name)

        await self.refresh_special_shop(interaction, view_id)

        await interaction.followup.send(
            "Purchase Successful.",
            ephemeral=True,
        )

    async def equip_gear(
        self, interaction: discord.Interaction, selected: list[Gear], view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        if not await self.encounter_check(interaction):
            return

        if selected is None or len(selected) <= 0:
            return

        if len(selected) > 2:
            return

        if len(selected) == 1:
            await self.database.update_user_equipment(guild_id, member_id, selected[0])
            if selected[0].base.slot == EquipmentSlot.ACCESSORY:
                await self.database.update_user_equipment(
                    guild_id, member_id, None, acc_slot_2=True
                )

        if len(selected) == 2:
            # Accessory
            await self.database.update_user_equipment(guild_id, member_id, selected[0])
            await self.database.update_user_equipment(
                guild_id, member_id, selected[1], acc_slot_2=True
            )

        for gear in selected:
            message = f"{interaction.user.display_name} equipped {gear.rarity.value} {gear.name} ({gear.id}) in {gear.slot.name}."
            self.logger.log(interaction.guild_id, message, self.log_name)

        await self.refresh_gear_select(interaction, selected[0].base.slot, view_id)

    async def update_gear_lock(
        self,
        interaction: discord.Interaction,
        selected: list[Gear],
        lock: bool,
        view_id: int,
    ):
        if not await self.encounter_check(interaction):
            return

        if selected is None or len(selected) <= 0:
            return

        gear_slot = None
        for gear in selected:
            if gear_slot is None:
                gear_slot = gear.base.slot
            await self.database.update_lock_gear_by_id(gear.id, lock=lock)

        if gear_slot is None:
            event = UIEvent(
                UIEventType.MAIN_MENU_STATE_CHANGE,
                (interaction, MenuState.GEAR, False),
                view_id,
            )
            await self.controller.dispatch_ui_event(event)
            return

        if gear_slot == EquipmentSlot.SKILL:
            await self.refresh_skill_view(interaction, SkillViewState.MANAGE, view_id)
            return

        for gear in selected:
            lock_str = "locked" if lock else "unlocked"
            message = f"{interaction.user.display_name} {lock_str} {gear.rarity.value} {gear.name} ({gear.id})."
            self.logger.log(interaction.guild_id, message, self.log_name)

        await self.refresh_gear_select(interaction, gear_slot, view_id)

    async def dismantle_gear(
        self,
        interaction: discord.Interaction,
        selected: list[Gear],
        scrap_all: bool,
        view_id: int,
        gear_slot: EquipmentSlot = None,
    ):
        if not await self.encounter_check(interaction):
            return
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        gear_to_scrap = selected

        if scrap_all:
            if gear_slot == EquipmentSlot.SKILL:
                gear_to_scrap = await self.database.get_scrappable_equipment_by_user(
                    guild_id, member_id, type=Base.SKILL
                )
            else:
                gear_to_scrap = await self.database.get_scrappable_equipment_by_user(
                    guild_id, member_id
                )

        await self.gear_manager.scrap_gear(interaction.user, guild_id, gear_to_scrap)

        if gear_slot == EquipmentSlot.ANY:
            await self.refresh_enchantment_view(interaction, view_id)
            return

        if gear_slot is None:
            event = UIEvent(
                UIEventType.MAIN_MENU_STATE_CHANGE,
                (interaction, MenuState.GEAR, False),
                view_id,
            )
            await self.controller.dispatch_ui_event(event)
            return

        if gear_slot == EquipmentSlot.SKILL:
            if scrap_all:
                event = UIEvent(
                    UIEventType.MAIN_MENU_STATE_CHANGE,
                    (interaction, MenuState.SKILLS, False),
                    view_id,
                )
                await self.controller.dispatch_ui_event(event)
                return
            await self.refresh_skill_view(interaction, SkillViewState.MANAGE, view_id)
            return

        await self.refresh_gear_select(interaction, gear_slot, view_id)

    async def refresh_skill_view(
        self, interaction: discord.Interaction, state: SkillViewState, view_id: int
    ):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        character = await self.actor_manager.get_character(interaction.user)

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        user_skills = await self.database.get_user_skill_inventory(guild_id, member_id)

        view = SkillSelectView(
            self.controller, interaction, character, user_skills, scrap_balance, state
        )

        embeds = []
        embeds.append(SelectSkillHeadEmbed(interaction.user))

        loading_embed = discord.Embed(
            title="Loading Skills", color=discord.Colour.light_grey()
        )
        self.embed_manager.add_text_bar(loading_embed, "", "Please Wait...")
        loading_embed.set_thumbnail(url=self.bot.user.display_avatar)
        embeds.append(loading_embed)

        view: SkillSelectView = self.controller.get_view(view_id)
        await view.refresh_ui(
            character=character,
            skill_inventory=user_skills,
            scrap_balance=scrap_balance,
            state=state,
        )

    async def open_skill_view(
        self, interaction: discord.Interaction, state: SkillViewState, view_id: int
    ):
        if not await self.encounter_check(interaction):
            return
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        character = await self.actor_manager.get_character(interaction.user)

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        user_skills = await self.database.get_user_skill_inventory(guild_id, member_id)

        view = SkillSelectView(
            self.controller, interaction, character, user_skills, scrap_balance, state
        )

        embeds = []
        embeds.append(SelectSkillHeadEmbed(interaction.user))

        loading_embed = discord.Embed(
            title="Loading Skills", color=discord.Colour.light_grey()
        )
        self.embed_manager.add_text_bar(loading_embed, "", "Please Wait...")
        loading_embed.set_thumbnail(url=self.bot.user.display_avatar)
        embeds.append(loading_embed)

        message = await interaction.original_response()
        await message.edit(embeds=embeds, view=view, attachments=[])
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def set_selected_skills(
        self, interaction: discord.Interaction, skills: dict[int, Skill], view_id: int
    ):
        if not await self.encounter_check(interaction):
            return
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        dupe_check: list[int] = []

        for _, skill in skills.items():
            if skill.id in dupe_check:
                await interaction.followup.send(
                    "You cannot equip the same skill multiple times.",
                    ephemeral=True,
                )
                return
            dupe_check.append(skill.id)

        for slot, skill in skills.items():
            message = f"{interaction.user.display_name} equipped {skill.rarity.value} {skill.name} ({skill.id}) in slot {slot}."
            self.logger.log(interaction.guild_id, message, self.log_name)

        await self.database.set_selected_user_skills(guild_id, member_id, skills)

        event = UIEvent(
            UIEventType.MAIN_MENU_STATE_CHANGE,
            (interaction, MenuState.SKILLS, False),
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def use_forge(
        self,
        interaction: discord.Interaction,
        level: int,
        slot: EquipmentSlot,
    ):
        if not await self.encounter_check(interaction):
            return
        drop = await self.forge_manager.use_scrap(interaction.user, slot, level)

        if drop is None:
            await interaction.followup.send(
                "You don't have enough scrap for this. Go and scrap some equipment you no longer need and come back.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(embed=drop.get_embed(), ephemeral=True)

    async def clear_forge_inventory(
        self, interaction: discord.Interaction, view_id: int
    ):
        if not await self.encounter_check(interaction):
            return

        await self.forge_manager.clear_forge_inventory(interaction.user)

        view: EnchantmentView = self.controller.get_view(view_id)
        await view.refresh_ui()

    async def combine_forge_inventory(
        self, interaction: discord.Interaction, inventory: ForgeInventory, view_id: int
    ):
        if not await self.encounter_check(interaction):
            return

        result = await self.forge_manager.combine(interaction.user)

        if result is None:
            await interaction.followup.send("Not a valid recipe!", ephemeral=True)
            return

        await interaction.followup.send(embed=result.get_embed(), ephemeral=True)

        view: EnchantmentView = self.controller.get_view(view_id)
        await view.refresh_ui()

    async def apply_gear_enchantment(
        self,
        interaction: discord.Interaction,
        gear: Gear,
        enchantments: list[Enchantment],
        view_id: int,
    ):
        if not await self.encounter_check(interaction):
            return

        effects = []
        new_gear = gear
        for enchantment in enchantments:
            match enchantment.base_enchantment.enchantment_effect:
                case EnchantmentEffect.EFFECT:
                    effects.append(enchantment)
                case EnchantmentEffect.CRAFTING:
                    handler: EnchantmentCraftHandler = (
                        EnchantmentCraftHandler.get_handler(
                            self.controller,
                            enchantment.base_enchantment.enchantment_type,
                        )
                    )
                    new_gear = await handler.handle(enchantment, gear)
                    await self.database.delete_gear_by_ids([enchantment.id])

        if len(effects) > 0:
            new_gear = await self.database.log_user_gear_enchantment(new_gear, effects)

        message = f"{interaction.user.display_name} Enchanted {gear.rarity.value} {gear.name} ({gear.id}) "
        message += f"with {", ".join([f"{enchantment.rarity.value} {enchantment.name}" for enchantment in enchantments])}."
        self.logger.log(interaction.guild_id, message, self.log_name)

        await self.refresh_enchantment_view(interaction, view_id, new_gear)

    async def open_enchantment_view(
        self, interaction: discord.Interaction, gear: Gear | None, view_id: int
    ):
        guild_id = interaction.guild.id
        member_id = interaction.user.id

        if not await self.encounter_check(interaction):
            return

        character = await self.actor_manager.get_character(interaction.user)

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        user_enchantments = await self.database.get_user_enchantment_inventory(
            guild_id, member_id
        )

        view = EnchantmentView(
            self.controller,
            interaction,
            character,
            user_enchantments,
            scrap_balance,
            gear,
        )

        message = await interaction.original_response()
        await message.edit(view=view, attachments=[])
        view.set_message(message)
        await view.refresh_ui()
        self.controller.detach_view_by_id(view_id)

    async def refresh_enchantment_view(
        self, interaction: discord.Interaction, view_id: int, gear: Gear | None = None
    ):
        guild_id = interaction.guild.id
        member_id = interaction.user.id

        character = await self.actor_manager.get_character(interaction.user)

        user_items = await self.database.get_item_counts_by_user(
            guild_id, member_id, item_types=[ItemType.SCRAP]
        )
        scrap_balance = 0
        if ItemType.SCRAP in user_items:
            scrap_balance = user_items[ItemType.SCRAP]

        user_enchantments = await self.database.get_user_enchantment_inventory(
            guild_id, member_id
        )

        view: EnchantmentView = self.controller.get_view(view_id)
        await view.refresh_ui(
            character=character,
            enchantment_inventory=user_enchantments,
            scrap_balance=scrap_balance,
            gear=gear,
        )
