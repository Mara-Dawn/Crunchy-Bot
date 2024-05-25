from enum import Enum

import discord
from combat.actors import Character
from combat.gear.types import GearSlot
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.combat.embed import AttributesHeadEmbed, EquipmentHeadEmbed, SkillsHeadEmbed
from view.view_menu import ViewMenu


class EquipmentViewState(Enum):
    GEAR = 0
    STATS = 1
    SKILLS = 2
    FORGE = 3


class EquipmentView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
        character: Character,
        scrap_balance: int,
    ):
        super().__init__(timeout=None)
        self.controller = controller
        self.character = character
        self.member_id = character.member.id
        self.guild_id = character.member.guild.id
        self.member = interaction.user
        self.blocked = False
        self.state = EquipmentViewState.GEAR
        self.scrap_balance = scrap_balance

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

    def refresh_elements(self):

        gear_button_disabled = False
        stats_button_disabled = False
        skills_button_disabled = False
        forge_button_disabled = False

        self.clear_items()
        match self.state:
            case EquipmentViewState.GEAR:
                gear_button_disabled = True
                self.add_item(SelectWeapon())
                self.add_item(SelectHeadGear())
                self.add_item(SelectBodyArmor())
                self.add_item(SelectLegs())
                self.add_item(SelectAccessory())
            case EquipmentViewState.STATS:
                stats_button_disabled = True
            case EquipmentViewState.SKILLS:
                skills_button_disabled = True
            case EquipmentViewState.FORGE:
                forge_button_disabled = True

        self.add_item(GearButton(gear_button_disabled))
        self.add_item(StatsButton(stats_button_disabled))
        self.add_item(SkillsButton(skills_button_disabled))
        self.add_item(ForgeButton(forge_button_disabled))
        self.add_item(ScrapBalanceButton(self.scrap_balance))

    async def refresh_ui(self, character: Character = None, scrap_balance: int = None):
        if self.message is None:
            return

        if scrap_balance is not None:
            self.scrap_balance = scrap_balance

        if character is not None:
            self.character = character

        self.refresh_elements()
        embeds = []
        files = []
        match self.state:
            case EquipmentViewState.GEAR:
                embeds.append(EquipmentHeadEmbed(self.member))
                embeds.append(
                    self.character.equipment.weapon.get_embed(title="Weapon Slot")
                )
                files.append(
                    discord.File(
                        f"./{self.character.equipment.weapon.base.image_path}{self.character.equipment.weapon.base.image}",
                        self.character.equipment.weapon.base.image,
                    )
                )
                embeds.append(
                    self.character.equipment.head_gear.get_embed(title="Head Gear Slot")
                )
                files.append(
                    discord.File(
                        f"./{self.character.equipment.head_gear.base.image_path}{self.character.equipment.head_gear.base.image}",
                        self.character.equipment.head_gear.base.image,
                    )
                )
                embeds.append(
                    self.character.equipment.body_gear.get_embed(
                        title="Body Armor Slot"
                    )
                )
                files.append(
                    discord.File(
                        f"./{self.character.equipment.body_gear.base.image_path}{self.character.equipment.body_gear.base.image}",
                        self.character.equipment.body_gear.base.image,
                    )
                )
                embeds.append(
                    self.character.equipment.leg_gear.get_embed(title="Leg Gear Slot")
                )
                files.append(
                    discord.File(
                        f"./{self.character.equipment.leg_gear.base.image_path}{self.character.equipment.leg_gear.base.image}",
                        self.character.equipment.leg_gear.base.image,
                    )
                )
                embeds.append(
                    self.character.equipment.accessory_1.get_embed(
                        title="Accessory Slot 1"
                    )
                )
                files.append(
                    discord.File(
                        f"./{self.character.equipment.accessory_1.base.image_path}{self.character.equipment.accessory_1.base.image}",
                        self.character.equipment.accessory_1.base.image,
                    )
                )
                embeds.append(
                    self.character.equipment.accessory_2.get_embed(
                        title="Accessory Slot 2"
                    )
                )
                if (
                    self.character.equipment.accessory_1.base.image
                    != self.character.equipment.accessory_2.base.image
                ):
                    files.append(
                        discord.File(
                            f"./{self.character.equipment.accessory_2.base.image_path}{self.character.equipment.accessory_2.base.image}",
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

    async def change_gear(self, interaction: discord.Interaction, slot: GearSlot):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.GEAR_OPEN_SECELT,
            (interaction, slot),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)


class GearButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        color = discord.ButtonStyle.grey
        if disabled:
            color = discord.ButtonStyle.red

        super().__init__(label="Gear", style=color, disabled=disabled, row=0)

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.set_state(EquipmentViewState.GEAR, interaction)


class StatsButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        color = discord.ButtonStyle.grey
        if disabled:
            color = discord.ButtonStyle.red

        super().__init__(
            label="Attributes",
            style=color,
            disabled=disabled,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.set_state(EquipmentViewState.STATS, interaction)


class SkillsButton(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        color = discord.ButtonStyle.grey
        if disabled:
            color = discord.ButtonStyle.red

        super().__init__(
            label="Skills",
            style=color,
            disabled=disabled,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.set_state(EquipmentViewState.SKILLS, interaction)


class SelectWeapon(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Change Weapon",
            style=discord.ButtonStyle.green,
            disabled=disabled,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.change_gear(interaction, GearSlot.WEAPON)


class SelectHeadGear(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Change Headgear",
            style=discord.ButtonStyle.green,
            disabled=disabled,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.change_gear(interaction, GearSlot.HEAD)


class SelectBodyArmor(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Change Body",
            style=discord.ButtonStyle.green,
            disabled=disabled,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.change_gear(interaction, GearSlot.BODY)


class SelectLegs(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Change Bottoms",
            style=discord.ButtonStyle.green,
            disabled=disabled,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.change_gear(interaction, GearSlot.LEGS)


class SelectAccessory(discord.ui.Button):

    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Change Accessory",
            style=discord.ButtonStyle.green,
            disabled=disabled,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view
        await view.change_gear(interaction, GearSlot.ACCESSORY)


class ForgeButton(discord.ui.Button):

    def __init__(self, disabled: bool = True):
        color = discord.ButtonStyle.grey
        if disabled:
            color = discord.ButtonStyle.red

        disabled = True

        super().__init__(
            label="Bean Forge",
            style=color,
            row=0,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)


class ScrapBalanceButton(discord.ui.Button):

    def __init__(self, balance: int):
        self.balance = balance
        super().__init__(label=f"⚙️{balance}", style=discord.ButtonStyle.blurple, row=0)

    async def callback(self, interaction: discord.Interaction):
        view: EquipmentView = self.view

        if await view.interaction_check(interaction):
            await interaction.response.defer(ephemeral=True)
