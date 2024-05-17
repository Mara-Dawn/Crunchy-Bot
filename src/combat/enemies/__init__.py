from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.skills import NormalAttack
from items import BoxSeed, CatSeed, YellowSeed

# class Example(Enemy):
#     def __init__(self):
#         super().__init__(
#             name="Example Enemy",
#             type=EnemyType.EXAMPLE,
#             description="Example description",
#             information="Example information",
#             image="image.png",
#             level=1,
#             min_hp=90,
#             max_hp=110,
#             skills=[],
#             loot_table=[],
#             weighting=100,
#             min_drop_count=None,
#             max_drop_count=None,
#             min_beans_reward=None,
#             max_beans_reward=None,
#         )


class MindGoblin(Enemy):
    def __init__(self):
        super().__init__(
            name="Mind Goblin",
            type=EnemyType.MIND_GOBLIN,
            description="Comes with a big sack of nuts.",
            information="Mind goblin' deez nuts?",
            image="mind_goblin.png",
            level=1,
            min_hp=90,
            max_hp=110,
            skills=[NormalAttack],
            loot_table=[BoxSeed, CatSeed, YellowSeed],
        )
