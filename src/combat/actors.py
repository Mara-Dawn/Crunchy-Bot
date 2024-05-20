import random

import discord
from combat.enemies.enemy import Enemy
from combat.equipment import CharacterEquipment
from combat.gear.types import CharacterAttribute, GearModifierType
from combat.skills.skill import Skill, SkillData
from combat.skills.types import DamageInstance, SkillEffect


class Actor:

    def __init__(
        self,
        id: int,
        name: str,
        max_hp: int,
        initiative: int,
        is_enemy: bool,
        skill_data: list[SkillData],
        defeated: bool,
    ):
        self.id = id
        self.name = name
        self.max_hp = max_hp
        self.initiative = initiative
        self.is_enemy = is_enemy
        self.skill_data = skill_data
        self.defeated = defeated


class Character(Actor):

    def __init__(
        self,
        member: discord.Member,
        skill_data: list[SkillData],
        equipment: CharacterEquipment,
        defeated: bool,
    ):
        super().__init__(
            id=member.id,
            name=member.display_name,
            max_hp=100,
            initiative=10,
            is_enemy=False,
            skill_data=skill_data,
            defeated=defeated,
        )
        self.member = member
        self.equipment = equipment

    def get_skill_value(self, skill: Skill) -> DamageInstance:

        skill_base_value = skill.base_value

        weapon_min_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MIN
        ]
        weapon_max_roll = self.equipment.weapon.modifiers[
            GearModifierType.WEAPON_DAMAGE_MAX
        ]

        weapon_roll = random.randint(weapon_min_roll, weapon_max_roll)

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
            is_crit=critical_hit,
        )
        return damage_instance


class Opponent(Actor):

    def __init__(
        self, enemy: Enemy, max_hp: int, skill_data: list[SkillData], defeated: bool
    ):
        super().__init__(
            id=None,
            name=enemy.name,
            max_hp=max_hp,
            initiative=enemy.initiative,
            is_enemy=True,
            skill_data=skill_data,
            defeated=defeated,
        )
        self.enemy = enemy

    def get_skill_value(self, skill_data: SkillData) -> int:
        if skill_data not in self.skill_data:
            return 0
        return skill_data.skill.base_value
