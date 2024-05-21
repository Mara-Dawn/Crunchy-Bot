from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.skills import DeezNuts
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
#             min_dmg=1,
#             max_dmg=1,
#             skills=[],
#             loot_table=[],
#             min_drop_count=None,
#             max_drop_count=None,
#             min_beans_reward=None,
#             max_beans_reward=None,
#             weighting=100,
#             initiative=10,
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
            min_dmg=3,
            max_dmg=6,
            skills=[DeezNuts()],
            loot_table=[BoxSeed, CatSeed, YellowSeed],
            initiative=5,
        )
