import datetime
import random

import discord

from combat.actors import Actor, Character
from combat.encounter import EncounterContext, TurnData
from combat.engine.states.state import State
from combat.engine.types import StateType
from combat.skills.skill import Skill
from combat.skills.types import (
    SkillEffect,
    SkillInstance,
    SkillType,
    StatusEffectApplication,
)
from config import Config
from control.controller import Controller
from control.types import UserSettingsToggle, UserSettingType
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.types import CombatEventType, EncounterEventType, EventType
from view.combat.combat_turn_view import CombatTurnView


class PlayerTurn(State):
    def __init__(self, controller: Controller, context: EncounterContext):
        super().__init__(controller, context)
        self.state_type: StateType = StateType.PLAYER_TURN
        self.next_state: StateType = StateType.TURN_END

    async def startup(self):
        actor = self.context.current_actor
        embeds = await self.embed_manager.get_character_turn_embeds(self.context)

        dm_ping_enabled = (
            await self.user_settings_manager.get(
                actor.id, self.context.encounter.guild_id, UserSettingType.DM_PING
            )
            == UserSettingsToggle.ENABLED
        )

        view = await CombatTurnView.create(
            self.controller, actor, self.context, dm_ping_enabled
        )

        message = await self.discord.send_message(
            self.context.thread,
            content=f"<@{actor.id}>",
            embeds=embeds,
            view=view,
        )
        view.set_message(message)

    async def handle(self, event: BotEvent) -> bool:
        update = False
        if not event.synchronized:
            return update
        match event.type:
            case EventType.ENCOUNTER:
                encounter_event: EncounterEvent = event
                if encounter_event.encounter_id != self.context.encounter.id:
                    return update

                match encounter_event.encounter_event_type:
                    case EncounterEventType.MEMBER_ENGAGE:
                        await self.common.add_member_to_encounter(
                            encounter_event.member_id, self.context
                        )
                    case EncounterEventType.MEMBER_REQUEST_JOIN:
                        await self.common.add_member_join_request(
                            encounter_event.member_id, self.context
                        )
                    case EncounterEventType.MEMBER_REVIVE:
                        actor = self.context.get_actor_by_id(event.member_id)
                        if actor in self.context.defeated_combatants:
                            self.context.defeated_combatants.remove(actor)
                        if actor not in self.context.active_combatants:
                            self.context.active_combatants.append(actor)
                        update = True
                    case EncounterEventType.ENEMY_PHASE_CHANGE:
                        self.context.reset_initiative = True
                    case EncounterEventType.MEMBER_OUT:
                        actor = self.context.get_actor_by_id(
                            encounter_event.member_id,
                        )
                        self.context.active_combatants.remove(actor)
                        update = True
                    case EncounterEventType.END:
                        self.next_state = StateType.POST_ENCOUNTER
                        self.done = True
                        await self.common.force_end(self.context)
                        update = True

            case EventType.COMBAT:
                combat_event: CombatEvent = event
                if combat_event.encounter_id != self.context.encounter.id:
                    return update
                if combat_event.member_id != self.context.current_actor.id:
                    return update

                match combat_event.combat_event_type:
                    case CombatEventType.MEMBER_TURN:
                        update = True
                    case CombatEventType.MEMBER_TURN_STEP:
                        await self.skill_manager.trigger_special_skill_effects(event)
                    case CombatEventType.MEMBER_TURN_ACTION:
                        await self.combatant_turn(
                            combat_event.skill_type, combat_event.skill_id
                        )
                    case CombatEventType.MEMBER_TURN_SKIP:
                        await self.combatant_timeout()
                        update = True

        return update

    async def update(self):
        await self.discord.refresh_round_overview(self.context)
        enemy_embed = await self.embed_manager.get_combat_embed(self.context)
        message = await self.discord.get_previous_enemy_info(self.context.thread)
        if message is not None:
            await self.discord.edit_message(message, embed=enemy_embed)

    async def combatant_turn(self, skill_type: SkillType, skill_id: int):
        character = self.context.current_actor
        context = self.context

        skill = await self.database.get_skill_by_id(skill_id)

        if SkillType.is_weapon_skill(skill_type):
            equipment = await self.database.get_user_equipment(
                character.member.guild.id, character.id
            )
            weapon_skills = equipment.weapon.base.skills

            for type in weapon_skills:
                if type == skill_type:
                    skill = await self.factory.get_weapon_skill(
                        skill_type, equipment.weapon.rarity, equipment.weapon.level
                    )
                    break

        skill_data = await self.skill_manager.get_character_skill_data(character, skill)

        target = await self.skill_manager.get_character_default_target(
            character, skill, context
        )

        if target is not None:
            if skill_data.skill.base_skill.aoe:
                # assumes party targeted
                damage_data, post_embed_data = await self.calculate_character_aoe_skill(
                    context,
                    skill_data.skill,
                    character,
                    context.active_combatants,
                )
            else:
                damage_data, post_embed_data = await self.calculate_character_skill(
                    context, skill_data.skill, character, target
                )

            turn = TurnData(
                actor=character,
                skill=skill_data.skill,
                damage_data=damage_data,
                post_embed_data=post_embed_data,
            )
        else:
            turn = TurnData(
                actor=character,
                skill=skill_data.skill,
                damage_data=[],
                post_embed_data={"No Target": "The Skill had no effect."},
            )

        await self.discord.append_embed_generator_to_round(
            context, self.embed_manager.handle_actor_turn_embed(turn, context)
        )

        if turn.post_embed_data is not None:
            await self.discord.append_embeds_to_round(
                context, character, turn.post_embed_data
            )

        for target, damage_instance, _ in turn.damage_data:
            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, turn.skill, damage_instance.scaled_value
            )
            display_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, turn.skill, damage_instance.value
            )
            outcome = (
                await self.status_effect_manager.handle_post_attack_status_effects(
                    context,
                    character,
                    target,
                    skill_data.skill,
                    damage_instance,
                )
            )
            if outcome.embed_data is not None:
                await self.discord.append_embeds_to_round(
                    context, character, outcome.embed_data
                )

            status_effect_damage = display_damage
            for skill_status_effect in turn.skill.base_skill.status_effects:
                application_value = None
                match skill_status_effect.application:
                    case StatusEffectApplication.ATTACK_VALUE:
                        if skill_data.skill.base_skill.skill_effect == SkillEffect.BUFF:
                            application_value = damage_instance.skill_base
                        else:
                            application_value = status_effect_damage
                    case StatusEffectApplication.MANUAL_VALUE:
                        application_value = skill_status_effect.application_value
                    case StatusEffectApplication.DEFAULT:
                        if status_effect_damage <= 0:
                            application_value = status_effect_damage

                status_effect_target = target
                if skill_status_effect.self_target:
                    status_effect_target = character

                if random.random() < skill_status_effect.application_chance:
                    await self.status_effect_manager.apply_status(
                        context,
                        character,
                        status_effect_target,
                        skill_status_effect.status_effect_type,
                        skill_status_effect.stacks,
                        application_value,
                    )

            event = CombatEvent(
                datetime.datetime.now(),
                context.encounter.guild_id,
                context.encounter.id,
                character.id,
                target.id,
                skill_data.skill.base_skill.skill_type,
                total_damage,
                display_damage,
                skill_data.skill.id,
                CombatEventType.MEMBER_TURN_STEP,
            )
            await self.controller.dispatch_event(event)

        self.done = True
        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            character.id,
            None,
            skill_data.skill.base_skill.skill_type,
            None,
            None,
            skill_data.skill.id,
            CombatEventType.MEMBER_TURN,
        )
        await self.controller.dispatch_event(event)

    async def calculate_character_aoe_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        source: Character,
        available_targets: list[Actor],
    ) -> tuple[list[tuple[Actor, SkillInstance, float], discord.Embed]]:
        damage_data = []
        embed_data = {}
        outcome = await self.status_effect_manager.handle_attack_status_effects(
            context, source, skill
        )
        if outcome.embed_data is not None:
            embed_data = embed_data | outcome.embed_data

        for target in available_targets:
            instances = await self.skill_manager.get_skill_effect(
                source, skill, combatant_count=context.combat_scale
            )
            instance = instances[0]
            instance.apply_effect_outcome(outcome)

            current_hp = target.current_hp

            outcome_on_dmg = (
                await self.status_effect_manager.handle_on_damage_taken_status_effects(
                    context,
                    target,
                    skill,
                )
            )

            if outcome_on_dmg.embed_data is not None:
                embed_data = embed_data | outcome_on_dmg.embed_data

            instance.apply_effect_outcome(outcome_on_dmg)

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )

            if skill.base_skill.skill_effect == SkillEffect.HEALING:
                total_damage *= -1

            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)

            damage_data.append((target, instance, new_target_hp))
        return damage_data, embed_data

    async def calculate_character_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        source: Character,
        target: Actor,
    ) -> tuple[list[tuple[Actor, SkillInstance, float], list[discord.Embed]]]:
        skill_instances = await self.skill_manager.get_skill_effect(
            source, skill, combatant_count=context.combat_scale
        )

        skill_value_data = []
        hp_cache = {}
        embed_data = {}

        for instance in skill_instances:
            outcome = await self.status_effect_manager.handle_attack_status_effects(
                context,
                source,
                skill,
            )
            if outcome.embed_data is not None:
                embed_data = embed_data | outcome.embed_data
            instance.apply_effect_outcome(outcome)

            outcome = (
                await self.status_effect_manager.handle_on_damage_taken_status_effects(
                    context,
                    target,
                    skill,
                )
            )

            if outcome.embed_data is not None:
                embed_data = embed_data | outcome.embed_data
            instance.apply_effect_outcome(outcome)

            total_skill_value = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )

            target_id = target.id
            if target_id is None:
                target_id = -1

            if target_id not in hp_cache:
                hp_cache[target_id] = target.current_hp

            current_hp = hp_cache[target_id]

            if skill.base_skill.skill_effect != SkillEffect.HEALING:
                total_skill_value *= -1

            new_target_hp = min(max(0, current_hp + total_skill_value), target.max_hp)
            hp_cache[target_id] = new_target_hp

            skill_value_data.append((target, instance, new_target_hp))

        return skill_value_data, embed_data

    async def combatant_timeout(self):
        character = self.context.current_actor
        context = self.context

        timeout_count = character.timeout_count
        character.timeout_count += 1

        message = (
            f"{character.name} was inactive for too long, their turn will be skipped."
        )
        timeout_count += 1

        jail_time = Config.TIMEOUT_JAIL_TIME
        jail_message = (
            f"<@{character.member.id}> was jailed for missing their turn in combat."
        )

        if (
            timeout_count >= Config.TIMEOUT_COUNT_LIMIT
            and not context.opponent.enemy.is_boss
        ):
            event = EncounterEvent(
                datetime.datetime.now(),
                context.encounter.guild_id,
                context.encounter.id,
                character.id,
                EncounterEventType.MEMBER_OUT,
            )
            await self.controller.dispatch_event(event)
            message += f" They reached {Config.TIMEOUT_COUNT_LIMIT} total timeouts and will be excluded from the fight."
            jail_time += Config.KICK_JAIL_TIME
            jail_message = f"<@{character.member.id}> was jailed for repeatedly missing their turn in combat, leading to them getting kicked."

        embed = self.embed_manager.get_turn_skip_embed(character, message, context)
        await self.discord.append_embed_to_round(context, embed)
        await self.jail_manager.jail_or_extend_user(
            context.encounter.guild_id,
            self.bot.user.id,
            character.member,
            jail_time,
            jail_message,
        )
        self.done = True
