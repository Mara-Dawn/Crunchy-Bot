from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.gear.types import CharacterAttribute, GearBaseType
from combat.skills.types import SkillType
from config import Config
from items.types import ItemType

GENERAL_LOOT = [
    ItemType.SPEED_SEED,
    ItemType.CAT_SEED,
    ItemType.YELLOW_SEED,
    ItemType.BAKED_SEED,
    ItemType.BOX_SEED,
    ItemType.KEY_SEED,
    ItemType.CHEST_BEANS,
]

RARE_LOOT = [
    ItemType.RARE_SEED,
    ItemType.CRYSTAL_SEED,
    ItemType.GHOST_SEED,
    ItemType.FLASH_SEED,
]


class BoobaSlime(Enemy):
    def __init__(self):
        super().__init__(
            name="Booba Slime",
            type=EnemyType.BOOBA_SLIME,
            description="Even thought it looks munchable, you probably shouldn't",
            information="",
            image_url="https://i.imgur.com/f1cMvsr.jpeg",
            min_level=1,
            max_level=1,
            health=3,
            damage_scaling=4,
            min_gear_drop_count=1,
            max_gear_drop_count=1,
            max_players=5,
            skill_types=[SkillType.MILK_SHOWER],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=8,
            actions_per_turn=1,
            author="Klee",
        )


class GarlicDog(Enemy):
    def __init__(self):
        super().__init__(
            name="Garlic Dog",
            type=EnemyType.GARLIC_DOG,
            description="He has garlic on top of its head.",
            information="Good Boi",
            image_url="https://i.imgur.com/lTysGqh.png",
            min_level=1,
            max_level=2,
            health=8 * (1 - Config.BLIND_MISS_CHANCE),
            damage_scaling=8,
            max_players=4,
            skill_types=[SkillType.GARLIC_BREATH],
            item_loot_table=RARE_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            min_gear_drop_count=3,
            max_gear_drop_count=4,
            initiative=18,
            actions_per_turn=1,
            author="Lusa",
        )


class MindGoblin(Enemy):
    def __init__(self):
        super().__init__(
            name="Mind Goblin",
            type=EnemyType.MIND_GOBLIN,
            description="Comes with a big sack of nuts.",
            information="Has tickets to SawCon.",
            image_url="https://i.imgur.com/IrZjelg.png",
            min_level=1,
            max_level=3,
            health=3.5,
            damage_scaling=3.5,
            max_players=4,
            skill_types=[SkillType.DEEZ_NUTS, SkillType.BONK],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[GearBaseType.DEEZ_NUTS],
            skill_loot_table=[],
            initiative=9,
            actions_per_turn=1,
        )


class Table(Enemy):
    def __init__(self):
        super().__init__(
            name="Table",
            type=EnemyType.TABLE,
            description="A plain, white table with four legs.",
            information="Watch your toes!",
            image_url="https://i.imgur.com/ryWhWTP.png",
            min_level=1,
            max_level=3,
            health=4,
            damage_scaling=4.5,
            max_players=3,
            skill_types=[SkillType.TOE_STUB, SkillType.LOOKING_GOOD],
            item_loot_table=GENERAL_LOOT,
            attribute_overrides={CharacterAttribute.CRIT_RATE: 0.03},
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=20,
            actions_per_turn=1,
        )


class Goose(Enemy):
    def __init__(self):
        super().__init__(
            name="Park Goose",
            type=EnemyType.GOOSE,
            description="A motherfucking goose saw you.",
            information="",
            image_url="https://i.imgur.com/YgIkwmT.png",
            min_level=1,
            max_level=5,
            health=6,
            damage_scaling=6.5,
            max_players=4,
            skill_types=[SkillType.BIG_HONK, SkillType.ASS_BITE],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=16,
            actions_per_turn=1,
            author="Lusa",
        )


class ShoppingCart(Enemy):
    def __init__(self):
        super().__init__(
            name="Shopping Cart",
            type=EnemyType.SHOPPING_CART,
            description="Luckily not pushed by a child.",
            information="",
            image_url="https://i.imgur.com/xzy3C3q.jpeg",
            min_level=2,
            max_level=4,
            health=4,
            damage_scaling=3,
            max_players=3,
            skill_types=[SkillType.ANKLE_AIM, SkillType.DOWN_HILL],
            item_loot_table=GENERAL_LOOT,
            # min_gear_drop_count=2,
            # max_gear_drop_count=3,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=13,
            actions_per_turn=1,
            author="Klee",
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
            max_level=4,
            health=5,
            damage_scaling=4.5,
            max_players=5,
            skill_types=[SkillType.M_LADY, SkillType.FEDORA_TIP],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=13,
            actions_per_turn=1,
        )


