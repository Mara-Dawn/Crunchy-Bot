import discord
from combat.enemies.enemy import Enemy
from combat.skills.skill import Skill


class Actor:

    def __init__(
        self,
        id: int,
        name: str,
        max_hp: int,
        initiative: int,
        is_enemy: bool,
        skills: list[Skill],
        defeated: bool,
    ):
        self.id = id
        self.name = name
        self.max_hp = max_hp
        self.initiative = initiative
        self.is_enemy = is_enemy
        self.skills = skills
        self.defeated = defeated

    def get_skill_value(self, skill: Skill) -> int:
        if skill not in self.skills:
            return 0
        return skill.base_value * 15


class Character(Actor):

    def __init__(self, member: discord.Member, skills: list[Skill], defeated: bool):
        super().__init__(
            id=member.id,
            name=member.display_name,
            max_hp=100,
            initiative=10,
            is_enemy=False,
            skills=skills,
            defeated=defeated,
        )
        self.member = member


class Opponent(Actor):

    def __init__(self, enemy: Enemy, max_hp: int, defeated: bool):
        super().__init__(
            id=None,
            name=enemy.name,
            max_hp=max_hp,
            initiative=enemy.initiative,
            is_enemy=True,
            skills=enemy.skills,
            defeated=defeated,
        )
        self.enemy = enemy
