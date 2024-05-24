import random

import discord
from combat.enemies.enemy import Enemy
from combat.equipment import CharacterEquipment
from combat.gear.types import CharacterAttribute, GearModifierType
from combat.skills.skill import Skill, SkillData
from combat.skills.types import DamageInstance, SkillEffect, SkillType


class Actor:

    CHARACTER_SCALING_FACOTR = 0.9
    OPPONENT_SCALING_FACTOR = 1.05

    def __init__(
        self,
        id: int,
        name: str,
        max_hp: int,
        initiative: int,
        is_enemy: bool,
        skills: list[Skill],
        skill_cooldowns: dict[SkillType, int],
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
        self.defeated = defeated
        self.image = image

    def get_skill_data(self, skill: Skill) -> SkillData:
        pass

    def get_skill_damage(
        self, skill: Skill, combatant_count: int = 1, force_roll: int = None
    ) -> list[DamageInstance]:
        pass


class Character(Actor):

    BASE_INITIATIVE = 10

    def __init__(
        self,
        member: discord.Member,
        skills: list[Skill],
        skill_cooldowns: dict[SkillType, int],
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
            defeated=defeated,
            image=member.avatar.url,
        )

    def get_skill_data(self, skill: Skill) -> SkillData:
        weapon_min_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MIN
        ]
        weapon_max_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MAX
        ]

        return SkillData(
            skill=skill,
            last_used=self.skill_cooldowns[skill.type],
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
        skill_base_value = skill.base_value

        weapon_min_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MIN
        ]
        weapon_max_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MAX
        ]

        modifier = 1

        match skill.skill_effect:
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
            encounter_scaling = 1 / combatant_count * self.CHARACTER_SCALING_FACOTR

        attack_count = skill.hits
        attacks = []
        for _ in range(attack_count):
            weapon_roll = force_roll
            if weapon_roll is None:
                weapon_roll = random.randint(weapon_min_roll, weapon_max_roll)

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


class Opponent(Actor):

    def __init__(
        self,
        enemy: Enemy,
        max_hp: int,
        skills: list[Skill],
        skill_cooldowns: dict[SkillType, int],
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
            defeated=defeated,
            image=f"attachment://{enemy.image}",
        )
        self.enemy = enemy

    def get_skill_data(self, skill: Skill) -> SkillData:
        weapon_min_roll = self.enemy.min_dmg
        weapon_max_roll = self.enemy.max_dmg

        return SkillData(
            skill=skill,
            last_used=self.skill_cooldowns[skill.type],
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

        skill_base_value = skill.base_value

        weapon_min_roll = self.enemy.min_dmg
        weapon_max_roll = self.enemy.max_dmg

        modifier = 1
        encounter_scaling = 1
        attack_count = skill.hits
        if combatant_count > 1:
            attack_count *= max(1, int(combatant_count * 0.7))
            encounter_scaling = (
                combatant_count / attack_count * Actor.OPPONENT_SCALING_FACTOR
            )

        attacks = []
        for _ in range(attack_count):
            weapon_roll = random.randint(weapon_min_roll, weapon_max_roll)
            crit_roll = random.random()
            critical_hit = False
            critical_modifier = 1
            if crit_roll < self.enemy.crit_chance:
                critical_hit = True
                critical_modifier = self.enemy.crit_mod

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
