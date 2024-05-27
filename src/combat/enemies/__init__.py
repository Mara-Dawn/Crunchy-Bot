from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.skills import Bonk, DeezNuts
from items.types import ItemType

# class Example(Enemy):
#     def __init__(self):
#         super().__init__(
#             name="Example Enemy",
#             type=EnemyType.EXAMPLE,
#             description="Example description",
#             information="Example information",
#             image="image.png",
#             min_level=1,
#             max_level=1,
#             min_hp=90,
#             max_hp=110,
#             min_dmg=1,
#             max_dmg=1,
#             skills=[],
#             loot_table=[],
#             min_gear_drop_count=None,
#             max_gear_drop_count=None,
#             min_beans_reward=None,
#             max_beans_reward=None,
#             weighting=100,
#             initiative=10,
#             attribute_overrides=[],
#             actions_per_turn=1,
#         )


class MindGoblin(Enemy):
    def __init__(self):
        super().__init__(
            name="Mind Goblin",
            type=EnemyType.MIND_GOBLIN,
            description="Comes with a big sack of nuts.",
            information="Mind goblin' deez nuts?",
            image="mind_goblin.png",
            min_level=1,
            max_level=3,
            # min_hp=1,
            # max_hp=2,
            min_hp=130,
            max_hp=170,
            min_dmg=16,
            max_dmg=25,
            skills=[DeezNuts(), Bonk()],
            loot_table=[ItemType.BOX_SEED, ItemType.CAT_SEED, ItemType.YELLOW_SEED],
            initiative=5,
            actions_per_turn=1,
        )