class YourMom(Enemy):
    def __init__(self):
        super().__init__(
            name="Your Mom",
            type=EnemyType.YOUR_MOM,
            description="The Earth turns dark. Your mom appeared.",
            information="",
            image_url="https://i.imgur.com/71ztyhZ.png",
            min_level=2,
            max_level=3,
            health=10,
            damage_scaling=9,
            max_players=8,
            skill_types=[SkillType.AROUND_THE_WORLD, SkillType.SIT],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            min_gear_drop_count=4,
            max_gear_drop_count=5,
            initiative=10,
            actions_per_turn=1,
            author="Lusa",
        )


class CatDog(Enemy):
    def __init__(self):
        super().__init__(
            name="Cat-Dog",
            type=EnemyType.CAT_DOG,
            description="What is it? How was it born? Why doesn’t it look cute?",
            information="",
            image_url="https://i.imgur.com/c8yRpIk.png",
            min_level=2,
            max_level=5,
            health=5,
            damage_scaling=4.5,
            max_players=5,
            skill_types=[SkillType.PUKE, SkillType.TAIL_WHIP],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=13,
            actions_per_turn=2,
            author="Klee",
        )


class Mushroom(Enemy):
    def __init__(self):
        super().__init__(
            name="Happy Mushroom",
            type=EnemyType.MUSHROOM,
            description="He looks like he is about to BURST from happiness.",
            information="Seriously guys im kinda scared.",
            image_url="https://i.imgur.com/4S5sYFg.png",
            min_level=3,
            max_level=5,
            health=6,
            damage_scaling=0.1,
            max_players=5,
            skill_types=[SkillType.HOLD, SkillType.BURST],
            item_loot_table=GENERAL_LOOT,
            min_gear_drop_count=3,
            max_gear_drop_count=5,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=17,
            actions_per_turn=1,
            author="Lusa",
        )


class Scribbler(Enemy):
    def __init__(self):
        super().__init__(
            name="Scribbler",
            type=EnemyType.SCRIBBLER,
            description=(
                "It can appear in many shapes and forms. Nobody knows where it came from or what it wants."
                " It is extremely agressive, dangerous, and should be approached with caution."
            ),
            information="Dont say I didnt warn ya.",
            image_url="",
            min_level=2,
            max_level=7,
            health=7,
            damage_scaling=3.5,
            max_players=5,
            skill_types=[SkillType.ERASE, SkillType.EYE_POKE, SkillType.PAPER_CUTS],
            item_loot_table=RARE_LOOT + [ItemType.CRAPPY_COUPON],
            min_gear_drop_count=5,
            max_gear_drop_count=6,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=25,
            actions_per_turn=2,
            author="Lusa",
        )


