import random

from combat.actors import Actor, Character, Opponent
from combat.encounter import EncounterContext
from combat.gear.types import CharacterAttribute, GearModifierType
from combat.skills.skill import CharacterSkill, Skill, SkillType
from combat.skills.skills import *  # noqa: F403
from combat.skills.types import SkillEffect, SkillInstance, SkillTarget
from config import Config
from control.ai_manager import AIManager
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent


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
        self.log_name = "Combat Skills"

    async def listen_for_event(self, event: BotEvent):
        pass

    async def get_character_default_target(
        self, source: Actor, skill: Skill, context: EncounterContext
    ) -> Actor:

        match skill.base_skill.default_target:
            case SkillTarget.OPPONENT:
                return context.opponent
            case SkillTarget.SELF:
                return source

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
                    "Make a creative yo mama so fat joke. Maximum length is 30 words."
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

        attack_count = skill.base_skill.hits
        skill_instances = []
        for _ in range(attack_count):

            if force_min:
                weapon_roll = weapon_min_roll
            elif force_max:
                weapon_roll = weapon_max_roll
            else:
                weapon_roll = random.randint(int(weapon_min_roll), int(weapon_max_roll))

            crit_roll = random.random()
            critical_hit = False
            critical_modifier = 1
            if crit_roll < character.equipment.attributes[CharacterAttribute.CRIT_RATE]:
                critical_hit = True
                critical_modifier = character.equipment.attributes[
                    CharacterAttribute.CRIT_DAMAGE
                ]

            skill_instance = SkillInstance(
                weapon_roll=weapon_roll,
                skill_base=skill_base_value,
                modifier=modifier,
                critical_modifier=critical_modifier,
                encounter_scaling=encounter_scaling,
                is_crit=critical_hit,
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
                modifier += opponent.enemy.attributes[CharacterAttribute.HEALING_BONUS]

        encounter_scaling = opponent.enemy.min_encounter_scale
        raw_attack_count = skill.base_skill.hits
        attack_count = raw_attack_count

        if (
            combatant_count > opponent.enemy.min_encounter_scale
            and not skill.base_skill.aoe
        ):
            encounter_scale = combatant_count - (opponent.enemy.min_encounter_scale - 1)
            attack_count_scaling = max(1, encounter_scale * 0.75)
            attack_count = int(raw_attack_count * attack_count_scaling)
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

            crit_roll = random.random()
            critical_hit = False
            critical_modifier = 1
            if crit_roll < opponent.enemy.attributes[CharacterAttribute.CRIT_RATE]:
                critical_hit = True
                critical_modifier = opponent.enemy.attributes[
                    CharacterAttribute.CRIT_DAMAGE
                ]

            damage_instance = SkillInstance(
                weapon_roll=weapon_roll,
                skill_base=skill_scaling,
                modifier=modifier,
                critical_modifier=critical_modifier,
                encounter_scaling=encounter_scaling,
                is_crit=critical_hit,
            )
            attacks.append(damage_instance)

        return attacks
