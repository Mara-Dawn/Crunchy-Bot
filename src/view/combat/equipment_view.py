from enum import Enum

import discord
from combat.actors import Character
from combat.gear.gear import GearBase
from control.controller import Controller
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.embed import AttributesHeadEmbed, EquipmentHeadEmbed, SkillsHeadEmbed
from view.view_menu import ViewMenu


class EquipmentViewState(Enum):
    GEAR = 0
    STATS = 1
    SKILLS = 2


class EquipmentView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        character: Character,
    ):
        super().__init__(timeout=None)
        self.controller = controller
        self.character = character
        self.member_id = character.member.id
        self.member = interaction.user
        self.blocked = False
        self.state = EquipmentViewState.GEAR

        # self.controller_type = ControllerType.EQUIPMENT
        # self.controller.register_view(self)
        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.STOP_INTERACTIONS:
                self.blocked = True
            case UIEventType.RESUME_INTERACTIONS:
                self.blocked = False

    def refresh_elements(self):

        gear_button_disabled = False
        stats_button_disabled = False
        skills_button_disabled = False

        match self.state:
            case EquipmentViewState.GEAR:
                gear_button_disabled = True
            case EquipmentViewState.STATS:
                stats_button_disabled = True
            case EquipmentViewState.SKILLS:
                skills_button_disabled = True

        self.clear_items()
        self.add_item(GearButton(gear_button_disabled))
        self.add_item(StatsButton(stats_button_disabled))
        self.add_item(SkillsButton(skills_button_disabled))

    async def refresh_ui(self, character: Character = None):
        if self.message is None:
            return

        if character is not None:
            self.character = character

        self.refresh_elements()
        embeds = []
        files = []
        match self.state:
            case EquipmentViewState.GEAR:
                embeds.append(EquipmentHeadEmbed(self.member))
                embeds.append(self.character.equipment.weapon.get_embed())
                files.append(
                    discord.File(
                        f"./{GearBase.DEFAULT_IMAGE_PATH}{self.character.equipment.weapon.base.image}",
                        self.character.equipment.weapon.base.image,
                    )
                )
                embeds.append(self.character.equipment.head_gear.get_embed())
                files.append(
                    discord.File(
                        f"./{GearBase.DEFAULT_IMAGE_PATH}{self.character.equipment.head_gear.base.image}",
                        self.character.equipment.head_gear.base.image,
                    )
                )
                embeds.append(self.character.equipment.body_gear.get_embed())
                files.append(
                    discord.File(
                        f"./{GearBase.DEFAULT_IMAGE_PATH}{self.character.equipment.body_gear.base.image}",
                        self.character.equipment.body_gear.base.image,
                    )
                )
                embeds.append(self.character.equipment.leg_gear.get_embed())
                files.append(
                    discord.File(
                        f"./{GearBase.DEFAULT_IMAGE_PATH}{self.character.equipment.leg_gear.base.image}",
                        self.character.equipment.leg_gear.base.image,
                    )
                )
                embeds.append(self.character.equipment.accessory_1.get_embed())
                files.append(
                    discord.File(
                        f"./{GearBase.DEFAULT_IMAGE_PATH}{self.character.equipment.accessory_1.base.image}",
                        self.character.equipment.accessory_1.base.image,
                    )
                )
                embeds.append(self.character.equipment.accessory_2.get_embed())
                if (
                    self.character.equipment.accessory_1.base.image
                    != self.character.equipment.accessory_2.base.image
                ):
                    files.append(
                        discord.File(
                            f"./{GearBase.DEFAULT_IMAGE_PATH}{self.character.equipment.accessory_2.base.image}",
                            self.character.equipment.accessory_2.base.image,
                        )
                    )
            case EquipmentViewState.STATS:
                embeds.append(AttributesHeadEmbed(self.member))
                title = f"{self.member.display_name}'s Attributes"
                embeds.append(self.character.equipment.get_embed(title=title))
            case EquipmentViewState.SKILLS:
                embed = SkillsHeadEmbed(self.member)
                for skill in self.character.skills:
                    self.character.get_skill_data(skill).add_to_embed(
                        embed, show_data=True
                    )
                embeds.append(embed)

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


class GearButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):

        super().__init__(
            label="Gear", style=discord.ButtonStyle.green, disabled=disabled, row=0
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.set_state(EquipmentViewState.GEAR, interaction)


class StatsButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):

        super().__init__(
            label="Attributes",
            style=discord.ButtonStyle.green,
            disabled=disabled,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.set_state(EquipmentViewState.STATS, interaction)


class SkillsButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):

        super().__init__(
            label="Skills",
            style=discord.ButtonStyle.green,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.set_state(EquipmentViewState.SKILLS, interaction)
