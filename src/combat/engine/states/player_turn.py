import asyncio
import datetime
import random

from combat.actors import Actor, Character
from combat.effects.effect import EmbedDataCollection
from combat.encounter import EncounterContext, TurnDamageData, TurnData
from combat.engine.states.state import State
from combat.engine.types import StateType
from combat.skills.skill import Skill
from combat.skills.types import (
    SkillEffect,
    SkillType,
)
from combat.status_effects.types import StatusEffectApplication
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
                        update = True
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

        post_turn_embed_data = EmbedDataCollection()

        if turn.post_embed_data is not None:
            post_turn_embed_data.extend(turn.post_embed_data)

        for turn_damage_data in turn.damage_data:
            target = turn_damage_data.target
            damage_instance = turn_damage_data.instance

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, turn.skill, damage_instance.scaled_value
            )
            display_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, turn.skill, damage_instance.value
            )
            outcome = await self.effect_manager.on_post_attack(
                context,
                character,
                target,
                skill_data.skill,
                damage_instance,
            )
            if outcome.applied_effects is not None:
                turn_damage_data.applied_status_effects.extend(outcome.applied_effects)
            if outcome.embed_data is not None:
                post_turn_embed_data.extend(outcome.embed_data)

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
                    case StatusEffectApplication.RAW_ATTACK_VALUE:
                        application_value = (
                            await self.actor_manager.get_skill_damage_after_defense(
                                target, turn.skill, damage_instance.raw_value
                            )
                        )

                status_effect_target = target
                if skill_status_effect.self_target:
                    status_effect_target = character

                application_chance = skill_status_effect.application_chance
                if damage_instance.is_crit:
                    application_chance = min(1, application_chance * 2)

                if random.random() < application_chance:
                    outcome = await self.effect_manager.apply_status(
                        context,
                        character,
                        status_effect_target,
                        skill_status_effect.status_effect_type,
                        skill_status_effect.stacks,
                        application_value,
                    )

                    if outcome.embed_data is not None:
                        post_turn_embed_data.extend(outcome.embed_data)

                    if outcome.applied_effects is not None:
                        turn_damage_data.applied_status_effects.extend(
                            outcome.applied_effects
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

        await self.embed_manager.apply_attack_data_to_embed(
            self.context.current_turn_embed, turn
        )

        await self.discord.update_current_turn_embed_by_generator(
            self.context,
            self.embed_manager.get_actor_turn_embed_data(turn, self.context),
        )

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

        outcome = await self.effect_manager.on_post_skill(
            context,
            character,
            target,
            skill_data.skill,
        )
        if outcome.embed_data is not None:
            post_turn_embed_data.extend(outcome.embed_data)

        if post_turn_embed_data.length > 0:
            await asyncio.sleep(0.5)
            await self.discord.update_current_turn_embed(
                self.context, post_turn_embed_data
            )

        self.done = True

    async def calculate_character_aoe_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        source: Character,
        available_targets: list[Actor],
    ) -> tuple[list[TurnDamageData], EmbedDataCollection]:
        skill_value_data = []
        embed_data = EmbedDataCollection()

        for target in available_targets:
            outcome = await self.effect_manager.on_attack(
                context, source, target, skill
            )

            if outcome.embed_data is not None:
                embed_data.extend(outcome.embed_data)

            instances = await self.skill_manager.get_skill_effect(
                source, skill, combatant_count=context.combat_scale
            )
            instance = instances[0]
            outcome.apply_to_instance(instance)

            current_hp = target.current_hp

            if instance.value > 0:
                outcome_on_dmg = await self.effect_manager.on_damage_taken(
                    context,
                    target,
                    skill,
                )

                if outcome_on_dmg.embed_data is not None:
                    embed_data.extend(outcome.embed_data)

                outcome.apply_to_instance(instance)

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )

            if skill.base_skill.skill_effect == SkillEffect.HEALING:
                total_damage *= -1

            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)

            damage_data = TurnDamageData(target, instance, new_target_hp)
            skill_value_data.append(damage_data)

        return skill_value_data, embed_data

    async def calculate_character_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        source: Character,
        target: Actor,
    ) -> tuple[list[TurnDamageData], EmbedDataCollection]:
        skill_instances = await self.skill_manager.get_skill_effect(
            source, skill, combatant_count=context.combat_scale
        )

        skill_value_data = []
        hp_cache = {}
        embed_data = EmbedDataCollection()

        for instance in skill_instances:
            outcome = await self.effect_manager.on_attack(
                context,
                source,
                target,
                skill,
            )
            if outcome.embed_data is not None:
                embed_data.extend(outcome.embed_data)
            outcome.apply_to_instance(instance)

            if instance.value > 0:
                outcome = await self.effect_manager.on_damage_taken(
                    context,
                    target,
                    skill,
                )

                if outcome.embed_data is not None:
                    embed_data.extend(outcome.embed_data)

                outcome.apply_to_instance(instance)

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

            damage_data = TurnDamageData(target, instance, new_target_hp)
            skill_value_data.append(damage_data)

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

        self.embed_manager.add_turn_skip_to_embed(
            message, character, context.current_turn_embed
        )
        await self.discord.update_current_turn_embed(self.context)
        await self.jail_manager.jail_or_extend_user(
            context.encounter.guild_id,
            self.bot.user.id,
            character.member,
            jail_time,
            jail_message,
        )
        self.done = True
