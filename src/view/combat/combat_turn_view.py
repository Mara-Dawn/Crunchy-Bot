import contextlib

import discord
from combat.actors import Character
from combat.encounter import EncounterContext
from combat.skills.skill import CharacterSkill
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class CombatTurnView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        character: Character,
        context: EncounterContext,
    ):
        timeout = context.get_turn_timeout(character.id)
        super().__init__(timeout=timeout)
        self.controller = controller
        self.character = character
        self.context = context
        self.member_id = character.member.id
        self.blocked = False

        for skill in character.skills:
            skill_data = character.get_skill_data(skill)
            self.add_item(SkillButton(skill_data))

        self.controller_type = ControllerType.COMBAT
        self.controller.register_view(self)

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return

        match event.type:
            case UIEventType.STOP_INTERACTIONS:
                self.blocked = True
            case UIEventType.RESUME_INTERACTIONS:
                self.blocked = False

    async def use_skill(
        self, interaction: discord.Interaction, skill_data: CharacterSkill
    ):
        await interaction.response.defer()

        if self.blocked:
            return

        event = UIEvent(
            UIEventType.COMBAT_USE_SKILL,
            (interaction, skill_data, self.character, self.context),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.delete()

            event = UIEvent(
                UIEventType.COMBAT_TIMEOUT,
                (self.character, self.context),
            )
            await self.controller.dispatch_ui_event(event)

            self.controller.detach_view(self)


class SkillButton(discord.ui.Button):

    def __init__(self, skill_data: CharacterSkill):
        self.skill_data = skill_data

        disabled = False
        if skill_data.on_cooldown():
            disabled = True

        if skill_data.stacks_left() is not None and skill_data.stacks_left() <= 0:
            disabled = True

        super().__init__(
            label=skill_data.skill.name,
            style=discord.ButtonStyle.green,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: CombatTurnView = self.view
        await view.use_skill(interaction, self.skill_data)
