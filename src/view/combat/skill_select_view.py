import contextlib
from enum import Enum

import discord
from combat.actors import Character
from combat.gear.gear import Gear
from combat.gear.types import EquipmentSlot, Rarity
from combat.skills.skill import Skill
from combat.skills.skills import EmptySkill
from control.combat.combat_embed_manager import CombatEmbedManager
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.embed import SelectSkillHeadEmbed
from view.view_menu import ViewMenu


class SkillViewState(Enum):
    EQUIP = 0
    MANAGE = 1


class SkillSelectView(ViewMenu):

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
        self.current_skills = character.skills
        self.scrap_balance = scrap_balance

        self.current_page = 0
        self.selected: dict[int, Gear] = []

        for index in range(4):
            if len(self.current_skills) > index:
                self.selected.append(self.current_skills[index])
            else:
                self.selected.append(
                    Skill(
                        base_skill=EmptySkill(),
                        rarity=Rarity.DEFAULT,
                        level=1,
                        id=-index,
                    )
                )

        self.filter = EquipmentSlot.SKILL
        self.filtered_items = []
        self.display_items = []
        self.item_count = 0
        self.page_count = 1
        self.filter_items()
        self.message = None
        self.state = state

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
                x.locked,
                x.level,
                Skill.RARITY_SORT_MAP[x.rarity],
                Skill.EFFECT_SORT_MAP[x.base_skill.skill_effect],
                (x.id in [skill.id for skill in self.current_skills]),
            ),
            reverse=True,
        )

    async def flip_page(self, interaction: discord.Interaction, right: bool = False):
        await interaction.response.defer()
        self.current_page = (self.current_page + (1 if right else -1)) % self.page_count
        await self.refresh_ui()

    async def select_skills(self, interaction: discord.Interaction):
        await interaction.response.defer()

        selected = [
            skill for skill in self.selected if skill.id is not None and skill.id > 0
        ]

        event = UIEvent(
            UIEventType.SKILLS_EQUIP,
            (interaction, selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def dismantle_skill(
        self, interaction: discord.Interaction, scrap_all: bool = False
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_DISMANTLE,
            (interaction, self.selected, scrap_all),
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
            interaction,
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

    def refresh_elements(self, disabled: bool = False):
        page_display = f"Page {self.current_page + 1}/{self.page_count}"

        disable_equip = disabled
        disable_dismantle = disabled
        for selected_gear in self.selected:
            if selected_gear.id in [gear.id for gear in self.current_skills]:
                disable_dismantle = True

            if selected_gear.id is None or selected_gear.id < 0:
                # Default Gear
                disable_dismantle = True

        self.clear_items()

        match self.state:
            case SkillViewState.EQUIP:
                for row, equipped_skill in enumerate(self.selected):
                    self.add_item(
                        Dropdown(
                            self.display_items,
                            [equipped_skill],
                            self.state,
                            row=row + 1,
                        )
                    )
                self.add_item(PageButton("<", False, row=0))
                self.add_item(SelectButton(disable_equip, row=0))
                self.add_item(PageButton(">", True, row=0))
                self.add_item(CurrentPageButton(page_display, row=0))
                self.add_item(BackButton(row=0))
            case SkillViewState.MANAGE:
                if len(self.display_items) > 0:
                    self.add_item(
                        Dropdown(
                            self.display_items,
                            self.selected,
                            self.state,
                        )
                    )
                self.add_item(PageButton("<", False))
                self.add_item(SelectButton(disable_equip))
                self.add_item(PageButton(">", True))
                self.add_item(CurrentPageButton(page_display))
                self.add_item(ScrapBalanceButton(self.scrap_balance))
                self.add_item(ScrapSelectedButton(disable_dismantle))
                self.add_item(LockButton(disabled))
                self.add_item(UnlockButton(disabled))
                self.add_item(BackButton())

    async def refresh_ui(
        self,
        skill_inventory: list[Skill] = None,
        scrap_balance: int = None,
        disabled: bool = False,
    ):
        if self.message is None:
            return

        if scrap_balance is not None:
            self.scrap_balance = scrap_balance

        if skill_inventory is not None:
            self.skills = skill_inventory
            self.filter_items()
            self.current_page = min(self.current_page, (self.page_count - 1))

        if self.selected is None or len(self.selected) <= 0:
            disabled = True

        start_offset = SelectSkillHeadEmbed.ITEMS_PER_PAGE * self.current_page
        end_offset = min(
            (start_offset + SelectSkillHeadEmbed.ITEMS_PER_PAGE),
            len(self.filtered_items),
        )
        self.display_items = self.filtered_items[start_offset:end_offset]

        self.refresh_elements(disabled)

        embeds = []
        files = {}
        embeds.append(SelectSkillHeadEmbed(self.member))

        if len(self.display_items) <= 0:
            empty_embed = discord.Embed(
                title="Empty", color=discord.Colour.light_grey()
            )
            self.embed_manager.add_text_bar(
                empty_embed, "", "Seems like there is nothing here."
            )
            empty_embed.set_thumbnail(url=self.controller.bot.user.display_avatar)
            embeds.append(empty_embed)

        for skill in self.display_items:
            equipped = False
            if skill.id in [gear.id for gear in self.current_skills]:
                equipped = True

            skill_data = self.character.get_skill_data(skill)

            embeds.append(
                skill_data.get_embed(equipped=equipped, show_locked_state=True)
            )
            file_path = f"./{skill.base.image_path}{skill.base.image}"
            if file_path not in files:
                file = discord.File(
                    file_path,
                    skill.base.attachment_name,
                )
                files[file_path] = file

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
        index: int,
    ):
        await interaction.response.defer()
        match self.state:
            case SkillViewState.EQUIP:
                self.selected[index] = [
                    skill for skill in self.skills if skill.id in skill_ids
                ][0]
            case SkillViewState.MANAGE:
                self.selected = [
                    skill for skill in self.skills if skill.id in skill_ids
                ]
        await self.refresh_ui()

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class SelectButton(discord.ui.Button):

    def __init__(self, disabled: bool = True, row: int = 4):

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


class ScrapSelectedButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Scrap Selected",
            style=discord.ButtonStyle.red,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.dismantle_skill(interaction)


class ScrapAllButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Scrap All (non locked)",
            style=discord.ButtonStyle.red,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.dismantle_skill(interaction, scrap_all=True)


class LockButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Lock Selected",
            style=discord.ButtonStyle.gray,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.lock_selected(interaction)


class UnlockButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Unlock Selected",
            style=discord.ButtonStyle.gray,
            row=3,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.unlock_selected(interaction)


class BackButton(discord.ui.Button):

    def __init__(self, disabled: bool = False, row: int = 4):
        super().__init__(
            label="Back",
            style=discord.ButtonStyle.gray,
            row=row,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.go_back(interaction)


class Dropdown(discord.ui.Select):

    def __init__(
        self,
        skills: list[Skill],
        equipped: list[Skill],
        state: SkillViewState,
        disabled: bool = False,
        row: int = 0,
        max_values: int = 1,
    ):
        self.row = row
        options = []

        available_skills = skills
        if state == SkillViewState.EQUIP:
            equipped_skill = equipped[0]
            if equipped_skill.id not in [skill.id for skill in skills]:
                available_skills = available_skills + [equipped_skill]

            if equipped_skill.id is None:
                disabled = True
                available_skills = [equipped_skill]

        for item in available_skills:
            name = item.name
            if name is None or name == "":
                name = item.base.slot.value
            elif item.id in equipped or item.id is None:
                name += " [EQUIPPED]"
            elif item.locked:
                name += " [🔒]"

            description = [f"ILVL: {item.level}"]
            description.append(f"PRW: {item.base.scaling}")
            description = " | ".join(description)
            description = (
                (description[:95] + "..") if len(description) > 95 else description
            )
            label = f"[{item.rarity.value}] {name}"

            if item.id is not None and item.id < 0:
                label = item.name
                description = ""

            option = discord.SelectOption(
                label=label,
                description=description,
                value=item.id if item.id is not None else 0,
                default=(item.id in [skill.id for skill in equipped]),
            )
            options.append(option)

        super().__init__(
            placeholder="Select one or more pieces of equipment.",
            min_values=0,
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


class PageButton(discord.ui.Button):

    def __init__(self, label: str, right: bool, disabled: bool = False, row: int = 2):
        self.right = right
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=row, disabled=disabled
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await view.flip_page(interaction, self.right)


class CurrentPageButton(discord.ui.Button):

    def __init__(self, label: str, row: int = 2):
        super().__init__(
            label=label, style=discord.ButtonStyle.grey, row=row, disabled=True
        )


class ScrapBalanceButton(discord.ui.Button):

    def __init__(self, balance: int, row: int = 2):
        self.balance = balance
        super().__init__(
            label=f"⚙️{balance}", style=discord.ButtonStyle.blurple, row=row
        )

    async def callback(self, interaction: discord.Interaction):
        view: SkillSelectView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)
