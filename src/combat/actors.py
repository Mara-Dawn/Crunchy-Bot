import random

import discord
from combat.enemies.enemy import Enemy
from combat.equipment import CharacterEquipment
from combat.gear.types import CharacterAttribute, GearModifierType
from combat.skills.skill import CharacterSkill, Skill
from combat.skills.types import DamageInstance, SkillEffect, SkillType


class Actor:

    CHARACTER_ENCOUNTER_SCALING_FACOTR = 0.9
    OPPONENT_ENCOUNTER_SCALING_FACTOR = 1.2
    OPPONENT_LEVEL_SCALING_FACTOR = 0.5

    def __init__(
        self,
        id: int,
        name: str,
        max_hp: int,
        initiative: int,
        is_enemy: bool,
        skills: list[Skill],
        skill_cooldowns: dict[SkillType, int],
        skill_stacks_used: dict[SkillType, int],
        defeated: bool,
        image: str,
    ):
        self.id = id
        self.name = name
        self.max_hp = max_hp
        self.initiative = initiative
        self.is_enemy = is_enemy
        self.skills = skills
        self.skill_cooldowns = skill_cooldowns
        self.skill_stacks_used = skill_stacks_used
        self.defeated = defeated
        self.image = image

    def get_skill_data(self, skill: Skill) -> CharacterSkill:
        pass

    def get_skill_damage(
        self, skill: Skill, combatant_count: int = 1, force_roll: int = None
    ) -> list[DamageInstance]:
        pass

    def get_damage_after_defense(self, skill: Skill, incoming_damage: int) -> float:
        pass


class Character(Actor):

    BASE_INITIATIVE = 10

    def __init__(
        self,
        member: discord.Member,
        skills: list[Skill],
        skill_cooldowns: dict[SkillType, int],
        skill_stacks_used: dict[SkillType, int],
        equipment: CharacterEquipment,
        defeated: bool,
    ):
        self.member = member
        self.equipment = equipment
        max_hp = self.equipment.attributes[CharacterAttribute.MAX_HEALTH]
        initiative = (
            self.BASE_INITIATIVE
            + self.equipment.gear_modifiers[GearModifierType.DEXTERITY]
        )
        super().__init__(
            id=member.id,
            name=member.display_name,
            max_hp=max_hp,
            initiative=initiative,
            is_enemy=False,
            skills=skills,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            defeated=defeated,
            image=member.avatar.url,
        )

    def get_skill_data(self, skill: Skill) -> CharacterSkill:
        weapon_min_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MIN
        ]
        weapon_max_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MAX
        ]

        skill_type = skill.type
        stacks_used = 0
        last_used = None

        if skill_type in self.skill_stacks_used:
            stacks_used = self.skill_stacks_used[skill_type]

        if skill_type in self.skill_cooldowns:
            last_used = self.skill_cooldowns[skill.base_skill.skill_type]

        return CharacterSkill(
            skill=skill,
            last_used=last_used,
            stacks_used=stacks_used,
            min_roll=self.get_skill_damage(skill, force_roll=weapon_min_roll)[
                0
            ].raw_value,
            max_roll=self.get_skill_damage(skill, force_roll=weapon_max_roll)[
                0
            ].raw_value,
        )

    def get_skill_damage(
        self, skill: Skill, combatant_count: int = 1, force_roll: int = None
    ) -> list[DamageInstance]:
        skill_base_value = skill.base_skill.scaling
        weapon_min_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MIN
        ]
        weapon_max_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MAX
        ]

        modifier = 1

        match skill.base_skill.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier += self.equipment.attributes[
                    CharacterAttribute.PHYS_DAMAGE_INCREASE
                ]
            case SkillEffect.MAGICAL_DAMAGE:
                modifier += self.equipment.attributes[
                    CharacterAttribute.MAGIC_DAMAGE_INCREASE
                ]
            case SkillEffect.HEALING:
                modifier += self.equipment.attributes[CharacterAttribute.HEALING_BONUS]

        encounter_scaling = 1
        if combatant_count > 1:
            encounter_scaling = (
                1 / combatant_count * self.CHARACTER_ENCOUNTER_SCALING_FACOTR
            )

        attack_count = skill.base_skill.hits
        attacks = []
        for _ in range(attack_count):
            weapon_roll = force_roll
            if weapon_roll is None:
                weapon_roll = random.randint(int(weapon_min_roll), int(weapon_max_roll))

            crit_roll = random.random()
            critical_hit = False
            critical_modifier = 1
            if crit_roll < self.equipment.attributes[CharacterAttribute.CRIT_RATE]:
                critical_hit = True
                critical_modifier = self.equipment.attributes[
                    CharacterAttribute.CRIT_DAMAGE
                ]

            damage_instance = DamageInstance(
                weapon_roll=weapon_roll,
                skill_base=skill_base_value,
                modifier=modifier,
                critical_modifier=critical_modifier,
                encounter_scaling=encounter_scaling,
                is_crit=critical_hit,
            )
            attacks.append(damage_instance)

        return attacks

    def get_damage_after_defense(self, skill: Skill, incoming_damage: int) -> float:

        modifier = 1
        flat_reduction = 0

        match skill.base_skill.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier -= self.equipment.attributes[
                    CharacterAttribute.PHYS_DAMAGE_REDUCTION
                ]
                flat_reduction = int(
                    self.equipment.gear_modifiers[GearModifierType.ARMOR] / 4
                )
            case SkillEffect.MAGICAL_DAMAGE:
                modifier -= self.equipment.attributes[
                    CharacterAttribute.MAGIC_DAMAGE_REDUCTION
                ]
            case SkillEffect.HEALING:
                pass

        return int(max(0, ((incoming_damage * modifier) - flat_reduction)))


