from enum import Enum

import discord
from combat.actors import Character
from combat.gear.types import (
    EquipmentSlot,
    Rarity,
)
from control.combat.combat_gear_manager import CombatGearManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.embed import (
    AttributesHeadEmbed,
    EquipmentHeadEmbed,
    ForgeEmbed,
    SkillsHeadEmbed,
)
from view.view_menu import ViewMenu


class EquipmentViewState(Enum):
    GEAR = 0
    STATS = 1
    SKILLS = 2
    FORGE = 3


class EquipmentView(ViewMenu):

    SCRAP_ILVL_MAP = {
        1: 15,
        2: 40,
        3: 80,
        4: 120,
        5: 180,
        6: 240,
        7: 300,
        8: 350,
        9: 400,
        10: 450,
        11: 500,
        12: 550,
    }

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        character: Character,
        scrap_balance: int,
        guild_level: int,
        state: EquipmentViewState = EquipmentViewState.GEAR,
    ):
        super().__init__(timeout=None)
        self.controller = controller
        self.character = character
        self.member_id = character.member.id
        self.guild_id = character.member.guild.id
        self.member = interaction.user
        self.state = state
        self.scrap_balance = scrap_balance
        self.loaded = False

        self.guild_level = guild_level
        self.max_rarity = Rarity.NORMAL
        for rarity, level in CombatGearManager.MIN_RARITY_LVL.items():
            if level < self.guild_level:
                self.max_rarity = rarity
            else:
                break

        self.forge_options = {
            level: scrap
            for level, scrap in self.SCRAP_ILVL_MAP.items()
            if level <= self.guild_level
        }
        self.max_forge_level = max(self.forge_options.keys())
        self.selected: int = self.max_forge_level

        self.controller_type = ControllerType.EQUIPMENT
        self.controller.register_view(self)
        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.SCRAP_BALANCE_CHANGED:
                guild_id = event.payload[0]
                member_id = event.payload[1]
                balance = event.payload[2]
                if member_id != self.member_id or guild_id != self.guild_id:
                    return
                await self.refresh_ui(scrap_balance=balance)
                return

    def refresh_elements(self, disabled: bool = False):

        if not self.loaded:
            disabled = True

        gear_button_selected = False
        stats_button_selected = False
        skills_button_selected = False
        forge_button_selected = False

        self.clear_items()
        match self.state:
            case EquipmentViewState.GEAR:
                gear_button_selected = True
                self.add_item(SelectGearSlot(EquipmentSlot.WEAPON, disabled=disabled))
                self.add_item(SelectGearSlot(EquipmentSlot.HEAD, disabled=disabled))
                self.add_item(SelectGearSlot(EquipmentSlot.BODY, disabled=disabled))
                self.add_item(SelectGearSlot(EquipmentSlot.LEGS, disabled=disabled))
                self.add_item(
                    SelectGearSlot(EquipmentSlot.ACCESSORY, disabled=disabled)
                )
                self.add_item(ScrapAllButton(disabled=disabled))
            case EquipmentViewState.STATS:
                stats_button_selected = True
            case EquipmentViewState.SKILLS:
                skills_button_selected = True
                self.add_item(SkillManageButton(disabled=disabled))
                self.add_item(SkillEquipButton(disabled=disabled))
                self.add_item(
                    ScrapAllButton(slot=EquipmentSlot.SKILL, disabled=disabled)
                )
            case EquipmentViewState.FORGE:
                forge_button_selected = True
                self.add_item(ForgeDropdown(self.forge_options, self.selected))
                self.add_item(ForgeUseButton())

        self.add_item(GearButton(selected=gear_button_selected, disabled=disabled))
        self.add_item(StatsButton(selected=stats_button_selected, disabled=disabled))
        self.add_item(SkillsButton(selected=skills_button_selected, disabled=disabled))
        self.add_item(ForgeButton(selected=forge_button_selected, disabled=disabled))
        self.add_item(ScrapBalanceButton(self.scrap_balance))

    async def refresh_ui(
        self,
        character: Character = None,
        scrap_balance: int = None,
        disabled: bool = False,
    ):
        if self.message is None:
            return

        if scrap_balance is not None:
            self.scrap_balance = scrap_balance

        if character is not None:
            self.character = character

        if self.character is not None and self.scrap_balance is not None:
            self.loaded = True

        self.refresh_elements(disabled=disabled)
        embeds = []
        files: list[discord.File] = []
        match self.state:
            case EquipmentViewState.GEAR:
                embeds.append(EquipmentHeadEmbed(self.member))
                embeds.append(self.character.equipment.weapon.get_embed())
                files.append(
                    discord.File(
                        (
                            f"./{self.character.equipment.weapon.base.image_path}"
                            f"{self.character.equipment.weapon.base.image}"
                        ),
                        self.character.equipment.weapon.base.attachment_name,
                    )
                )
                embeds.append(self.character.equipment.head_gear.get_embed())
                files.append(
                    discord.File(
                        (
                            f"./{self.character.equipment.head_gear.base.image_path}"
                            f"{self.character.equipment.head_gear.base.image}"
                        ),
                        self.character.equipment.head_gear.base.attachment_name,
                    )
                )
                embeds.append(self.character.equipment.body_gear.get_embed())
                files.append(
                    discord.File(
                        (
                            f"./{self.character.equipment.body_gear.base.image_path}"
                            f"{self.character.equipment.body_gear.base.image}"
                        ),
                        self.character.equipment.body_gear.base.attachment_name,
                    )
                )
                embeds.append(self.character.equipment.leg_gear.get_embed())
                files.append(
                    discord.File(
                        (
                            f"./{self.character.equipment.leg_gear.base.image_path}"
                            f"{self.character.equipment.leg_gear.base.image}"
                        ),
                        self.character.equipment.leg_gear.base.attachment_name,
                    )
                )
                embeds.append(self.character.equipment.accessory_1.get_embed())
                files.append(
                    discord.File(
                        (
                            f"./{self.character.equipment.accessory_1.base.image_path}"
                            f"{self.character.equipment.accessory_1.base.image}"
                        ),
                        self.character.equipment.accessory_1.base.attachment_name,
                    )
                )
                embeds.append(self.character.equipment.accessory_2.get_embed())
                if (
                    self.character.equipment.accessory_1.base.attachment_name
                    != self.character.equipment.accessory_2.base.attachment_name
                ):
                    files.append(
                        discord.File(
                            (
                                f"./{self.character.equipment.accessory_2.base.image_path}"
                                f"{self.character.equipment.accessory_2.base.image}"
                            ),
                            self.character.equipment.accessory_2.base.attachment_name,
                        )
                    )
            case EquipmentViewState.STATS:
                embeds.append(AttributesHeadEmbed(self.member))
                title = f"{self.member.display_name}'s Attributes"
                embeds.append(self.character.equipment.get_embed(title=title))
            case EquipmentViewState.SKILLS:
                embed = SkillsHeadEmbed(self.member)
                embeds.append(embed)
                for skill in self.character.skills:
                    skill_embed = self.character.get_skill_data(skill).get_embed(
                        show_data=True, show_full_data=True
                    )
                    embeds.append(skill_embed)
                    file = discord.File(
                        f"./{skill.base_skill.image_path}{skill.base_skill.image}",
                        skill.base_skill.attachment_name,
                    )
                    if file.filename not in [file.filename for file in files]:
                        files.append(file)
            case EquipmentViewState.FORGE:
                embed = ForgeEmbed(
                    self.member,
                    self.guild_level,
                    self.max_rarity,
                )
                embeds.append(embed)
                # file = discord.File("./forge.png", "forge.png")
                # files.append(file)

        try:
            await self.message.edit(embeds=embeds, attachments=files, view=self)
        except (discord.NotFound, discord.HTTPException):
            self.controller.detach_view(self)

    async def set_state(
        self, state: EquipmentViewState, interaction: discord.Interaction
    ):
        await interaction.response.defer()
        self.state = state
        await self.refresh_ui()

    async def set_selected(self, interaction: discord.Interaction, item_level: int):
        await interaction.response.defer()
        self.selected = item_level
        await self.refresh_ui()

    async def change_gear(self, interaction: discord.Interaction, slot: EquipmentSlot):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_OPEN_SECELT,
            (interaction, slot),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def use_forge(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        event = UIEvent(
            UIEventType.FORGE_USE,
            (interaction, self.selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def dismantle_gear(
        self, interaction: discord.Interaction, slot: EquipmentSlot = None
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_DISMANTLE,
            (interaction, [], True, slot),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def open_skill_equip_view(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.SKILL_EQUIP_VIEW,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def open_skill_manage_view(self, interaction: discord.Interaction):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.SKILL_MANAGE_VIEW,
            interaction,
            self.id,
        )
        await self.controller.dispatch_ui_event(event)


class GearButton(discord.ui.Button):

    def __init__(self, selected: bool = False, disabled: bool = True):
        color = discord.ButtonStyle.grey

        label = "Gear"
        if selected:
            label = f">{label}<"
            disabled = True

        super().__init__(label=label, style=color, disabled=disabled, row=0)

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.set_state(EquipmentViewState.GEAR, interaction)


class StatsButton(discord.ui.Button):

    def __init__(self, selected: bool = False, disabled: bool = True):
        color = discord.ButtonStyle.grey

        label = "Attributes"
        if selected:
            label = f">{label}<"
            disabled = True

        super().__init__(
            label=label,
            style=color,
            disabled=disabled,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.set_state(EquipmentViewState.STATS, interaction)


class SkillsButton(discord.ui.Button):

    def __init__(self, selected: bool = False, disabled: bool = True):
        color = discord.ButtonStyle.grey

        label = "Skills"
        if selected:
            label = f">{label}<"
            disabled = True

        super().__init__(
            label=label,
            style=color,
            disabled=disabled,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.set_state(EquipmentViewState.SKILLS, interaction)


class SelectGearSlot(discord.ui.Button):

    def __init__(
        self,
        slot: EquipmentSlot,
        selected: bool = False,
        disabled: bool = False,
        row: int = 1,
    ):

        label = slot.value
        if selected:
            label = f">{label}<"
            disabled = True

        super().__init__(
            label=label,
            style=discord.ButtonStyle.green,
            disabled=disabled,
            row=row,
        )
        self.slot = slot

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.change_gear(interaction, self.slot)


class ForgeButton(discord.ui.Button):

    def __init__(self, selected: bool = False, disabled: bool = True):
        color = discord.ButtonStyle.grey

        label = "Forge"
        if selected:
            label = f">{label}<"
            disabled = True

        super().__init__(
            label=label,
            style=color,
            row=0,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view

        if await view.interaction_check(interaction):
            await view.set_state(EquipmentViewState.FORGE, interaction)


class ScrapBalanceButton(discord.ui.Button):

    def __init__(self, balance: int):
        self.balance = balance
        super().__init__(label=f"⚙️{balance}", style=discord.ButtonStyle.blurple, row=0)

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)


class SkillManageButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Manage Skill Inventory",
            style=discord.ButtonStyle.green,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view

        if await view.interaction_check(interaction):
            await view.open_skill_manage_view(interaction)


class SkillEquipButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Quick Select",
            style=discord.ButtonStyle.green,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view

        if await view.interaction_check(interaction):
            await view.open_skill_equip_view(interaction)


class ScrapAllButton(discord.ui.Button):

    def __init__(self, slot: EquipmentSlot = None, disabled: bool = False):
        self.slot = slot

        label = "Scrap non locked Gear"
        if slot == EquipmentSlot.SKILL:
            label = "Scrap non locked Skills"

        super().__init__(
            label=label,
            style=discord.ButtonStyle.red,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view

        if await view.interaction_check(interaction):
            await view.dismantle_gear(interaction, slot=self.slot)


class ForgeDropdown(discord.ui.Select):

    def __init__(
        self,
        scrap_options: dict[int, int],
        selected: int,
        disabled: bool = False,
    ):
        options = []

        for item_level, scrap_amount in scrap_options.items():
            label = f"⚙️{scrap_amount} Scrap"
            description = f"Gain a random level {item_level} item or skill."

            option = discord.SelectOption(
                label=label,
                description=description,
                value=item_level,
                default=(item_level == selected),
            )
            options.append(option)

        super().__init__(
            placeholder="Select one or more pieces of equipment.",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(
                interaction, [int(value) for value in self.values][0]
            )


class ForgeUseButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Throw Scrap into Forge",
            style=discord.ButtonStyle.green,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view

        if await view.interaction_check(interaction):
            await view.use_forge(interaction)
