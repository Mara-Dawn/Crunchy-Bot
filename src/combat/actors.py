import discord
from combat.enemies.enemy import Enemy
from combat.skills.skill import SkillData


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

    def get_skill_value(self, skill_data: SkillData) -> int:
        if skill_data not in self.skill_data:
            return 0
        return skill_data.skill.base_value * 5


class Character(Actor):

    def __init__(
        self,
        member: discord.Member,
        skill_data: list[SkillData],
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