class BroColi(Enemy):
    def __init__(self):
        super().__init__(
            name="BRO-Coli",
            type=EnemyType.BROCOLI,
            description="It is just a simple broccoli, enjoying his vacation with charming smile.",
            information="",
            image_url="https://i.imgur.com/k61s4go.png",
            min_level=3,
            max_level=8,
            health=6,
            damage_scaling=6,
            max_players=4,
            skill_types=[
                SkillType.EXERCISE,
                SkillType.BRO_ARROW,
                SkillType.BRO_FART,
                SkillType.BRO_EXTRA_FART,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=15,
            actions_per_turn=2,
            author="Franny",
        )


class Pimple(Enemy):
    def __init__(self):
        super().__init__(
            name="Pimple",
            type=EnemyType.PIMPLE,
            description="You wake up, take a look in the mirror and see it. A massive, blistering pimple right on your nose.",
            information="Comes with an irresistable urge to pop it.",
            image_url="https://i.imgur.com/IVDyooR.png",
            min_level=3,
            max_level=4,
            health=6,
            damage_scaling=4,
            max_players=5,
            skill_types=[SkillType.IT_HURTS, SkillType.POP],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=10,
            actions_per_turn=2,
            author="Lusa",
        )


class DFTank(Enemy):
    def __init__(self):
        super().__init__(
            name="DF Tank",
            type=EnemyType.DF_TANK,
            description="Looks like we arent getting out of this dungeon anytime soon. Contrary to what the tooltips might say, he mainly deals emotional damage.",
            information="If you don't manage to finish him off when hes on low health he will ragequit!",
            image_url="https://i.imgur.com/uw91SSy.png",
            min_level=2,
            max_level=4,
            health=6,
            damage_scaling=5,
            max_players=3,
            skill_types=[
                SkillType.STANCE_OFF,
                SkillType.YPYT,
                SkillType.DEAD_TANK,
            ],
            item_loot_table=RARE_LOOT,
            min_gear_drop_count=4,
            max_gear_drop_count=5,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=15,
            actions_per_turn=1,
            author="Lusa",
        )


class SchoolBully(Enemy):
    def __init__(self):
        super().__init__(
            name="School Bully",
            type=EnemyType.SCHOOL_BULLY,
            description="Loot at this little douche bag. Dont you just wanna punch his face? (Hes talking about you.)",
            information="",
            image_url="https://i.imgur.com/DWqm3oz.png",
            # min_level=6,
            min_level=7,
            max_level=9,
            health=6,
            damage_scaling=5.5,
            max_players=5,
            skill_types=[
                SkillType.WEDGIE,
                SkillType.KNEE_KICK,
                SkillType.HA_HA,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=16,
            actions_per_turn=2,
            author="Lusa",
        )


class Cuddles(Enemy):
    def __init__(self):
        super().__init__(
            name="Cuddles",
            type=EnemyType.CUDDLES,
            description="You abandoned it and now it is haunting you forever. It will never forgive and it will never forget. It feasts on your fear.",
            information="",
            image_url="https://i.imgur.com/YvZD72W.png",
            min_level=4,
            max_level=7,
            health=7,
            damage_scaling=6,
            max_players=4,
            skill_types=[
                SkillType.FEAR,
                SkillType.FEASTING,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=15,
            actions_per_turn=1,
            author="Lusa",
        )


class Eli(Enemy):
    def __init__(self):
        super().__init__(
            name="Eli",
            type=EnemyType.ELI,
            description="You're in awe of his size. Give him food or face destruction! (He will destroy you either way)",
            information="MRROWWWWW",
            image_url="https://i.imgur.com/AHKl27r.png",
            min_level=4,
            max_level=8,
            health=9,
            damage_scaling=7.5,
            max_players=7,
            skill_types=[
                SkillType.FAT_ASS,
                SkillType.OH_LAWD_HE_COMIN,
                SkillType.CAT_SCREECH,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            min_gear_drop_count=5,
            max_gear_drop_count=6,
            initiative=10,
            actions_per_turn=2,
            author="Lusa",
        )


class HomelessWoman(Enemy):
    def __init__(self):
        super().__init__(
            name="Homeless Woman",
            type=EnemyType.HOMELESS_WOMAN,
            description="Got some spare change? *cough* *cough*",
            information="",
            image_url="https://i.imgur.com/iSskEb5.png",
            min_level=4,
            max_level=8,
            health=4,
            damage_scaling=4,
            max_players=4,
            skill_types=[
                SkillType.HOMELESS_BEGGING,
                SkillType.HOMELESS_PLEADING,
            ],
            item_loot_table=[],
            gear_loot_table=[GearBaseType.USELESS_AMULET],
            skill_loot_table=[],
            min_gear_drop_count=1,
            max_gear_drop_count=1,
            initiative=3,
            actions_per_turn=1,
            random_loot=False,
            author="Lusa",
        )


class Crackachu(Enemy):
    def __init__(self):
        super().__init__(
            name="Crackachu",
            type=EnemyType.CRACKACHU,
            description="A messed up creature that needs its beans. NOW!",
            information="",
            image_url="https://i.imgur.com/MNVKt2D.png",
            min_level=5,
            max_level=8,
            health=5,
            damage_scaling=4.5,
            max_players=4,
            skill_types=[
                SkillType.THUNDER_CRACK,
                SkillType.USED_NEEDLES,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=25,
            actions_per_turn=2,
            author="Lusa",
        )


class Mommy(Enemy):
    def __init__(self):
        super().__init__(
            name="Mommy",
            type=EnemyType.MOMMY,
            description="She is big. She is hot. She is undead. She wants to step on you.",
            information="Looks surprisingly similar to Lady Dimitrescu.",
            image_url="https://i.imgur.com/1orHFL2.png",
            min_level=5,
            max_level=9,
            health=8,
            damage_scaling=5.5,
            max_players=6,
            skill_types=[
                SkillType.TIME_TO_SLICE,
                SkillType.STEP_ON_YOU,
                SkillType.CHOKE,
            ],
            item_loot_table=RARE_LOOT,
            gear_loot_table=[],
            min_gear_drop_count=6,
            max_gear_drop_count=7,
            skill_loot_table=[],
            initiative=20,
            actions_per_turn=2,
            author="Lusa",
        )


class Hoe(Enemy):
    def __init__(self):
        super().__init__(
            name="Hoe",
            type=EnemyType.HOE,
            description="Your mom from a different timeline.",
            information="",
            image_url="https://i.imgur.com/mxVJh0i.png",
            min_level=5,
            max_level=9,
            health=7,
            damage_scaling=5.5,
            max_players=5,
            skill_types=[
                SkillType.HOE_SHANK,
                SkillType.HOE_KNEES,
                SkillType.HOE_SPREAD,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=20,
            actions_per_turn=2,
            author="Lusa",
        )


class Mimic(Enemy):
    def __init__(self):
        super().__init__(
            name="Mimic",
            type=EnemyType.MIMIC,
            description="Sike, you got got! Better bring out the big guns or you'll get eaten alive.",
            information="",
            image_url="https://i.imgur.com/1Pip7BT.png",
            min_level=4,
            max_level=9,
            health=10,
            damage_scaling=5,
            max_players=1,
            skill_types=[
                SkillType.DEVOUR,
                SkillType.LOOT_SPIT,
            ],
            item_loot_table=RARE_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            min_gear_drop_count=6,
            max_gear_drop_count=7,
            initiative=20,
            actions_per_turn=2,
            author="Lusa",
        )


class Bonterry(Enemy):
    def __init__(self):
        super().__init__(
            name="Bonterry",
            type=EnemyType.BONTERRY,
            description=(
                "It was said that it once was a human, who tricked the Devil into not taking their soul. "
                "After death, they became a mindless monster with nowhere to go, following a flame from the underworld."
            ),
            information="",
            image_url="https://i.imgur.com/MDnqn2A.png",
            min_level=5,
            max_level=9,
            health=5,
            damage_scaling=3,
            max_players=4,
            skill_types=[
                SkillType.CHEFS_KNIFE,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=5,
            actions_per_turn=1,
            author="Lusa",
        )


class BonterryKing(Enemy):
    def __init__(self):
        super().__init__(
            name="Bonterry King",
            type=EnemyType.BONTERRY_KING,
            description=(
                "The king is seeking revenge for his fallen friends. "
                "He is the largest of his specimen."
            ),
            information="",
            image_url="https://i.imgur.com/F8Cxo0R.png",
            min_level=5,
            max_level=9,
            health=10,
            damage_scaling=6.5,
            max_players=5,
            skill_types=[
                SkillType.CHEFS_KNIFE,
                SkillType.KARMA,
                SkillType.GLOOM,
            ],
            item_loot_table=RARE_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            min_gear_drop_count=5,
            max_gear_drop_count=6,
            initiative=25,
            weighting=10,
            actions_per_turn=1,
            author="Lusa",
        )


class Fairy(Enemy):
    def __init__(self):
        super().__init__(
            name="Fairy",
            type=EnemyType.FAIRY,
            description=(
                "A fairy appears in front of you! She looks very nice, maybe she will grant you a wish."
            ),
            information="",
            image_url="https://i.imgur.com/OVhMx6V.png",
            # min_level=6,
            min_level=7,
            max_level=9,
            health=7,
            damage_scaling=6,
            max_players=4,
            skill_types=[
                SkillType.SPARKLES,
                SkillType.GET_FROGGED,
                SkillType.WHISPERING,
                SkillType.FOLLOW_ME,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            min_gear_drop_count=5,
            max_gear_drop_count=6,
            initiative=25,
            actions_per_turn=1,
            author="Lusa",
        )


class Boomer(Enemy):
    def __init__(self):
        super().__init__(
            name="The Boomer",
            type=EnemyType.BOOMER,
            description=("A powerful aura of technological ineptitude fills the room."),
            information="",
            image_url="https://i.imgur.com/bPKSVcp.png",
            min_level=3,
            max_level=7,
            health=7,
            damage_scaling=5,
            max_players=5,
            skill_types=[
                SkillType.BACK_IN_MY_DAYS,
                SkillType.OUTDATED_ADVICE,
                SkillType.NOSTALGIA_BOMB,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=15,
            actions_per_turn=1,
            author="Kiwi",
        )


class SausageButcher(Enemy):
    def __init__(self):
        super().__init__(
            name="Sausage Butcher",
            type=EnemyType.SAUSAGE_BUTCHER,
            description=("For some reason, all he's selling is sausages."),
            information="",
            image_url="https://i.imgur.com/js3YqhU.png",
            min_level=3,
            max_level=6,
            health=5,
            damage_scaling=5,
            max_players=5,
            skill_types=[
                SkillType.BIG_SALAMI,
                SkillType.WIENER_BOMB,
                SkillType.BRATWURST_BREAK,
            ],
            item_loot_table=RARE_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            min_gear_drop_count=4,
            max_gear_drop_count=5,
            initiative=20,
            actions_per_turn=1,
            author="Waldheld",
        )


class MangoTheCat(Enemy):
    def __init__(self):
        super().__init__(
            name="Mango the Cat",
            type=EnemyType.MANGO_THE_CAT,
            description=("A small, cute, grey, fluffy Cat."),
            information="",
            image_url="https://i.imgur.com/BazMNtB.jpeg",
            min_level=4,
            max_level=6,
            health=6,
            damage_scaling=6,
            max_players=5,
            skill_types=[
                SkillType.FURRY_HUG,
                SkillType.ROUGH_LOVE,
                SkillType.NO_THANK_YOU,
            ],
            item_loot_table=GENERAL_LOOT,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=35,
            actions_per_turn=1,
            author="Feye",
        )


# Bosses


class Daddy_P1(Enemy):
    def __init__(self):
        super().__init__(
            name="Daddy",
            type=EnemyType.DADDY_P1,
            controller="DaddyController",
            description="Meet Daddy, whose commanding presence and smirk promise both discipline and the world's best bedtime stories.",
            information="Defeat this boss to unlock access to level 4 and above.",
            image_url="https://i.imgur.com/zGrKHqj.png",
            min_level=3,
            max_level=3,
            health=7.3,
            damage_scaling=12,
            max_players=6,
            min_encounter_scale=6,
            skill_types=[
                SkillType.WHIP,
                SkillType.HAIR_PULL,
                SkillType.BELT,
                SkillType.BUTT_SLAP,
            ],
            item_loot_table=RARE_LOOT,
            bonus_loot_chance=1,
            min_gear_drop_count=7,
            max_gear_drop_count=8,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=40,
            actions_per_turn=2,
            is_boss=True,
            fixed_avg_potency=3.32,
            phases=[EnemyType.DADDY_P1, EnemyType.DADDY_P2],
            author="Lusa, Mara",
        )


class Daddy_P2(Enemy):
    def __init__(self):
        super().__init__(
            name="Daddy",
            type=EnemyType.DADDY_P2,
            controller="DaddyController",
            description="Bruised but unyielding, Daddy's fierce gaze and electrifying smirk promise a relentless, heart-pounding continuation of your tantalizing game.",
            information="Defeat this boss to unlock access to level 4 and above.",
            image_url="https://i.imgur.com/UqbImuS.png",
            min_level=3,
            max_level=3,
            health=7,
            damage_scaling=12,
            max_players=6,
            min_encounter_scale=6,
            skill_types=[
                SkillType.WHIP,
                SkillType.HAIR_PULL,
                SkillType.BELT,
                SkillType.BUTT_SLAP,
                SkillType.TIE_YOU_UP,
                SkillType.ON_YOUR_KNEES,
            ],
            item_loot_table=RARE_LOOT,
            bonus_loot_chance=1,
            min_gear_drop_count=7,
            max_gear_drop_count=8,
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=45,
            actions_per_turn=3,
            fixed_avg_potency=4.28,
            is_boss=True,
            phases=[EnemyType.DADDY_P1, EnemyType.DADDY_P2],
            author="Lusa, Mara",
        )


class WeebBall(Enemy):
    def __init__(self):
        super().__init__(
            name="Mysterious Ball",
            type=EnemyType.WEEB_BALL,
            controller="WeebController",
            description=(
                "Ooo ho ho, what is this? A great sealing object from a time long past..."
            ),
            information="May or may not have something to do with the level 6 boss.",
            image_url="https://i.imgur.com/VAtRjZK.png",
            min_level=6,
            max_level=6,
            health=7.5,
            damage_scaling=14,
            max_players=6,
            min_encounter_scale=6,
            skill_types=[
                SkillType.OMAE_WA,
                SkillType.DAKIMAKURA,
                SkillType.WEEB_KAWAII,
                SkillType.WEEB_SPLAINING,
                SkillType.ALCHEMY,
                SkillType.POTATO_CHIP,
            ],
            item_loot_table=[],
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=9999,
            is_boss=True,
            fixed_avg_potency=2.4,
            phases=[
                EnemyType.WEEB_BALL,
                EnemyType.WEEB_P1,
                EnemyType.WEEB_P2,
                EnemyType.WEEB_P3,
            ],
            author="Lusa, Sophie, Mara",
        )


class Weeb_P1(Enemy):
    def __init__(self):
        super().__init__(
            name="Weeb",
            type=EnemyType.WEEB_P1,
            controller="WeebController",
            description="He has the power of God and Anime on his side.",
            information="Defeat this boss to unlock access to level 7 and above.",
            image_url="https://i.imgur.com/kauVRZ7.png",
            min_level=6,
            max_level=6,
            health=7.5,
            # health=0.001,
            damage_scaling=14,
            max_players=6,
            min_encounter_scale=6,
            skill_types=[
                SkillType.OMAE_WA,
                SkillType.DAKIMAKURA,
                SkillType.WEEB_KAWAII,
                SkillType.WEEB_SPLAINING,
                SkillType.ALCHEMY,
                SkillType.POTATO_CHIP,
            ],
            item_loot_table=[],
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=80,
            actions_per_turn=3,
            is_boss=True,
            fixed_avg_potency=4,
            phases=[
                EnemyType.WEEB_BALL,
                EnemyType.WEEB_P1,
                EnemyType.WEEB_P2,
                EnemyType.WEEB_P3,
            ],
            author="Lusa, Sophie, Mara",
        )


class Weeb_P2(Enemy):
    def __init__(self):
        super().__init__(
            name="Weeb Sayan",
            type=EnemyType.WEEB_P2,
            controller="WeebController",
            description="This isnt even my final form!",
            information="Defeat this boss to unlock access to level 7 and above.",
            image_url="https://i.imgur.com/NqBCRA1.png",
            min_level=6,
            max_level=6,
            health=5,
            # health=0.001,
            damage_scaling=10,
            max_players=6,
            min_encounter_scale=6,
            skill_types=[
                SkillType.WEEBI_HAME_HA,
                SkillType.WEEBI_DAMA_CHARGE_1,
                SkillType.WEEBI_DAMA_CHARGE_2,
                SkillType.WEEBI_DAMA_CHARGE_3,
                SkillType.WEEBI_DAMA,
            ],
            item_loot_table=[],
            gear_loot_table=[],
            skill_loot_table=[],
            initiative=20,
            actions_per_turn=1,
            is_boss=True,
            fixed_avg_potency=1.3,
            phases=[
                EnemyType.WEEB_BALL,
                EnemyType.WEEB_P1,
                EnemyType.WEEB_P2,
                EnemyType.WEEB_P3,
            ],
            author="Lusa, Sophie, Mara",
        )


class Weeb_P3(Enemy):
    def __init__(self):
        super().__init__(
            name="Magical Weeb Girl",
            type=EnemyType.WEEB_P3,
            controller="WeebController",
            description="Unlocking ones inner potential to pierce the heavens above.",
            information="Defeat this boss to unlock access to level 7 and above.",
            image_url="https://i.imgur.com/cm6h34f.png",
            min_level=6,
            max_level=6,
            health=7.5,
            # health=0.001,
            damage_scaling=14,
            max_players=6,
            min_encounter_scale=6,
            skill_types=[
                SkillType.MEOW_KISS,
                SkillType.MEOW_SPIRAL,
                SkillType.MEOW_TIARA,
            ],
            item_loot_table=[],
            min_gear_drop_count=7,
            max_gear_drop_count=8,
            gear_loot_table=[],
            skill_loot_table=[],
            phases=[
                EnemyType.WEEB_BALL,
                EnemyType.WEEB_P1,
                EnemyType.WEEB_P2,
                EnemyType.WEEB_P3,
            ],
            initiative=50,
            actions_per_turn=2,
            is_boss=True,
            fixed_avg_potency=6.4,
            author="Lusa, Sophie, Mara",
        )
