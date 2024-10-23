import asyncio
import contextlib
import datetime

import discord

from combat.actors import Character
from combat.encounter import EncounterContext
from combat.skills.skill import CharacterSkill
from config import Config
from control.combat.combat_skill_manager import CombatSkillManager
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
        dm_pings_enabled: bool,
    ):
        self.dm_pings_enabled = dm_pings_enabled

        self.__timeout_task = None
        if dm_pings_enabled:
            dm_timeout = datetime.datetime.now() + datetime.timedelta(
                seconds=Config.DM_PING_TIMEOUT
            )
            self.__timeout_task = asyncio.create_task(
                self.__dm_ping_timeout_task(dm_timeout)
            )

        if character.timeout_count == 0:
            timeout = Config.DEFAULT_TIMEOUT
        else:
            timeout = Config.SHORT_TIMEOUT

        super().__init__(timeout=timeout)
        self.controller = controller
        self.character = character
        self.context = context
        self.member_id = character.member.id
        self.blocked = False
        self.done = False

        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
        )

        self.controller_types = [ControllerType.COMBAT]
        self.controller.register_view(self)
        self.skill_data = []

    @classmethod
    async def create(
        cls: "CombatTurnView",
        controller: Controller,
        character: Character,
        context: EncounterContext,
        dm_pings_enabled: bool,
    ):
        view = cls(controller, character, context, dm_pings_enabled)
        for skill in character.skills:
            skill_data = await view.skill_manager.get_skill_data(character, skill)
            view.add_item(SkillButton(skill_data))
            view.skill_data.append(skill_data)

        return view

    async def __dm_ping_timeout_task(self, dm_timeout: datetime.datetime) -> None:
        while True:
            if self.done:
                return

            now = datetime.datetime.now()
            if now >= dm_timeout:
                event = UIEvent(
                    UIEventType.COMBAT_DM_PING,
                    (self.character, self.context),
                    self.id,
                )
                await self.controller.dispatch_ui_event(event)
                return

            sleep = dm_timeout - now

            await asyncio.sleep(sleep.total_seconds())

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.COMBAT_FORCE_USE:
                interaction = event.payload[0]
                slot = event.payload[1]
                with contextlib.suppress(discord.HTTPException):
                    await self.message.delete()
                    self.controller.detach_view(self)
                await self.use_skill(interaction, self.skill_data[slot])

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

        self.done = True

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
