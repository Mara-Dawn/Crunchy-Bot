from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.skills.types import SkillType
from items.types import ItemType


class MindGoblin(Enemy):
    def __init__(self):
        super().__init__(
            name="Mind Goblin",
            type=EnemyType.MIND_GOBLIN,
            description="Comes with a big sack of nuts.",
            information="Has tickets to SawCon.",
            image_url="https://i.imgur.com/IrZjelg.png",
            min_level=2,
            max_level=3,
            health=3,
            damage_scaling=5,
            max_players=3,
            skill_types=[SkillType.DEEZ_NUTS, SkillType.BONK],
            item_loot_table=[
                ItemType.BOX_SEED,
                ItemType.CAT_SEED,
                ItemType.YELLOW_SEED,
            ],
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=11,
            actions_per_turn=1,
        )


class Table(Enemy):
    def __init__(self):
        super().__init__(
            name="Table",
            type=EnemyType.TABLE,
            description="A plain, white table with four legs.",
            information="Watch your toes!",
            image_url="",
            min_level=1,
            max_level=2,
            health=4,
            damage_scaling=5,
            max_players=4,
            skill_types=[SkillType.TOE_STUB, SkillType.LOOKING_GOOD],
            item_loot_table=[
                ItemType.SPEED_SEED,
                ItemType.RARE_SEED,
            ],
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=20,
            actions_per_turn=1,
        )


class NiceGuy(Enemy):
    def __init__(self):
        super().__init__(
            name="Nice Guy",
            type=EnemyType.NICE_GUY,
            description="Why do girls always fall for assholes? It's not fair!",
            information="No more Mr. Nice Guy!",
            image_url="https://i.imgur.com/M93ra6J.png",
            min_level=2,
            max_level=5,
            health=5,
            damage_scaling=5.5,
            max_players=5,
            skill_types=[SkillType.M_LADY, SkillType.FEDORA_TIP],
            item_loot_table=[
                ItemType.BOX_SEED,
                ItemType.CAT_SEED,
                ItemType.YELLOW_SEED,
            ],
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=13,
            actions_per_turn=1,
        )
