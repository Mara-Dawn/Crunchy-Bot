import contextlib
from enum import Enum

import discord
from combat.actors import Character
from combat.gear.types import EquipmentSlot, Rarity
from combat.skills.skill import CharacterSkill, Skill
from combat.skills.skills import EmptySkill
from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.elements import (
    BackButton,
    CurrentPageButton,
    ImplementsBack,
    ImplementsLocking,
    ImplementsPages,
    ImplementsScrapping,
    LockButton,
    PageButton,
    ScrapBalanceButton,
    ScrapSelectedButton,
    UnlockButton,
)
from view.combat.embed import SelectSkillHeadEmbed
from view.combat.equipment_view import EquipmentViewState
from view.view_menu import ViewMenu


class SkillViewState(Enum):
    EQUIP = 0
    MANAGE = 1
    SELECT_MODE = 2


class SkillSelectView(
    ViewMenu, ImplementsPages, ImplementsBack, ImplementsLocking, ImplementsScrapping
):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        character: Character,
        skill_inventory: list[Skill],
        scrap_balance: int,
        state: SkillViewState,
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.member = interaction.user
        self.guild_id = interaction.guild_id
        self.skills = skill_inventory
        self.character = character
        self.equipped_skill_slots = character.skill_slots
        self.equipped_skills = character.skills
        self.scrap_balance = scrap_balance

        self.current_page = 0
        self.selected = []
        self.selected_slots = {}

        if state == SkillViewState.EQUIP:
            self.selected_slots = {k: v for k, v in self.equipped_skill_slots.items()}

        self.equipped_skill_slot_data = {}

        for slot, skill in self.equipped_skill_slots.items():
            if skill is None:
                self.equipped_skill_slot_data[slot] = None
                continue
            self.equipped_skill_slot_data[slot] = character.get_skill_data(skill)

        self.filter = EquipmentSlot.SKILL
        self.filtered_items = []
        self.display_items = []
        self.display_skill_data = []
        self.item_count = 0
        self.page_count = 1
        self.filter_items()
        self.message = None
        self.state = state
        self.loaded = False

        self.controller_type = ControllerType.EQUIPMENT
        self.controller.register_view(self)
        self.refresh_elements()
        self.embed_manager: CombatEmbedManager = controller.get_service(
            CombatEmbedManager
        )

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

        if event.view_id != self.id:
            return

    def filter_items(self):
        self.filtered_items = [
            gear for gear in self.skills if gear.base.slot == self.filter
        ]
        self.item_count = len(self.filtered_items)
        self.page_count = int(self.item_count / SelectSkillHeadEmbed.ITEMS_PER_PAGE) + (
            self.item_count % SelectSkillHeadEmbed.ITEMS_PER_PAGE > 0
        )
        self.page_count = max(self.page_count, 1)

        self.filtered_items = sorted(
            self.filtered_items,
            key=lambda x: (
                (x.id in [skill.id for skill in self.equipped_skills]),
                # x.locked,
                x.level,
                Skill.RARITY_SORT_MAP[x.rarity],
                Skill.EFFECT_SORT_MAP[x.base_skill.skill_effect],
            ),
            reverse=True,
        )

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        self.selected = []
        # self.selected_slots = {}
        await self.refresh_ui()

    async def equip_selected_skill(self, interaction: discord.Interaction, slot: int):
        await interaction.response.defer()

        selected = {
            slot: skill
            for slot, skill in self.equipped_skill_slots.items()
            if skill is not None and skill.id is not None and skill.id > 0
        }

        selected[slot] = self.selected[0]

        event = UIEvent(
            UIEventType.SKILLS_EQUIP,
            (interaction, selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def select_skills(self, interaction: discord.Interaction):
        await interaction.response.defer()

        selected = {
            slot: skill
            for slot, skill in self.selected_slots.items()
            if skill is not None and skill.id is not None and skill.id > 0
        }

        event = UIEvent(
            UIEventType.SKILLS_EQUIP,
            (interaction, selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def scrap_selected(
        self, interaction: discord.Interaction, scrap_all: bool = False
    ):
        await interaction.response.defer()

        scrappable = [item for item in self.selected if not item.locked]

        event = UIEvent(
            UIEventType.GEAR_DISMANTLE,
            (interaction, scrappable, scrap_all, self.filter),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def lock_selected(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_LOCK,
            (interaction, self.selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def unlock_selected(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_UNLOCK,
            (interaction, self.selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def go_back(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_OPEN_OVERVIEW,
            (interaction, EquipmentViewState.SKILLS),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def change_skill(self, interaction: discord.Interaction, slot: EquipmentSlot):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_OPEN_SECELT,
            (interaction, slot),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def cancel_select_mode(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.state = SkillViewState.MANAGE
        await self.refresh_ui()

    async def enable_select_mode(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.state = SkillViewState.SELECT_MODE
        await self.refresh_ui()

    def refresh_elements(self, disabled: bool = False):
        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        if not self.loaded:
            disabled = True

        disable_equip = disabled
        disable_dismantle = disabled
        disable_locking = disabled
        for equipped_skill_data in self.selected:
            if equipped_skill_data is None:
                continue
            if equipped_skill_data.id in [skill.id for skill in self.equipped_skills]:
                disable_dismantle = True

            if equipped_skill_data.id is None or equipped_skill_data.id < 0:
                # Default Gear
                disable_dismantle = True

        if len(self.selected) <= 0:
            disable_locking = True
            disable_equip = True
            disable_dismantle = True

        self.clear_items()

        match self.state:
            case SkillViewState.EQUIP:
                if len(self.display_skill_data) > 0:
                    for slot, equipped_skill_data in self.selected_slots.items():
                        selected_skill_data = None
                        if equipped_skill_data is not None:
                            selected_skill_data = self.character.get_skill_data(
                                equipped_skill_data
                            )
                        self.add_item(
                            Dropdown(
                                self.display_skill_data,
                                self.equipped_skill_slot_data,
                                [selected_skill_data],
                                self.state,
                                row=slot + 1,
                            )
                        )
                self.add_item(PageButton("<", False, row=0))
                self.add_item(SelectButton(disabled=False, row=0))
                self.add_item(PageButton(">", True, row=0))
                self.add_item(CurrentPageButton(page_display, row=0))
                self.add_item(BackButton(row=0))

            case SkillViewState.MANAGE:
                if len(self.selected) > 1:
                    disable_equip = True
                elif len(self.selected) == 1:
                    equipped_skill_data = self.selected[0]
                    if equipped_skill_data.id in [
                        skill.id for skill in self.equipped_skills
                    ]:
                        disable_equip = True

                if len(self.display_skill_data) > 0:
                    selected_skill_data = []
                    for equipped_skill_data in self.selected:
                        skill_data = self.character.get_skill_data(equipped_skill_data)
                        selected_skill_data.append(skill_data)
                    self.add_item(
                        Dropdown(
                            self.display_skill_data,
                            self.equipped_skill_slot_data,
                            selected_skill_data,
                            self.state,
                            min_values=0,
                            max_values=5,
                        )
                    )

                self.add_item(PageButton("<", False))
                self.add_item(SelectSingleButton(disabled=disable_equip))
                self.add_item(PageButton(">", True))
                self.add_item(CurrentPageButton(page_display))
                self.add_item(ScrapBalanceButton(self.scrap_balance))
                self.add_item(ScrapSelectedButton(disabled=disable_dismantle))
                self.add_item(LockButton(disabled=disable_locking))
                self.add_item(UnlockButton(disabled=disable_locking))
                self.add_item(BackButton())

            case SkillViewState.SELECT_MODE:
                if len(self.selected) > 1:
                    disable_equip = True

                if len(self.display_skill_data) > 0:
                    selected_skill_data = []
                    for equipped_skill_data in self.selected:
                        skill_data = self.character.get_skill_data(equipped_skill_data)
                        selected_skill_data.append(skill_data)
                    self.add_item(
                        Dropdown(
                            self.display_skill_data,
                            self.equipped_skill_slot_data,
                            selected_skill_data,
                            self.state,
                            min_values=0,
                            max_values=5,
                            disabled=True,
                        )
                    )

                self.add_item(PageButton("<", False, disabled=True, row=1))
                self.add_item(
                    SelectSingleButton(label="Select a Slot:", disabled=True, row=1)
                )
                self.add_item(PageButton(">", True, disabled=True, row=1))
                self.add_item(CurrentPageButton(page_display, row=1))
                self.add_item(ScrapBalanceButton(self.scrap_balance, row=1))

                for slot, equipped_skill_data in self.equipped_skill_slot_data.items():
                    self.add_item(
                        SkillSlotButton(
                            equipped_skill_data,
                            slot,
                        )
                    )
                self.add_item(CancelButton(row=3))

    async def refresh_ui(
        self,
        character: Character = None,
        skill_inventory: list[Skill] = None,
        scrap_balance: int = None,
        state: SkillViewState = None,
        disabled: bool = False,
        no_embeds: bool = False,
    ):
        if self.message is None:
            return

        if character is not None:
            self.character = character

        if skill_inventory is not None:
            self.skills = skill_inventory
            self.filter_items()
            self.current_page = min(self.current_page, (self.page_count - 1))

        if scrap_balance is not None:
            self.scrap_balance = scrap_balance

        if state is not None:
            self.state = state

        if self.selected is None or len(self.selected) <= 0:
            disabled = True

        if no_embeds:
            self.refresh_elements(disabled)
            await self.message.edit(view=self)
            return

        start_offset = SelectSkillHeadEmbed.ITEMS_PER_PAGE * self.current_page
        end_offset = min(
            (start_offset + SelectSkillHeadEmbed.ITEMS_PER_PAGE),
            len(self.filtered_items),
        )
        self.display_items = self.filtered_items[start_offset:end_offset]

        if None not in [self.scrap_balance, self.skills]:
            self.loaded = True

        self.display_skill_data = []
        embeds = []
        files = {}

        embeds.append(SelectSkillHeadEmbed(self.member))

        for skill in self.display_items:
            equipped = False
            if skill.id in [skill.id for skill in self.equipped_skills]:
                equipped = True

            skill_data = self.character.get_skill_data(skill)
            self.display_skill_data.append(skill_data)

            embeds.append(
                skill_data.get_embed(
                    equipped=equipped, show_full_data=True, show_locked_state=True
                )
            )
            file_path = f"./{skill.base.image_path}{skill.base.image}"
            if file_path not in files:
                file = discord.File(
                    file_path,
                    skill.base.attachment_name,
                )
                files[file_path] = file

        self.refresh_elements(disabled)

        if len(self.display_items) <= 0:
            empty_embed = discord.Embed(
                title="Empty", color=discord.Colour.light_grey()
            )
            self.embed_manager.add_text_bar(
                empty_embed, "", "Seems like there is nothing here."
            )
            empty_embed.set_thumbnail(url=self.controller.bot.user.display_avatar)
            embeds.append(empty_embed)

        files = list(files.values())

        await self.message.edit(embeds=embeds, attachments=files, view=self)
        # try:
        #     await self.message.edit(embeds=embeds, attachments=files, view=self)
        # except (discord.NotFound, discord.HTTPException):
        #     self.controller.detach_view(self)

    async def set_selected(
        self,
        interaction: discord.Interaction,
        skill_ids: list[int],
        index: int = 0,
    ):
        await interaction.response.defer()

        if self.state == SkillViewState.EQUIP:
            skill_list = [skill for skill in self.skills if skill.id in skill_ids]
            if len(skill_list) <= 0:
                self.selected_slots[index] = None
            else:
                self.selected_slots[index] = skill_list[0]

        self.selected = [skill for skill in self.skills if skill.id in skill_ids]

        no_embeds = self.state == SkillViewState.EQUIP
        await self.refresh_ui(no_embeds=no_embeds)

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class SelectSingleButton(discord.ui.Button):

    def __init__(self, label: str = "Equip", disabled: bool = True, row: int = 2):

        super().__init__(
            label=label,
            style=discord.ButtonStyle.green,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.enable_select_mode(interaction)


class SelectButton(discord.ui.Button):

    def __init__(self, disabled: bool = True, row: int = 2):

        super().__init__(
            label="Confirm",
            style=discord.ButtonStyle.green,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.select_skills(interaction)


class CancelButton(discord.ui.Button):

    def __init__(self, disabled: bool = False, row: int = 2):

        super().__init__(
            label="Cancel",
            style=discord.ButtonStyle.red,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.cancel_select_mode(interaction)


class SkillSlotButton(discord.ui.Button):

    def __init__(
        self, current: CharacterSkill, slot: int, disabled: bool = False, row: int = 2
    ):
        label = "Empty"
        self.skill = current
        self.slot = slot
        if current is not None:
            label = f"{current.skill.name}"
            if current.stacks_left() is not None:
                label += f" ({current.stacks_left()}/{current.skill.base_skill.stacks})"
            if current.skill.id is None:
                disabled = True

        super().__init__(
            label=f"{slot+1}: {label}",
            style=discord.ButtonStyle.green,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.equip_selected_skill(interaction, self.slot)


class Dropdown(discord.ui.Select):

    def __init__(
        self,
        skill_data: list[CharacterSkill],
        equipped_data: dict[int, CharacterSkill],
        selected_data: list[CharacterSkill],
        state: SkillViewState,
        disabled: bool = False,
        row: int = 0,
        min_values: int = 1,
        max_values: int = 1,
    ):
        self.row = row
        options = []
        default = False

        available = skill_data

        if state == SkillViewState.EQUIP:
            empty_skill = Skill(
                base_skill=EmptySkill(),
                rarity=Rarity.DEFAULT,
                level=1,
                id=-row,
            )
            empty = CharacterSkill(empty_skill, 0, 0, 0, 0)
            available = skill_data + [empty]
            slot = row - 1
            equipped = equipped_data[slot]

            if equipped is not None:
                if equipped.skill.id not in [data.skill.id for data in skill_data]:
                    available.append(equipped)
                if equipped.skill.id is None:
                    # disabled = True
                    available = [equipped]

        max_values = min(max_values, len(available))

        equipped_ids = [
            data.skill.id for data in equipped_data.values() if data is not None
        ]
        selected_ids = [
            data.skill.id if data is not None else -row for data in selected_data
        ]

        for data in available:
            skill = data.skill

            name = skill.name
            name_prefix = f"[{skill.rarity.value}] "
            name_suffix = ""

            if name is None or name == "":
                name = skill.base.slot.value

            if skill.id is None:
                # Weaponskill
                name_prefix = ""
                name_suffix = " [WEAPON] "
            elif skill.id in equipped_ids:
                name_suffix = " [EQUIPPED]"
            elif skill.locked:
                name_suffix = " [🔒]"

            label = f"{name_prefix}{name}{name_suffix}"
            description = []

            if skill.id is not None:
                description.append(f"ILVL: {skill.level}")
                description.append(
                    f"USE: {data.stacks_left()}/{skill.base_skill.stacks}"
                )
            description.append(f"MIN: {data.min_roll}")
            description.append(f"MAX: {data.max_roll}")
            description = " | ".join(description)
            description = (
                (description[:95] + "..") if len(description) > 95 else description
            )

            if skill.id is not None and skill.id < 0:
                label = skill.name
                description = ""

            default = skill.id in selected_ids

            if (
                state == SkillViewState.EQUIP
                and selected_data[0] is None
                and skill.id < 0
            ):
                default = True

            option = discord.SelectOption(
                label=label,
                description=description,
                value=skill.id if skill is not None and skill.id is not None else 0,
                default=default,
            )
            options.append(option)

        placeholder = "Select one or more Skills."
        if state == SkillViewState.EQUIP:
            placeholder = "Select a Skill to equip."

        super().__init__(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected(
                interaction, [int(value) for value in self.values], index=self.row - 1
            )
