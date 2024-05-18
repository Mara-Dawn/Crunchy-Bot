import discord
from combat.actors import Character
from combat.encounter import EncounterContext
from combat.skills.skill import Skill
from control.controller import Controller
from control.types import ControllerType
from events.types import UIEventType
from events.ui_event import UIEvent
from view.view_menu import ViewMenu


class CombatTurnView(ViewMenu):

    def __init__(
        self, controller: Controller, character: Character, context: EncounterContext
    ):
        super().__init__(timeout=None)
        self.controller = controller
        self.character = character
        self.context = context
        self.member_id = character.member.id
        self.blocked = False

        for skill in character.skills:
            self.add_item(SkillButton(skill))

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

    async def use_skill(self, interaction: discord.Interaction, skill: Skill):
        await interaction.response.defer()

        if self.blocked:
            return

        event = UIEvent(
            UIEventType.COMBAT_USE_SKILL,
            (interaction, skill, self.character, self.context),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)


class SkillButton(discord.ui.Button):

    def __init__(self, skill: Skill):
        self.skill = skill
        super().__init__(label=skill.name, style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view: CombatTurnView = self.view
        await view.use_skill(interaction, self.skill)
