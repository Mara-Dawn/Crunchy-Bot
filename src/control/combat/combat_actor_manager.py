import datetime
import random

import discord
from discord.ext import commands

from combat.actors import Actor, Character, Opponent
from combat.enchantments.enchantment import Enchantment
from combat.encounter import Encounter, EncounterContext
from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.gear.types import CharacterAttribute, GearModifierType
from combat.skills.skill import Skill
from combat.skills.types import SkillEffect, SkillType
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.types import StatusEffectType
from config import Config
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.imgur_manager import ImgurManager
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.status_effect_event import StatusEffectEvent
from events.types import CombatEventType, EncounterEventType, EventType


class CombatActorManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.imgur_manager: ImgurManager = self.controller.get_service(ImgurManager)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.log_name = "Combat Skills"

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                if not event.synchronized:
                    return
                encounter_event: EncounterEvent = event
                match encounter_event.encounter_event_type:
                    case EncounterEventType.MEMBER_ENGAGE:
                        await self.initialize_actor(
                            encounter_event.member_id,
                            encounter_event.guild_id,
                            encounter_event.encounter_id,
                        )

    async def get_actor_current_hp(
        self, actor: Actor, combat_events: list[CombatEvent]
    ):
        health = actor.max_hp

        for event in reversed(combat_events):
            if event.target_id != actor.id:
                continue
            health += await self.get_event_health_delta(event)
            health = max(0, min(health, actor.max_hp))

        return int(health)

    async def get_event_health_delta(self, event: CombatEvent) -> int:
        if event.skill_type is None:
            return 0
        if event.combat_event_type in [
            CombatEventType.ENCHANTMENT_EFFECT,
            CombatEventType.STATUS_EFFECT,
        ]:
            return 0
        if event.combat_event_type == CombatEventType.STATUS_EFFECT_OUTCOME:
            status_effect = await self.factory.get_status_effect(event.skill_type)
            skill_effect = status_effect.skill_effect
        elif event.combat_event_type == CombatEventType.ENCHANTMENT_EFFECT_OUTCOME:
            enchantment = await self.database.get_enchantment_by_id(event.skill_id)
            skill_effect = enchantment.base_enchantment.skill_effect
        else:
            base_skill = await self.factory.get_base_skill(event.skill_type)
            skill_effect = base_skill.skill_effect

        health = 0
        match skill_effect:
            case SkillEffect.BUFF | SkillEffect.NOTHING:
                pass
            case (
                SkillEffect.PHYSICAL_DAMAGE
                | SkillEffect.MAGICAL_DAMAGE
                | SkillEffect.NEUTRAL_DAMAGE
                | SkillEffect.EFFECT_DAMAGE
            ):
                health = -event.skill_value
            case SkillEffect.HEALING:
                health = event.skill_value
        return health

    async def initialize_actor(
        self,
        member_id: int,
        guild_id: int,
        encounter_id: int,
    ):
        equipment = await self.database.get_user_equipment(guild_id, member_id)

        if equipment.gear_modifiers[GearModifierType.EVASION] > 0:
            event = StatusEffectEvent(
                datetime.datetime.now(),
                guild_id,
                encounter_id,
                member_id,
                member_id,
                StatusEffectType.EVASIVE,
                1,
                equipment.gear_modifiers[GearModifierType.EVASION],
            )
            await self.controller.dispatch_event(event)

    async def get_active_status_effects(
        self,
        id: int,
        status_effects: dict[int, list[StatusEffectEvent]],
        combat_events: list[CombatEvent],
    ) -> list[ActiveStatusEffect]:
        active_status_effects: dict[StatusEffectType, list[ActiveStatusEffect]] = {}
        active_status_effects = []

        if id not in status_effects:
            return active_status_effects

        actor_status_effects = status_effects[id]
        stacks = {event.id: event.stacks for event in actor_status_effects}

        for combat_event in combat_events:
            if combat_event.combat_event_type != CombatEventType.STATUS_EFFECT:
                continue

            status_id = combat_event.skill_id
            if status_id not in stacks:
                continue

            stacks[status_id] += combat_event.skill_value

        for event in actor_status_effects:
            status_effect = await self.factory.get_status_effect(event.status_type)
            active_status_effect = ActiveStatusEffect(
                status_effect, event, stacks[event.id]
            )
            active_status_effects.append(active_status_effect)

        return active_status_effects

    async def get_opponent(
        self,
        enemy: Enemy,
        encounter: Encounter,
        encounter_events: list[EncounterEvent],
        combat_events: list[CombatEvent],
        status_effects: dict[int, list[StatusEffectEvent]],
    ) -> Opponent:
        enemy_level = encounter.enemy_level
        max_hp = encounter.max_hp
        defeated = False
        encounter_id = None
        id = -1
        phase = 1

        defeated = False
        new_round = False
        force_skip = False
        for event in encounter_events:
            if encounter_id is None:
                encounter_id = event.encounter_id
            match event.encounter_event_type:
                case EncounterEventType.ENEMY_PHASE_CHANGE:
                    phase += 1
                case EncounterEventType.ENEMY_DEFEAT:
                    defeated = True
                case EncounterEventType.NEW_ROUND:
                    new_round = True
                case EncounterEventType.FORCE_SKIP:
                    if event.member_id < 0 and not new_round:
                        force_skip = True

        if phase > 1:
            enemy_type = enemy.phases[phase - 2]
            new_enemy = await self.factory.get_enemy(enemy_type)
            max_hp = int(max_hp * new_enemy.health / enemy.health)
            enemy = new_enemy
            id -= phase + 10

        skills = []
        for skill_type in enemy.skill_types:
            skill = await self.factory.get_enemy_skill(skill_type)
            skills.append(skill)

        skill_cooldowns = self.get_skill_cooldowns(id, skills, combat_events)
        skill_stacks_used = await self.database.get_opponent_skill_stacks_used(
            encounter_id
        )
        active_status_effects = await self.get_active_status_effects(
            id, status_effects, combat_events
        )

        image_url = None
        additional_info = None
        image = await self.imgur_manager.get_random_encounter_image(encounter)
        if image is not None:
            image_url = image.link
            additional_info = image.description

        opponent = Opponent(
            id=id,
            enemy=enemy,
            level=enemy_level,
            max_hp=max_hp,
            skills=skills,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            status_effects=active_status_effects,
            defeated=defeated,
            force_skip=force_skip,
            image_url=image_url,
            additional_info=additional_info,
        )

        opponent.current_hp = await self.get_actor_current_hp(opponent, combat_events)
        return opponent

    async def get_character(
        self,
        member: discord.Member,
        encounter_events: list[EncounterEvent] = None,
        combat_events: list[CombatEvent] = None,
        status_effects: dict[int, StatusEffectEvent] = None,
    ) -> Character:
        if encounter_events is None:
            encounter_events = []

        if combat_events is None:
            combat_events = []

        if status_effects is None:
            status_effects = {}

        defeated = False
        revived = False
        leaving = False
        is_out = False
        new_round = False
        force_skip = False
        ready = None
        encounter_start = True
        for event in encounter_events:
            match event.encounter_event_type:
                case EncounterEventType.NEW_ROUND:
                    new_round = True
                    encounter_start = False
                    if ready is None:
                        ready = True
            if event.member_id == member.id:
                match event.encounter_event_type:
                    case EncounterEventType.MEMBER_ENGAGE:
                        if ready is None:
                            ready = False
                    case EncounterEventType.MEMBER_DEFEAT:
                        if not revived:
                            defeated = True
                    case EncounterEventType.MEMBER_REVIVE:
                        revived = True
                    case EncounterEventType.MEMBER_LEAVING:
                        leaving = True
                    case EncounterEventType.MEMBER_OUT:
                        is_out = True
                    case EncounterEventType.FORCE_SKIP:
                        if not new_round:
                            force_skip = True

        if ready is None:
            ready = False
        ready = encounter_start or ready

        if is_out:
            leaving = False

        if is_out or leaving or defeated:
            force_skip = False

        equipment = await self.database.get_user_equipment(member.guild.id, member.id)

        weapon_skills = equipment.weapon.base.skills

        skill_slots = {}

        for slot, skill_type in enumerate(weapon_skills):
            skill = await self.factory.get_weapon_skill(
                skill_type, equipment.weapon.rarity, equipment.weapon.level
            )
            skill_slots[slot] = skill

        equipped_skills = await self.database.get_user_equipped_skills(
            member.guild.id, member.id
        )

        for index in range(4):
            if index not in skill_slots:
                skill_slots[index] = equipped_skills[index]

        skills = [skill for skill in skill_slots.values() if skill is not None]

        enchantments = equipment.enchantments

        skill_cooldowns = self.get_skill_cooldowns(member.id, skills, combat_events)

        enchantment_cooldowns = self.get_enchantment_cooldowns(
            member.id, enchantments, combat_events
        )
        skill_stacks_used = await self.database.get_user_skill_stacks_used(
            member.guild.id, member.id
        )
        enchantment_stacks_used = await self.database.get_user_enchantment_stacks_used(
            member.guild.id, member.id
        )

        active_status_effects = await self.get_active_status_effects(
            member.id, status_effects, combat_events
        )

        timeout_count = 0
        for event in combat_events:
            if (
                event.member_id == member.id
                and event.combat_event_type == CombatEventType.MEMBER_TURN_SKIP
            ):
                timeout_count += 1

        character = Character(
            member=member,
            skill_slots=skill_slots,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            active_enchantments=enchantments,
            enchantment_cooldowns=enchantment_cooldowns,
            enchantment_stacks_used=enchantment_stacks_used,
            status_effects=active_status_effects,
            equipment=equipment,
            defeated=defeated,
            leaving=leaving,
            is_out=is_out,
            force_skip=force_skip,
            ready=ready,
            timeout_count=timeout_count,
        )
        character.current_hp = await self.get_actor_current_hp(character, combat_events)
        return character

    async def apply_event(self, actor: Actor, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                event: EncounterEvent = event
                await self.apply_encounter_event(actor, event)
            case EventType.COMBAT:
                event: CombatEvent = event
                await self.apply_combat_event(actor, event)
            case EventType.STATUS_EFFECT:
                event: StatusEffectEvent = event
                await self.apply_status_event(actor, event)

    async def apply_encounter_event(self, actor: Actor, event: EncounterEvent):
        match event.encounter_event_type:
            case EncounterEventType.INITIATE:
                pass
            case EncounterEventType.NEW_ROUND:
                actor.force_skip = False
                if not actor.leaving:
                    actor.ready = True
            case EncounterEventType.ENEMY_PHASE_CHANGE:
                if actor.is_enemy:
                    actor: Opponent = actor
                    phase = actor.enemy.phases.index(actor.enemy.type)
                    enemy_type = actor.enemy.phases[phase + 1]
                    new_enemy = await self.factory.get_enemy(enemy_type)
                    actor.max_hp = int(
                        actor.max_hp * new_enemy.health / actor.enemy.health
                    )
                    actor.current_hp = actor.max_hp
                    actor.enemy = new_enemy
                    actor.image_url = new_enemy.image_url
                    actor.id -= phase + 10
                    actor.skill_stacks_used = {}
                    actor.status_effects = []

                    skills = []
                    for skill_type in new_enemy.skill_types:
                        skill = await self.factory.get_enemy_skill(skill_type)
                        skills.append(skill)

                    actor.skills = skills
                    actor.skill_cooldowns = self.get_skill_cooldowns(
                        actor.id, skills, []
                    )

                    actor.average_skill_multi = actor.get_potency_per_turn()
                    actor._initiative = new_enemy.initiative

        if event.member_id != actor.id:
            return

        match event.encounter_event_type:
            case EncounterEventType.MEMBER_REQUEST_JOIN:
                pass
            case EncounterEventType.MEMBER_ENGAGE:
                pass
            case EncounterEventType.MEMBER_REVIVE:
                actor.defeated = False
            case EncounterEventType.FORCE_SKIP:
                actor.force_skip = True
            case EncounterEventType.MEMBER_LEAVING:
                actor.leaving = True
            case EncounterEventType.MEMBER_OUT:
                actor.is_out = True
            case EncounterEventType.MEMBER_DISENGAGE:
                pass
            case EncounterEventType.MEMBER_DEFEAT | EncounterEventType.ENEMY_DEFEAT:
                actor.defeated = True
            case EncounterEventType.END:
                pass
            case EncounterEventType.PENALTY50:
                pass
            case EncounterEventType.PENALTY75:
                pass

    async def apply_combat_event(self, actor: Actor, event: CombatEvent):
        if event.target_id == actor.id:
            health = await self.get_event_health_delta(event)
            new_hp = actor.current_hp + health
            actor.current_hp = max(0, min(new_hp, actor.max_hp))

        if event.member_id != actor.id:
            return

        match event.combat_event_type:
            case CombatEventType.STATUS_EFFECT:
                status_id = event.skill_id
                for status in actor.status_effects:
                    if status.event.id != status_id:
                        continue
                    status.remaining_stacks += event.skill_value
                    break
            case CombatEventType.STATUS_EFFECT_OUTCOME:
                pass
            case CombatEventType.ENCHANTMENT_EFFECT_OUTCOME:
                pass
            case CombatEventType.MEMBER_TURN | CombatEventType.ENEMY_TURN:
                for skill_type in actor.skill_cooldowns:
                    if event.skill_type == skill_type:
                        actor.skill_cooldowns[skill_type] = 0
                    else:
                        if (
                            skill_type not in actor.skill_cooldowns
                            or actor.skill_cooldowns[skill_type] is None
                        ):
                            continue
                        actor.skill_cooldowns[skill_type] += 1

                if not actor.is_enemy:
                    actor: Character = actor
                    for enchantment_id in actor.enchantment_cooldowns:
                        if actor.enchantment_cooldowns[enchantment_id] is not None:
                            actor.enchantment_cooldowns[enchantment_id] += 1

                skill_id = event.skill_type if actor.is_enemy else event.skill_id

                if (
                    skill_id not in actor.skill_stacks_used
                    or actor.skill_stacks_used[skill_id] is None
                ):
                    actor.skill_stacks_used[skill_id] = 1
                else:
                    actor.skill_stacks_used[skill_id] += 1
            case CombatEventType.ENCHANTMENT_EFFECT:
                if actor.is_enemy:
                    return
                actor: Character = actor
                enchantment_id = event.skill_id
                for enchantment in actor.active_enchantments:
                    if enchantment.id == enchantment_id:
                        if (
                            enchantment_id not in actor.enchantment_stacks_used
                            or actor.enchantment_stacks_used[enchantment_id] is None
                        ):
                            actor.enchantment_stacks_used[enchantment_id] = 1
                        else:
                            actor.enchantment_stacks_used[enchantment.id] += 1
                        actor.enchantment_cooldowns[enchantment.id] = 0
                        break
            case CombatEventType.ENEMY_TURN_STEP | CombatEventType.MEMBER_TURN_STEP:
                pass
            case CombatEventType.MEMBER_END_TURN | CombatEventType.ENEMY_END_TURN:
                pass

    async def apply_status_event(self, actor: Actor, event: StatusEffectEvent):
        if event.actor_id != actor.id:
            return

        status_effect = await self.factory.get_status_effect(event.status_type)
        active_status_effect = ActiveStatusEffect(status_effect, event, event.stacks)
        actor.status_effects.append(active_status_effect)

    def get_undefeated_actors(self, actors: list[Actor]):
        return [actor for actor in actors if not actor.defeated]

    def get_used_skills(
        self, actor_id: int, context: EncounterContext
    ) -> list[SkillType]:
        used_skills = []
        combat_events = context.combat_events
        for event in combat_events:
            if (
                event.member_id == actor_id or (actor_id < 0 and event.member_id < 0)
            ) and event.skill_type is not None:
                skill_type = event.skill_type
                if (
                    skill_type not in used_skills
                    and context.turn_event_id_cutoff > event.id
                ):
                    used_skills.append(skill_type)
        return used_skills

    def get_enchantment_cooldowns(
        self,
        actor_id: int,
        enchantments: list[Enchantment],
        combat_events: list[CombatEvent],
    ) -> dict[SkillType, int]:
        cooldowns = {}
        last_used = 0
        for event in combat_events:
            if event.member_id == actor_id:
                if event.skill_id is not None:
                    enchantment_id = event.skill_id
                    if enchantment_id not in cooldowns:
                        cooldowns[enchantment_id] = max(0, last_used - 1)
                if event.combat_event_type in [
                    CombatEventType.ENEMY_END_TURN,
                    CombatEventType.MEMBER_END_TURN,
                ]:
                    last_used += 1

        round_count = last_used

        enchantment_data = {}

        for enchantment in enchantments:
            last_used = None
            enchantment_id = enchantment.id
            if enchantment_id in cooldowns:
                last_used = cooldowns[enchantment_id]
            elif (
                enchantment.base_enchantment.initial_cooldown is not None
                and enchantment.base_enchantment.initial_cooldown > 0
            ):
                last_used = (
                    -enchantment.base_enchantment.initial_cooldown
                    + round_count
                    + enchantment.base_enchantment.cooldown
                )

            enchantment_data[enchantment_id] = last_used
        return enchantment_data

    def get_skill_cooldowns(
        self, actor_id: int, skills: list[Skill], combat_events: list[CombatEvent]
    ) -> dict[SkillType, int]:
        cooldowns = {}
        last_used = 0
        for event in combat_events:
            if event.member_id == actor_id:
                if event.skill_type is not None:
                    skill_type = event.skill_type
                    if skill_type not in cooldowns:
                        cooldowns[skill_type] = max(0, last_used - 1)
                if event.combat_event_type in [
                    CombatEventType.ENEMY_END_TURN,
                    CombatEventType.MEMBER_END_TURN,
                ]:
                    last_used += 1

        round_count = last_used

        skill_data = {}

        for skill in skills:
            last_used = None
            skill_type = skill.base_skill.skill_type
            if skill_type in cooldowns:
                last_used = cooldowns[skill_type]
            elif (
                skill.base_skill.initial_cooldown is not None
                and skill.base_skill.initial_cooldown > 0
            ):
                last_used = (
                    -skill.base_skill.initial_cooldown
                    + round_count
                    + skill.base_skill.cooldown
                )

            skill_data[skill_type] = last_used
        return skill_data

    def get_encounter_scaling(self, actor: Actor, combatant_count: int = 1) -> float:
        encounter_scaling = 1
        if not actor.is_enemy:
            return encounter_scaling

        if combatant_count > 1:
            encounter_scaling = (
                1 / combatant_count * Config.CHARACTER_ENCOUNTER_SCALING_FACOTR
            )
        return encounter_scaling

    async def get_skill_damage_after_defense(
        self, actor: Actor, skill: Skill, incoming_damage: int
    ) -> float:
        return await self.get_damage_after_defense(
            actor, skill.base_skill.skill_effect, incoming_damage
        )

    async def get_damage_after_defense(
        self, actor: Actor, skill_effect: SkillEffect, incoming_damage: int
    ) -> float:
        if actor.is_enemy:
            return await self.get_opponent_damage_after_defense(
                actor, skill_effect, incoming_damage
            )
        else:
            return await self.get_character_damage_after_defense(
                actor, skill_effect, incoming_damage
            )

    async def get_character_damage_after_defense(
        self, character: Character, skill_effect: SkillEffect, incoming_damage: int
    ) -> float:
        modifier = 1
        flat_reduction = 0

        match skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier -= character.equipment.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
                flat_reduction = int(
                    character.equipment.gear_modifiers[GearModifierType.ARMOR] / 6
                )
            case SkillEffect.NEUTRAL_DAMAGE:
                modifier -= character.equipment.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.MAGICAL_DAMAGE:
                modifier -= character.equipment.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.EFFECT_DAMAGE:
                modifier -= character.equipment.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.HEALING:
                pass
            case SkillEffect.NOTHING | SkillEffect.BUFF:
                modifier = 0
                flat_reduction = 0

        return int(max(0, ((incoming_damage * modifier) - flat_reduction)))

    async def get_opponent_damage_after_defense(
        self, opponent: Opponent, skill_effect: SkillEffect, incoming_damage: int
    ) -> float:
        modifier = 1
        flat_reduction = 0

        match skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier -= opponent.enemy.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.NEUTRAL_DAMAGE:
                modifier -= opponent.enemy.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.MAGICAL_DAMAGE:
                modifier -= opponent.enemy.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.EFFECT_DAMAGE:
                modifier -= opponent.enemy.attributes[
                    CharacterAttribute.DAMAGE_REDUCTION
                ]
            case SkillEffect.HEALING:
                pass
            case SkillEffect.NOTHING | SkillEffect.BUFF:
                modifier = 0
                flat_reduction = 0

        return int(max(0, ((incoming_damage - flat_reduction) * modifier)))

    async def get_random_enemy(
        self, encounter_level: int, exclude: list[EnemyType] = None
    ) -> Enemy:
        if exclude is None:
            exclude = []

        enemies = [await self.factory.get_enemy(enemy_type) for enemy_type in EnemyType]
        possible_enemies = [
            enemy
            for enemy in enemies
            if encounter_level >= enemy.min_level
            and encounter_level <= enemy.max_level
            and not enemy.is_boss
            and enemy.type not in exclude
        ]

        spawn_weights = [enemy.weighting for enemy in possible_enemies]
        # spawn_weights = [1.0 / w for w in spawn_weights]
        sum_weights = sum(spawn_weights)
        spawn_weights = [w / sum_weights for w in spawn_weights]

        enemy = random.choices(possible_enemies, weights=spawn_weights)[0]
        return enemy