class Opponent(Actor):

    def __init__(
        self,
        enemy: Enemy,
        level: int,
        max_hp: int,
        skills: list[Skill],
        skill_cooldowns: dict[SkillType, int],
        skill_stacks_used: dict[SkillType, int],
        defeated: bool,
    ):
        super().__init__(
            id=None,
            name=enemy.name,
            max_hp=max_hp,
            initiative=enemy.initiative,
            is_enemy=True,
            skills=skills,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            defeated=defeated,
            image=f"attachment://{enemy.image}",
        )
        self.level = level
        self.enemy = enemy

    def get_skill_data(self, skill: Skill) -> CharacterSkill:
        weapon_min_roll = self.enemy.min_dmg
        weapon_max_roll = self.enemy.max_dmg

        skill_type = skill.type
        stacks_used = 0

        if skill_type in self.skill_stacks_used:
            stacks_used = self.skill_stacks_used[skill_type]

        return CharacterSkill(
            skill=skill,
            last_used=self.skill_cooldowns[skill.base_skill.skill_type],
            stacks_used=stacks_used,
            min_roll=self.get_skill_damage(skill, force_roll=weapon_min_roll)[
                0
            ].raw_value,
            max_roll=self.get_skill_damage(skill, force_roll=weapon_max_roll)[
                0
            ].raw_value,
        )

    def get_skill_damage(
        self, skill: Skill, combatant_count: int = 1, force_roll: int = None
    ) -> list[DamageInstance]:

        skill_base_value = skill.base_skill.scaling

        weapon_min_roll = self.enemy.min_dmg
        weapon_max_roll = self.enemy.max_dmg

        modifier = 1 + (
            self.OPPONENT_LEVEL_SCALING_FACTOR * (self.level - self.enemy.min_level)
        )

        match skill.base_skill.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier += self.enemy.attributes[
                    CharacterAttribute.PHYS_DAMAGE_INCREASE
                ]
            case SkillEffect.MAGICAL_DAMAGE:
                modifier += self.enemy.attributes[
                    CharacterAttribute.MAGIC_DAMAGE_INCREASE
                ]
            case SkillEffect.HEALING:
                modifier += self.enemy.attributes[CharacterAttribute.HEALING_BONUS]

        encounter_scaling = 1
        attack_count = skill.base_skill.hits
        if combatant_count > 1:
            attack_count_scaling = max(1, combatant_count * 0.7)
            attack_count = int(attack_count * attack_count_scaling)
            encounter_scaling = (
                combatant_count
                / attack_count_scaling
                * Actor.OPPONENT_ENCOUNTER_SCALING_FACTOR
            )

        attacks = []
        for _ in range(attack_count):
            weapon_roll = random.randint(weapon_min_roll, weapon_max_roll)

            crit_roll = random.random()
            critical_hit = False
            critical_modifier = 1
            if crit_roll < self.enemy.attributes[CharacterAttribute.CRIT_RATE]:
                critical_hit = True
                critical_modifier = self.enemy.attributes[
                    CharacterAttribute.CRIT_DAMAGE
                ]

            damage_instance = DamageInstance(
                weapon_roll=weapon_roll,
                skill_base=skill_base_value,
                modifier=modifier,
                critical_modifier=critical_modifier,
                encounter_scaling=encounter_scaling,
                is_crit=critical_hit,
            )
            attacks.append(damage_instance)

        return attacks

    def get_damage_after_defense(self, skill: Skill, incoming_damage: int) -> float:

        modifier = 1
        flat_reduction = 0

        match skill.base_skill.skill_effect:
            case SkillEffect.PHYSICAL_DAMAGE:
                modifier -= self.enemy.attributes[
                    CharacterAttribute.PHYS_DAMAGE_REDUCTION
                ]
            case SkillEffect.MAGICAL_DAMAGE:
                modifier -= self.enemy.attributes[
                    CharacterAttribute.MAGIC_DAMAGE_REDUCTION
                ]
            case SkillEffect.HEALING:
                pass

        return int(max(0, ((incoming_damage - flat_reduction) * modifier)))
