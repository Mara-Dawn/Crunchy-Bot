from collections import Counter

import discord

from combat.effects.effect import EffectOutcome
from combat.enchantments.enchantment import EffectEnchantment
from combat.enemies.enemy import Enemy
from combat.equipment import CharacterEquipment
from combat.gear.types import CharacterAttribute, GearModifierType
from combat.skills.skill import Skill
from combat.skills.types import SkillEffect, SkillType
from combat.status_effects.status_effect import ActiveStatusEffect
from config import Config


class Actor:

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
        status_effects: list[ActiveStatusEffect],
        defeated: bool,
        image_url: str,
        leaving: bool = False,
        is_out: bool = False,
        force_skip: bool = True,
        timeout_count: int = 0,
        ready: bool = False,
    ):
        self.id = id
        self.name = name
        self.max_hp = int(max_hp)
        self.current_hp = int(max_hp)
        self._initiative = initiative
        self.is_enemy = is_enemy
        self.skills = skills
        self.skill_cooldowns = skill_cooldowns
        self.skill_stacks_used = skill_stacks_used
        self.status_effects = status_effects
        self.defeated = defeated
        self.leaving = leaving
        self.is_out = is_out
        self.force_skip = force_skip
        self.image_url = image_url
        self.ready = ready
        self.timeout_count = timeout_count
        self.round_modifier = EffectOutcome.EMPTY()

    @property
    def initiative(self):
        initiative = self._initiative
        if self.round_modifier.initiative is not None:
            initiative += self.round_modifier.initiative
        return initiative


class Character(Actor):

    def __init__(
        self,
        member: discord.Member,
        skill_slots: dict[int, Skill],
        skill_cooldowns: dict[SkillType, int],
        skill_stacks_used: dict[int, int],
        active_enchantments: list[EffectEnchantment],
        enchantment_cooldowns: dict[int, int],
        enchantment_stacks_used: dict[int, int],
        status_effects: list[ActiveStatusEffect],
        equipment: CharacterEquipment,
        defeated: bool,
        leaving: bool = False,
        is_out: bool = False,
        force_skip: bool = True,
        timeout_count: int = 0,
        ready: bool = False,
    ):
        self.member = member
        self.equipment = equipment
        max_hp = self.equipment.attributes[CharacterAttribute.MAX_HEALTH]

        initiative = (
            Config.CHARACTER_BASE_INITIATIVE
            + self.equipment.gear_modifiers[GearModifierType.DEXTERITY]
        )

        self.skill_slots = skill_slots
        self.active_enchantments = active_enchantments
        self.enchantment_stacks_used = enchantment_stacks_used
        self.enchantment_cooldowns = enchantment_cooldowns

        super().__init__(
            id=member.id,
            name=member.display_name,
            max_hp=max_hp,
            initiative=initiative,
            is_enemy=False,
            skills=[skill for skill in skill_slots.values() if skill is not None],
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            status_effects=status_effects,
            defeated=defeated,
            leaving=leaving,
            is_out=is_out,
            force_skip=force_skip,
            image_url=member.display_avatar.url,
            timeout_count=timeout_count,
            ready=ready,
        )


class Opponent(Actor):

    def __init__(
        self,
        id: int,
        enemy: Enemy,
        level: int,
        max_hp: int,
        skills: list[Skill],
        skill_cooldowns: dict[SkillType, int],
        skill_stacks_used: dict[int, int],
        status_effects: list[ActiveStatusEffect],
        defeated: bool,
        force_skip: bool = True,
        image_url: str = None,
        additional_info: str = None,
    ):
        if image_url is None:
            image_url = enemy.image_url
        name = enemy.name
        if additional_info is not None:
            name += f" ({additional_info})"
        super().__init__(
            id=None,
            name=name,
            max_hp=max_hp,
            initiative=enemy.initiative,
            is_enemy=True,
            skills=skills,
            skill_cooldowns=skill_cooldowns,
            skill_stacks_used=skill_stacks_used,
            status_effects=status_effects,
            defeated=defeated,
            force_skip=force_skip,
            image_url=image_url,
            timeout_count=0,
            ready=True,
        )
        self.level = level
        self.enemy = enemy
        self.id = id

        self.average_skill_multi = enemy.fixed_avg_potency
        if self.average_skill_multi is None:
            self.average_skill_multi = self.get_potency_per_turn()

    def get_potency_per_turn(self):
        sorted_skills = sorted(
            self.skills,
            key=lambda x: (
                x.base_skill.custom_value
                if x.base_skill.custom_value is not None
                else (
                    x.base_skill.base_value
                    if x.base_skill.skill_effect
                    not in [SkillEffect.HEALING, SkillEffect.BUFF]
                    else 100
                )
            ),
            reverse=True,
        )

        max_depth = self.enemy.health * 2
        cooldowns: dict[SkillType, int] = {}
        initial_state: dict[SkillType, int] = {}

        for skill in sorted_skills:
            cooldowns[skill.base_skill.type] = skill.base_skill.cooldown
            initial_state[skill.base_skill.type] = 0
            if skill.base_skill.initial_cooldown is not None:
                initial_state[skill.base_skill.type] = skill.base_skill.initial_cooldown

        state_list: list[dict[SkillType, int]] = []
        skill_count = Counter()

        def get_rotation(
            state_list: list[dict[SkillType, int]],
            skill_count: Counter,
            state: dict[SkillType, int],
            depth_check: int,
        ) -> list[dict[SkillType, int]]:
            if depth_check <= 0:
                return

            state_list.append(state)

            next_state: dict[SkillType, int] = {}

            skills_chosen = 0

            for skill_type, cooldown in state.items():
                if cooldown <= 0 and skills_chosen < self.enemy.actions_per_turn:
                    next_state[skill_type] = cooldowns[skill_type]
                    skill_count[skill_type] += 1
                    skills_chosen += 1
                    continue

                next_state[skill_type] = max(0, cooldown - 1)

            if skills_chosen == 0:
                raise StopIteration("No available skill found.")

            get_rotation(state_list, skill_count, next_state, (depth_check - 1))

        get_rotation(state_list, skill_count, initial_state, max_depth)

        rotation_length = len(state_list)
        potency = 0

        for skill in sorted_skills:
            base_potency = 0
            if skill.base_skill.skill_effect not in [
                SkillEffect.BUFF,
                SkillEffect.HEALING,
            ]:
                base_potency = skill.base_skill.base_value * skill.base_skill.hits
            potency_per_turn = (
                base_potency
                * skill_count[skill.base_skill.skill_type]
                / rotation_length
            )
            potency += potency_per_turn

        return potency
