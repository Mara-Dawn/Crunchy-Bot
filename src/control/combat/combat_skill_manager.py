import datetime
import random

from discord.ext import commands

from combat.actors import Actor, Character, Opponent
from combat.encounter import EncounterContext
from combat.enemies.types import EnemyType
from combat.gear.types import CharacterAttribute, GearModifierType
from combat.skills.skill import CharacterSkill, Skill, SkillInstance, SkillType
from combat.skills.skills import *  # noqa: F403
from combat.skills.types import SkillEffect, SkillTarget
from config import Config
from control.ai_manager import AIManager
from control.combat.effect_manager import CombatEffectManager
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType


class CombatSkillManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.ai_manager: AIManager = self.controller.get_service(AIManager)
        self.effect_manager: CombatEffectManager = self.controller.get_service(
            CombatEffectManager
        )
        self.log_name = "Combat Skills"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_character_default_target(
        self, source: Actor, skill: Skill, context: EncounterContext
    ) -> Actor | None:

        match skill.base_skill.default_target:
            case SkillTarget.OPPONENT:
                return context.opponent
            case SkillTarget.SELF:
                return source
            case SkillTarget.RANDOM_PARTY_MEMBER:
                active_combatants = context.active_combatants
                if len(active_combatants) <= 0:
                    return None
                return random.choice(active_combatants)
            case SkillTarget.RANDOM_DEFEATED_PARTY_MEMBER:
                defeated_combatants = context.defeated_combatants
                if len(defeated_combatants) <= 0:
                    return None
                return random.choice(defeated_combatants)

    async def get_skill_data(self, actor: Actor, skill: Skill) -> CharacterSkill:
        if actor.is_enemy:
            return await self.get_opponent_skill_data(actor, skill)
        else:
            return await self.get_character_skill_data(actor, skill)

    async def get_character_skill_data(
        self, character: Character, skill: Skill
    ) -> CharacterSkill:
        skill_type = skill.type
        skill_id = skill.id
        stacks_used = 0
        last_used = None

        if skill_id in character.skill_stacks_used:
            stacks_used = character.skill_stacks_used[skill_id]
        if skill_type in character.skill_cooldowns:
            last_used = character.skill_cooldowns[skill.base_skill.skill_type]

        penalty = character.skill_slots[
            0
        ].base_skill.skill_effect != skill.base_skill.skill_effect and skill.base_skill.skill_effect not in [
            SkillEffect.HEALING,
            SkillEffect.NEUTRAL_DAMAGE,
        ]

        charges_outcome = await self.effect_manager.on_skill_charges(character, skill)
        hits_outcome = await self.effect_manager.on_skill_hits(character, skill)

        return CharacterSkill(
            skill=skill,
            last_used=last_used,
            stacks_used=stacks_used,
            min_roll=(await self.get_skill_effect(character, skill, force_min=True))[
                0
            ].raw_value,
            max_roll=(await self.get_skill_effect(character, skill, force_max=True))[
                0
            ].raw_value,
            penalty=penalty,
            additional_stacks=charges_outcome.value,
            additional_hits=hits_outcome.value,
        )

    async def get_opponent_skill_data(
        self, opponent: Opponent, skill: Skill
    ) -> CharacterSkill:
        base_damage = (
            Config.OPPONENT_DAMAGE_BASE[opponent.level] / opponent.enemy.damage_scaling
        )
        weapon_min_roll = int(base_damage * (1 - Config.OPPONENT_DAMAGE_VARIANCE))
        weapon_max_roll = int(base_damage * (1 + Config.OPPONENT_DAMAGE_VARIANCE))

        skill_id = skill.id
        stacks_used = 0

        if skill_id in opponent.skill_stacks_used:
            stacks_used = opponent.skill_stacks_used[skill_id]

        custom_description = await self.custom_skill_description(skill.type)
        if custom_description is not None:
            skill.description = custom_description

        return CharacterSkill(
            skill=skill,
            last_used=opponent.skill_cooldowns[skill.base_skill.skill_type],
            stacks_used=stacks_used,
            min_roll=(
                await self.get_skill_effect(opponent, skill, force_min=weapon_min_roll)
            )[0].raw_value,
            max_roll=(
                await self.get_skill_effect(opponent, skill, force_max=weapon_max_roll)
            )[0].raw_value,
        )

    async def custom_skill_description(self, skill_type: SkillType) -> str | None:
        match skill_type:
            case SkillType.AROUND_THE_WORLD:
                joke = await self.ai_manager.raw_prompt(
                    "Tell a creative yo mama joke. Maximum length is 30 words."
                )
                return joke.replace('"', "'")
        return None

    async def get_skill_effect(
        self,
        actor: Actor,
        skill: Skill,
        combatant_count: int = 1,
        force_min: bool = False,
        force_max: bool = False,
    ) -> list[SkillInstance]:
        if actor.is_enemy:
            return await self.get_opponent_skill_effect(
                actor, skill, combatant_count, force_min, force_max
            )
        else:
            return await self.get_character_skill_effect(
                actor, skill, combatant_count, force_min, force_max
            )

    async def get_special_skill_modifier(
        self,
        context: EncounterContext,
        skill: Skill,
    ) -> tuple[float, str]:
        skill_type = skill.type
        guild_id = context.encounter.guild_id

        modifier = 1
        description = None

        match skill_type:
            case SkillType.KARMA:
                enemy_data = await self.database.get_encounter_events(
                    guild_id,
                    [EnemyType.BONTERRY, EnemyType.BONTERRY_KING],
                    [EncounterEventType.ENEMY_DEFEAT],
                )
                kill_count = 0
                for _, enemy_type in enemy_data:
                    if enemy_type == EnemyType.BONTERRY:
                        kill_count += 1
                    if enemy_type == EnemyType.BONTERRY_KING:
                        break
                modifier = kill_count
                description = skill.description.replace("@", str(kill_count))

        return modifier, description

    async def trigger_special_skill_effects(
        self,
        event: CombatEvent,
    ) -> list[SkillInstance]:

        skill_type = event.skill_type
        if skill_type is None:
            return

        match skill_type:
            case SkillType.SMELLING_SALT:
                event = EncounterEvent(
                    datetime.datetime.now(),
                    event.guild_id,
                    event.encounter_id,
                    event.target_id,
                    EncounterEventType.MEMBER_REVIVE,
                )
                await self.controller.dispatch_event(event)

    async def get_character_skill_effect(
        self,
        character: Character,
        skill: Skill,
        combatant_count: int = 1,
        force_min: bool = False,
        force_max: bool = False,
    ) -> list[SkillInstance]:
        skill_base_value = skill.base_skill.base_value
        weapon_min_roll = character.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MIN
        ]
        weapon_max_roll = character.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MAX
        ]

        modifier = 1
        base_dmg_type = character.skill_slots[0].base_skill.skill_effect

        encounter_scaling = 1
        if combatant_count > 1:
            encounter_scaling = (
                1 / combatant_count * Config.CHARACTER_ENCOUNTER_SCALING_FACOTR
            )

        critical_modifier = character.equipment.attributes[
            CharacterAttribute.CRIT_DAMAGE
        ]

        match skill.base_skill.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier += character.equipment.attributes[
                    CharacterAttribute.PHYS_DAMAGE_INCREASE
                ]
                if base_dmg_type != skill.base_skill.skill_effect:
                    modifier *= Config.SKILL_TYPE_PENALTY
            case SkillEffect.MAGICAL_DAMAGE:
                modifier += character.equipment.attributes[
                    CharacterAttribute.MAGIC_DAMAGE_INCREASE
                ]
                if base_dmg_type != skill.base_skill.skill_effect:
                    modifier *= Config.SKILL_TYPE_PENALTY
            case SkillEffect.HEALING:
                encounter_scaling = 1
                weapon_lvl = character.equipment.weapon.level
                base_roll = Config.OPPONENT_DAMAGE_BASE[weapon_lvl]
                weapon_min_roll = base_roll * (1 - Config.OPPONENT_DAMAGE_VARIANCE)
                weapon_max_roll = base_roll * (1 + Config.OPPONENT_DAMAGE_VARIANCE)
                modifier += character.equipment.attributes[
                    CharacterAttribute.HEALING_BONUS
                ]
                critical_modifier = Config.HEAL_CRIT_MODIFIER
            case SkillEffect.NOTHING | SkillEffect.BUFF:
                modifier = 0

        attack_count = skill.base_skill.hits
        hit_outcome = await self.effect_manager.on_skill_hits(character, skill)
        if hit_outcome.value is not None:
            attack_count += hit_outcome.value
        skill_instances = []
        for _ in range(attack_count):

            if force_min:
                weapon_roll = weapon_min_roll
            elif force_max:
                weapon_roll = weapon_max_roll
            else:
                weapon_roll = random.randint(int(weapon_min_roll), int(weapon_max_roll))

            crit_rate = character.equipment.attributes[CharacterAttribute.CRIT_RATE]
            if skill.base_skill.custom_crit is not None:
                crit_rate = skill.base_skill.custom_crit

            skill_instance = SkillInstance(
                weapon_roll=weapon_roll,
                skill_base=skill_base_value,
                modifier=modifier,
                critical_modifier=critical_modifier,
                encounter_scaling=encounter_scaling,
                crit_chance=crit_rate,
            )
            skill_instances.append(skill_instance)

        return skill_instances

    async def get_opponent_skill_effect(
        self,
        opponent: Opponent,
        skill: Skill,
        combatant_count: int = 1,
        force_min: bool = False,
        force_max: bool = False,
    ) -> list[SkillInstance]:

        skill_base_value = skill.base_skill.base_value
        skill_scaling = skill_base_value / opponent.average_skill_multi

        effective_level = opponent.level
        if opponent.enemy.is_boss:
            effective_level += 1

        base_damage = (
            Config.OPPONENT_DAMAGE_BASE[effective_level] / opponent.enemy.damage_scaling
        )

        weapon_min_roll = int(base_damage * (1 - Config.OPPONENT_DAMAGE_VARIANCE))
        weapon_max_roll = int(base_damage * (1 + Config.OPPONENT_DAMAGE_VARIANCE))

        modifier = pow(
            Config.OPPONENT_LEVEL_SCALING_FACTOR,
            (opponent.level - opponent.enemy.min_level),
        )

        encounter_scaling = opponent.enemy.min_encounter_scale
        raw_attack_count = skill.base_skill.hits
        attack_count = raw_attack_count
        force_scaling = False
        critical_modifier = opponent.enemy.attributes[CharacterAttribute.CRIT_DAMAGE]

        match skill.base_skill.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier += opponent.enemy.attributes[
                    CharacterAttribute.PHYS_DAMAGE_INCREASE
                ]
            case SkillEffect.MAGICAL_DAMAGE:
                modifier += opponent.enemy.attributes[
                    CharacterAttribute.MAGIC_DAMAGE_INCREASE
                ]
            case SkillEffect.HEALING:
                encounter_scaling = 1
                force_scaling = True
                skill_scaling = skill_base_value
                modifier += opponent.enemy.attributes[CharacterAttribute.HEALING_BONUS]
                base_roll = opponent.max_hp
                weapon_min_roll = base_roll * (1 - Config.OPPONENT_DAMAGE_VARIANCE)
                weapon_max_roll = base_roll * (1 + Config.OPPONENT_DAMAGE_VARIANCE)
                critical_modifier = Config.HEAL_CRIT_MODIFIER
            case SkillEffect.NOTHING | SkillEffect.BUFF:
                modifier = 0

        if (
            combatant_count > opponent.enemy.min_encounter_scale
            and not skill.base_skill.aoe
            and not force_scaling
        ):
            max_hits = 10
            if skill.base_skill.max_hits is not None:
                max_hits = skill.base_skill.max_hits

            encounter_scale = combatant_count - (opponent.enemy.min_encounter_scale - 1)
            if not skill.base_skill.no_scaling:
                factor = raw_attack_count / max_hits
                attack_count_scaling = pow(1 - factor, 7)

                scaling = 1 + (encounter_scale * attack_count_scaling)
                attack_count = raw_attack_count * scaling

                # attack_count_scaling = max(1, encounter_scale * 0.75)
                attack_count = min(max_hits, int(raw_attack_count * scaling))

            encounter_scaling += (
                encounter_scale
                * Config.OPPONENT_ENCOUNTER_SCALING_FACTOR
                * raw_attack_count
                / attack_count
            ) - 1

        attacks = []
        for _ in range(attack_count):

            if force_min:
                weapon_roll = weapon_min_roll
            elif force_max:
                weapon_roll = weapon_max_roll
            else:
                weapon_roll = random.randint(int(weapon_min_roll), int(weapon_max_roll))

            crit_rate = opponent.enemy.attributes[CharacterAttribute.CRIT_RATE]
            if skill.base_skill.custom_crit is not None:
                crit_rate = skill.base_skill.custom_crit

            damage_instance = SkillInstance(
                weapon_roll=weapon_roll,
                skill_base=skill_scaling,
                modifier=modifier,
                critical_modifier=critical_modifier,
                encounter_scaling=encounter_scaling,
                crit_chance=crit_rate,
            )
            attacks.append(damage_instance)

        return attacks
