from datalayer.garden import (
    BakedBeanPlant,
    BeanPlant,
    BoxBeanPlant,
    CatBeanPlant,
    CrystalBeanPlant,
    FlashBeanPlant,
    GhostBeanPlant,
    KeyBeanPlant,
    RareBeanPlant,
    SpeedBeanPlant,
    YellowBeanPlant,
)
from datalayer.lootbox import LootBox
from datalayer.types import ItemTrigger, PlantType
from items.item import Item
from items.types import ItemGroup, ItemType, ShopCategory


class Arrest(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Citizens Arrest",
            type=ItemType.ARREST,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="Take the law into your own hands and arrest a user of choice for 30 minutes.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🚨",
            cost=cost,
            value=None,
            view_class="ShopUserSelectView",
        )


class AutoCrit(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Magic Beans",
            type=ItemType.AUTO_CRIT,
            group=ItemGroup.AUTO_CRIT,
            shop_category=ShopCategory.INTERACTION,
            description="Let these rainbow colored little beans guide your next slap, pet or fart to a guaranteed critical hit.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="💥",
            cost=cost,
            value=True,
            trigger=[ItemTrigger.FART, ItemTrigger.PET, ItemTrigger.SLAP],
            controllable=True,
        )


class Bailout(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bribe the Mods",
            type=ItemType.BAILOUT,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="Pay off the mods with beans to let you out of jail early.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🗿",
            cost=cost,
            value=None,
            view_class="ShopConfirmView",
        )


class Bat(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1337

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Baseball Bat",
            type=ItemType.BAT,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.INTERACTION,
            description="Sneak up on someone and knock them out for 20 minutes, making them unable to use and buy items or gamba their beans.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="💫",
            cost=cost,
            value=20,
            view_class="ShopUserSelectView",
        )


class BonusFart(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bonus Fart",
            type=ItemType.BONUS_FART,
            group=ItemGroup.BONUS_ATTEMPT,
            shop_category=ShopCategory.FART,
            description="Allows you to continue farting on a jailed person after using your guaranteed one.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="😂",
            cost=cost,
            value=True,
            trigger=[ItemTrigger.FART],
            weight=150,
            controllable=True,
        )


class BonusPet(Item):

    def __init__(self, cost: int | None):
        defaultcost = 35

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bonus Pet",
            type=ItemType.BONUS_PET,
            group=ItemGroup.BONUS_ATTEMPT,
            shop_category=ShopCategory.PET,
            description="Allows you to continue giving pets to a jailed person after using your guaranteed one.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🥰",
            cost=cost,
            value=True,
            trigger=[ItemTrigger.PET],
            weight=150,
            controllable=True,
        )


class UltraPet(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="The Most Gentle Pet Ever",
            type=ItemType.ULTRA_PET,
            group=ItemGroup.MAJOR_JAIL_ACTION,
            shop_category=ShopCategory.PET,
            description="You feel a weird tingle in your hand, almost as if the next person to recieve your pets will be instantly freed from jail.",
            information="Available as a rare drop from lootboxes.",
            emoji="😳",
            cost=cost,
            value=True,
            trigger=[ItemTrigger.PET],
            hide_in_shop=True,
            controllable=True,
        )


class PenetratingPet(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Gamer Hands Pet",
            type=ItemType.PENETRATING_PET,
            group=ItemGroup.MAJOR_JAIL_ACTION,
            shop_category=ShopCategory.PET,
            description="Years of hardcore sweaty gaming, dorito dust and a lack of hygiene turned your hands into incredibly effective weapons. Your next pet instantly dissolves any protection the target might have had.",
            information="Available as a rare drop from lootboxes.",
            emoji="🎮",
            cost=cost,
            value=True,
            trigger=[ItemTrigger.PET],
            hide_in_shop=True,
            controllable=True,
        )


class BonusSlap(Item):

    def __init__(self, cost: int | None):
        defaultcost = 35

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bonus Slap",
            type=ItemType.BONUS_SLAP,
            group=ItemGroup.BONUS_ATTEMPT,
            shop_category=ShopCategory.SLAP,
            description="Allows you to continue slapping a jailed person after using your guaranteed one.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="✋",
            cost=cost,
            value=True,
            trigger=[ItemTrigger.SLAP],
            weight=150,
            controllable=True,
        )


class SwapSlap(Item):

    def __init__(self, cost: int | None):
        defaultcost = 4000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="No U",
            type=ItemType.SWAP_SLAP,
            group=ItemGroup.MAJOR_ACTION,
            shop_category=ShopCategory.SLAP,
            description="Limited edition uno reverse card. If you are jailed, your next slap against a non jailed user will make them trade places with you.",
            information="Available as a rare drop from lootboxes.",
            emoji="🔁",
            cost=cost,
            value=None,
            trigger=[ItemTrigger.SLAP],
            hide_in_shop=True,
            controllable=True,
        )


class UltraSlap(Item):

    def __init__(self, cost: int | None):
        defaultcost = 3000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Infinity and Beyond Glove",
            type=ItemType.ULTRA_SLAP,
            group=ItemGroup.MAJOR_ACTION,
            shop_category=ShopCategory.SLAP,
            description="This glove will slap people into another dimension, completely annihilating them and erasing their existence. Your next slap will stun your target for 5 hours.",
            information="Available as a rare drop from lootboxes.",
            emoji="🥊",
            cost=cost,
            value=60 * 5,
            trigger=[ItemTrigger.SLAP],
            hide_in_shop=True,
            controllable=True,
        )


class ExplosiveFart(Item):

    def __init__(self, cost: int | None):
        defaultcost = 10000

        if cost is None:
            cost = defaultcost

        description = "You strayed too far from Gods guiding light and tasted the forbidden fruit you found behind grandmas fridge. "
        description += "Once released, the storm brewing inside you carries up to 5 random people directly to the shadow realm for 5-10 hours.\n"
        description += "(only affects people with more than 500 beans)"

        super().__init__(
            name="Explosive Diarrhea",
            type=ItemType.EXPLOSIVE_FART,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description=description,
            information="Available in the shop. Use /shop for more Information.\nYou can hit yourself with this item.",
            emoji="😨",
            cost=cost,
            value=1,
            view_class="ShopConfirmView",
            useable=True,
        )


class UltraFartBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Nuclear Lunch Codes",
            type=ItemType.ULTRA_FART_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.FART,
            description="You try to cook a nice lunch, but your cooking skills are so abysmal that the brave souls who 'agreed' to eat it have a near death experience. Powers up your next Fart by x50.",
            information="Available as a rare drop from lootboxes.",
            emoji="🤮",
            cost=cost,
            value=50,
            trigger=[ItemTrigger.FART],
            hide_in_shop=True,
            controllable=True,
        )


class FartBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 150

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="UK Breakfast Beans",
            type=ItemType.FART_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.FART,
            description="Extremely dangerous, multiplies the power of your next fart by 3.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="🤢",
            cost=cost,
            value=3,
            trigger=[ItemTrigger.FART],
            controllable=True,
        )


class FartProtection(Item):

    def __init__(self, cost: int | None):
        defaultcost = 175

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Your Uncle's old Hazmat Suit",
            type=ItemType.PROTECTION,
            group=ItemGroup.PROTECTION,
            shop_category=ShopCategory.INTERACTION,
            description="According to him his grandpa took it from a dead guy in ww2. The next 5 interactions negatively affecting your jailtime will be reduced by 50%",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="☣",
            cost=cost,
            value=0.5,
            base_amount=5,
            max_amount=5,
            trigger=[ItemTrigger.FART, ItemTrigger.SLAP, ItemTrigger.MIMIC],
            controllable=True,
        )


class AdvancedFartProtection(FartProtection):

    def __init__(self, cost: int | None):
        defaultcost = 2500

        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.base_amount = 15
        self.max_amount = 30
        self.name = self.name + " x3"
        self.description = "A poor paranoid soul sewed 3 hazmat suits into one, making this one much stronger than what you would usually find in a store. (caps out at 25 stacks)"
        self.information = "Available as a rare drop from lootboxes."
        self.hide_in_shop = True


class FartStabilizer(Item):

    def __init__(self, cost: int | None):
        defaultcost = 45

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Ass ACOG",
            type=ItemType.FART_STABILIZER,
            group=ItemGroup.STABILIZER,
            shop_category=ShopCategory.FART,
            description="Stabilizes your aim and increases your rectal precision. Your next fart cannot roll below 0.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="🔭",
            cost=cost,
            value=10,
            trigger=[ItemTrigger.FART],
            controllable=True,
        )


class Fartvantage(Item):

    def __init__(self, cost: int | None):
        defaultcost = 69

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Fast Food Binge",
            type=ItemType.FARTVANTAGE,
            group=ItemGroup.ADVANTAGE,
            shop_category=ShopCategory.FART,
            description="Couldn't hold back again, hm? Better go empty your bowels on some poor loser. Rolls your next fart twice and takes the better result.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="🍔",
            cost=cost,
            value=2,
            trigger=[ItemTrigger.FART],
            controllable=True,
        )


class GigaFart(Item):

    def __init__(self, cost: int | None):
        defaultcost = 500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Shady 4am Chinese Takeout",
            type=ItemType.GIGA_FART,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.FART,
            description="Works better than any laxative and boosts the pressure of your next fart by x10. Try not to hurt yourself.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="💀",
            cost=cost,
            value=10,
            trigger=[ItemTrigger.FART],
            controllable=True,
        )


class JailReduction(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Gaslight the Guards",
            type=ItemType.JAIL_REDUCTION,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="Manipulate the mods into believing your jail sentence is actually 30 minutes shorter than it really is. (Cuts off at 30 minutes left)",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🥺",
            cost=cost,
            value=30,
            view_class="ShopConfirmView",
            allow_amount=True,
            base_amount=1,
        )


class LootBoxItem(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Random Treasure Chest",
            type=ItemType.LOOTBOX,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="No need to wait for loot box drops, just buy your own!",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🧰",
            cost=cost,
            value=None,
        )


class LootBoxItemBundle(Item):

    def __init__(self, cost: int | None):
        defaultcost = 500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Random Treasure Chest x5",
            type=ItemType.LOOTBOX_BUNDLE,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="Too addicted? Just buy 5 at once! All neatly contained within a single Box.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🧰",
            cost=cost,
            value=None,
            base_amount=5,
        )


class LootBoxItemBigBundle(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Random Treasure Chest x10",
            type=ItemType.LOOTBOX_BIG_BUNDLE,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="For when 5 at a time just isn't enough.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🧰",
            cost=cost,
            value=None,
            base_amount=10,
        )


class PocketMimic(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Pocket Mimic",
            type=ItemType.MIMIC,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="Use this item from your inventory to spawn a large mimic. It will look like a regular chest spawn to other people.",
            information="Available as a rare drop from lootboxes.",
            emoji="🧰",
            cost=cost,
            value=None,
            controllable=True,
            hide_in_shop=True,
            useable=True,
        )


class CatGirl(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Useless Cat Girl",
            type=ItemType.CATGIRL,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="She is lazy, sleepy, does nothing all day and apparently lives in your inventory now. :3",
            information="Available as a rare drop from lootboxes.",
            emoji="🐱",
            cost=cost,
            value=None,
            hide_in_shop=True,
            permanent=True,
        )


class CrappyDrawing(Item):

    def __init__(self, cost: int | None):
        defaultcost = 4000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Soggy Crumpled Up Coupon",
            type=ItemType.CRAPPY_COUPON,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description=(
                "Ow! Something hits your forehead and makes you flinch. You manage to catch it before it reaches the floor "
                "and you notice a suspiciously wet rolled up small paper ball. After unwrapping it, you can read its message: "
                "'Coupon for one shitty profile picture drawing from Lusa' (Use item in your inventory to redeem.)"
            ),
            information="Available as a rare drop from lootboxes.",
            emoji="🧻",
            cost=cost,
            value=None,
            hide_in_shop=True,
            useable=True,
        )


class LotteryTicket(Item):

    def __init__(self, cost: int | None):
        defaultcost = 150

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Lottery Ticket",
            type=ItemType.LOTTERY_TICKET,
            group=ItemGroup.LOTTERY,
            shop_category=ShopCategory.FUN,
            description="Enter the Weekly Bean Lottery and win big! Max 3 tickets per person.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🎫",
            cost=cost,
            value=1,
            max_amount=3,
        )


class NameColor(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Name Color Change",
            type=ItemType.NAME_COLOR,
            group=ItemGroup.SUBSCRIPTION,
            shop_category=ShopCategory.FUN,
            description="Paint your discord name in your favourite color! Grab one weeks worth of color tokens. Each day, a token gets consumed until you run out.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🌈",
            cost=cost,
            value=1,
            view_class="ShopColorSelectView",
            allow_amount=True,
            base_amount=7,
            trigger=[ItemTrigger.DAILY],
        )


class PetBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 120

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Big Mama Bear Hug",
            type=ItemType.PET_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.PET,
            description="When a normal pet just isnt enough. Powers up your next pet by 5x.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="🧸",
            cost=cost,
            value=5,
            trigger=[ItemTrigger.PET],
            controllable=True,
        )


class ReactionSpam(Item):

    def __init__(self, cost: int | None):
        defaultcost = 50

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bully for Hire",
            type=ItemType.REACTION_SPAM,
            group=ItemGroup.SUBSCRIPTION,
            shop_category=ShopCategory.FUN,
            description="Hire a personal bully to react to every single message of your victim with an emoji of your choice. One purchase amounts to 10 message reactions. Only one bully can be active at a time.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🤡",
            cost=cost,
            value=1,
            view_class="ShopReactionSelectView",
            allow_amount=True,
            base_amount=10,
            trigger=[ItemTrigger.USER_MESSAGE],
        )


class Release(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Get out of Jail Fart",
            type=ItemType.RELEASE,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="Due to dietary advancements your farts can now help a friend out of jail for one time only.",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🔑",
            cost=cost,
            value=None,
            view_class="ShopUserSelectView",
        )


class RouletteFart(Item):

    def __init__(self, cost: int | None):
        defaultcost = 500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Russian Roulette",
            type=ItemType.ROULETTE_FART,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="After a night of heavy drinking you decide to gamble on a fart to prank your friend. 50% chance to jail the target, 50% chance to shit yourself and go to jail instead. (30 minutes)",
            information="Available in the shop. Use /shop for more Information.",
            emoji="🔫",
            cost=cost,
            value=None,
            view_class="ShopUserSelectView",
        )


class SatanBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2345

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Satan's Nuclear Hellfart",
            type=ItemType.SATAN_FART,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.FART,
            description="A x25 fart boost that sends a jailed person to the shadow realm but with a high risk of the farter being caught in the blast. 75% chance to jail yourself too with the same duration.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="😈",
            cost=cost,
            value=25,
            trigger=[ItemTrigger.FART],
            controllable=True,
        )


class SlapBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 120

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Massive Bonking Hammer",
            type=ItemType.SLAP_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.SLAP,
            description="For when someone has been extra horny. Powers up your next slap by 5x.",
            information="Available from loot boxes and in the shop. Use /shop for more Information.",
            emoji="🔨",
            cost=cost,
            value=5,
            trigger=[ItemTrigger.SLAP],
            controllable=True,
        )


class NoLimitGamba(Item):

    def __init__(self, cost: int | None):
        defaultcost = 10500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Giga Gamba",
            type=ItemType.UNLIMITED_GAMBA,
            group=ItemGroup.GAMBA,
            shop_category=ShopCategory.FUN,
            description="This item increases the maximum amount of beans you can bet on your next gamba to 10.000. Good luck.",
            information="Available as a rare drop from lootboxes.",
            emoji="🎰",
            cost=cost,
            value=1,
            trigger=[ItemTrigger.GAMBA],
            controllable=True,
            hide_in_shop=True,
        )


class NoCooldownGamba(Item):

    def __init__(self, cost: int | None):
        defaultcost = 3500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Instant Gamba",
            type=ItemType.INSTANT_GAMBA,
            group=ItemGroup.GAMBA,
            shop_category=ShopCategory.FUN,
            description="Allows you to ignore the cooldown on your next gamba.",
            information="Available as a rare drop from lootboxes.",
            emoji="🎰",
            cost=cost,
            value=1,
            trigger=[ItemTrigger.GAMBA],
            controllable=True,
            hide_in_shop=True,
        )


class MimicDetector(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Useful Foxgirl",
            type=ItemType.MIMIC_DETECTOR,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description=(
                "Compared to her less than useful cat sisters, she is genuinely happy to help you out."
                " With her superior sense of smell she can identify mimics before you open them! "
                " She is super shy though so she will run away after helping you once."
            ),
            information="Available as a rare drop from lootboxes.\n This item was designed by Maya as part of her season 1 reward.",
            emoji="🦊",
            cost=cost,
            value=1,
            trigger=[ItemTrigger.MIMIC],
            controllable=True,
            hide_in_shop=True,
        )


class GhostBean(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Spooky Bean",
            type=ItemType.SPOOK_BEAN,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.GARDEN,
            description=(
                "This bean allows you to possess someone with a random ghost. "
                "The ghost will mess with their messages for a short while, "
                "however you have no control over which ghost it is. Possible outcomes: "
                "E-Girl, Priest, Alcoholic, Weeb, British, Cat, Nerd"
            ),
            information="Obtained when harvesting a Ghost Bean Plant from your garden.",
            emoji="👻",
            cost=cost,
            value=1,
            view_class="ShopUserSelectView",
            controllable=True,
            useable=True,
            hide_in_shop=True,
        )


# Combat Items


class Scrap(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Scrap",
            type=ItemType.SCRAP,
            group=ItemGroup.GEAR,
            shop_category=ShopCategory.GEAR,
            description=(
                "A hand full of old equipment shreds and pieces. "
                "Can be reforged into new equipment at the bean forge."
            ),
            information=(
                "Obtained when dismantling combat equipment. "
                "Can be used at the bean forge to get random items. "
                "use /equipment for more information."
            ),
            emoji="⚙️",
            cost=cost,
            value=1,
            view_class="ShopUserSelectView",
            hide_in_shop=True,
        )


class BaseKey(Item):

    BASE_COST = 1000
    LEVEL_COST = 200
    TYPE_MAP = {
        1: ItemType.ENCOUNTER_KEY_1,
        2: ItemType.ENCOUNTER_KEY_2,
        3: ItemType.ENCOUNTER_KEY_3,
        4: ItemType.ENCOUNTER_KEY_4,
        5: ItemType.ENCOUNTER_KEY_5,
        6: ItemType.ENCOUNTER_KEY_6,
    }

    def __init__(self, cost: int | None = None, level: int = 1):

        if cost is None:
            cost = self.BASE_COST + (level * self.LEVEL_COST)

        super().__init__(
            name=f"Level {level} Key",
            type=self.TYPE_MAP[level],
            group=ItemGroup.GEAR,
            shop_category=ShopCategory.GEAR,
            description=(
                "A magical key that allows you to open a portal to another dimension. "
                f"Inside you will face an enemy of the {level}th level.\n"
                "(Item can be used from your inventory. You will automatically join the spawned encounter.)"
            ),
            information=(f"Spawns a random encounter of the {level}th level. "),
            emoji="🔑",
            cost=cost,
            useable=True,
            value=1,
            hide_in_shop=True,
            secret=True,
        )


class KeyLvl1(BaseKey):

    def __init__(self, cost: int | None):
        super().__init__(level=1)


class KeyLvl2(BaseKey):

    def __init__(self, cost: int | None):
        super().__init__(level=2)


class KeyLvl3(BaseKey):

    def __init__(self, cost: int | None):
        super().__init__(level=3)


class KeyLvl4(BaseKey):

    def __init__(self, cost: int | None):
        super().__init__(level=4)


class KeyLvl5(BaseKey):

    def __init__(self, cost: int | None):
        super().__init__(level=5)


class KeyLvl6(BaseKey):

    def __init__(self, cost: int | None):
        super().__init__(level=6)


class DaddyKey(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Suspicious Key",
            type=ItemType.DADDY_KEY,
            group=ItemGroup.GEAR,
            shop_category=ShopCategory.GEAR,
            description=(
                "This key looks rather normal, but you feel a strong commanding magic radiating from it. "
                "When used from your inventory, it will open a path to the lvl. 3 Boss.\n"
                "You will need 6 players to face this challenge.\n"
                "Come prepared, this key only grants you a single attempt."
                " Set aside sufficient time for this encounter, it might take a while."
            ),
            information=(
                "Boss Key to spawn the lvl.3 boss encounter.\n"
                "6-9 players\n"
                "Unlocks the 4th level."
            ),
            emoji="🔑",
            cost=cost,
            useable=True,
            value=1,
            hide_in_shop=True,
            secret=True,
            permanent=True,
            image_url="https://i.imgur.com/QqrB4OS.png",
        )


class WeebKey(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Master Ball",
            type=ItemType.WEEB_KEY,
            group=ItemGroup.GEAR,
            shop_category=ShopCategory.GEAR,
            description=(
                "Woah is this one of those super rare master balls? Hmm interesting, the label "
                "looks like it was printed upside down. Did it just move !? What could be hiding inside?\n\n"
                "When used from your inventory, it will open a path to the lvl. 6 Boss.\n\n"
                "You will need 6 players to face this challenge.\n"
                "Come prepared, this key only grants you a single attempt."
                " Set aside sufficient time for this encounter, it might take a while."
            ),
            information=(
                "Boss Key to spawn the lvl.6 boss encounter.\n"
                "6-9 players\n"
                "Unlocks the 7th level."
            ),
            emoji="🔑",
            cost=cost,
            useable=True,
            value=1,
            hide_in_shop=True,
            secret=True,
            permanent=True,
            image_url="https://i.imgur.com/VAtRjZK.png",
        )


# Debuffs
class Debuff(Item):

    DEBUFF_DURATION = 5
    DEBUFF_BAKED_DURATION = 1

    DEBUFFS = [
        ItemType.EGIRL_DEBUFF,
        ItemType.RELIGION_DEBUFF,
        # ItemType.ALCOHOL_DEBUFF,
        ItemType.WEEB_DEBUFF,
        ItemType.BRIT_DEBUFF,
        ItemType.MEOW_DEBUFF,
        ItemType.NERD_DEBUFF,
        ItemType.MACHO_DEBUFF,
        # ItemType.TRUMP_DEBUFF,
    ]

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="",
            type=None,
            group=ItemGroup.DEBUFF,
            shop_category=ShopCategory.GARDEN,
            description="",
            information="",
            emoji="",
            cost=cost,
            value=1,
            trigger=[ItemTrigger.USER_MESSAGE],
            hide_in_shop=True,
        )


class HighAsFrick(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "Blazed out of your Mind"
        self.type = ItemType.HIGH_AS_FRICK
        self.description = (
            "You got high of your own supply and must now suffer the conseqences. "
        )
        self.information = (
            "You gain this debuff after harvesting the Baked Beans plant. "
            "Your next few messages will become stoner talk instead."
        )
        self.emoji = "💨"


class UwUfy(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "Rawr xD omgoshiess *sparkles* ^-^"
        self.type = ItemType.EGIRL_DEBUFF
        self.description = (
            "You were possessed by a super random egirl teenager from 2010. "
            "You feel a desperate need for attention and just cant hold back all the uwu."
            "(We take no responsibility for whatever happens while possessed) "
        )
        self.information = (
            "You gain this debuff when someone uses a ghost bean on you. "
            "Your next few messages will become uwu egirl talk."
        )
        self.emoji = "💞"


class Religify(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "Praise the Lord!"
        self.type = ItemType.RELIGION_DEBUFF
        self.description = (
            "You were possessed by a religious fanatic. "
            "You feel a desperate need to judge everyone harshly for their impureness. "
            "(We take no responsibility for whatever happens while possessed) "
        )
        self.information = (
            "You gain this debuff when someone uses a ghost bean on you. "
            "Your next few messages will become religious fanatic talk."
        )
        self.emoji = "⛪"


class Alcoholify(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "BUUUURP *Hic*"
        self.type = ItemType.ALCOHOL_DEBUFF
        self.description = (
            "You were possessed by a raging alcoholic. "
            "You feel a desperate need to yell at people and slur your words. "
            "(We take no responsibility for whatever happens while possessed) "
        )
        self.information = (
            "You gain this debuff when someone uses a ghost bean on you. "
            "Your next few messages will become alcoholic talk."
        )
        self.emoji = "🍺"


class Weebify(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "Kawaii Desu"
        self.type = ItemType.WEEB_DEBUFF
        self.description = (
            "You were possessed by a shut in weeb. "
            "You feel a desperate need to make anime references and speak japanese. "
            "(We take no responsibility for whatever happens while possessed) "
        )
        self.information = (
            "You gain this debuff when someone uses a ghost bean on you. "
            "Your next few messages will become weeb talk."
        )
        self.emoji = "🗾"


class Britify(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "Bri'ish Debuff"
        self.type = ItemType.BRIT_DEBUFF
        self.description = (
            "You were possessed by an old british person. "
            "You feel a desperate need to speak in ye olde english. "
            "(We take no responsibility for whatever happens while possessed) "
        )
        self.information = (
            "You gain this debuff when someone uses a ghost bean on you. "
            "Your next few messages will become brit talk."
        )
        self.emoji = "😩"


class Meowify(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "Nyaaaa :3"
        self.type = ItemType.MEOW_DEBUFF
        self.description = (
            "You were possessed by a Cat. "
            "You feel a desperate need to meow meow meow mrrrrp. "
            "(We take no responsibility for whatever happens while possessed) "
        )
        self.information = (
            "You gain this debuff when someone uses a ghost bean on you. "
            "Your next few messages will become cat talk."
        )
        self.emoji = "😸"


class Nerdify(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "Uhm Actually.."
        self.type = ItemType.NERD_DEBUFF
        self.description = (
            "You were possessed by a pretentious nerdy high school kid. "
            "You feel a desperate need to correct everyone and be an annoying little shit. "
            "(We take no responsibility for whatever happens while possessed) "
        )
        self.information = (
            "You gain this debuff when someone uses a ghost bean on you. "
            "Your next few messages will become nerd talk."
        )
        self.emoji = "🤓"


class Trumpify(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "Grab her by the bean!"
        self.type = ItemType.TRUMP_DEBUFF
        self.description = (
            "You were possessed by the ghost of Donald Trump. "
            "Im sorry for you this is just unfortunate. "
            "(We take no responsibility for whatever happens while possessed) "
        )
        self.information = (
            "You gain this debuff when someone uses a ghost bean on you. "
            "Your next few messages will become trump talk."
        )
        self.emoji = "🚽"


class Machofy(Debuff):

    def __init__(self, cost: int | None):
        super().__init__(cost)
        self.name = "I am the best."
        self.type = ItemType.MACHO_DEBUFF
        self.description = (
            "You were possessed by the ghost of a massive macho. "
            "(We take no responsibility for whatever happens while possessed) "
        )
        self.information = (
            "You gain this debuff when someone uses a ghost bean on you. "
            "Your next few messages will become macho talk."
        )
        self.emoji = "😎"


# Lootbox Extras


class ChestBeansReward(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="A Bunch of Beans!",
            type=ItemType.CHEST_BEANS,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="Lootbox reward containing beans.",
            information=f"Can contain between {LootBox.LARGE_MIN_BEANS} and {LootBox.LARGE_MAX_BEANS} beans.",
            emoji="🅱️",
            cost=cost,
            value=None,
            hide_in_shop=True,
            image_url="https://i.imgur.com/jjBv2fG.png",
        )


class ChestMimic(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Oh no, it's a Mimic!",
            type=ItemType.CHEST_MIMIC,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="Lootbox 'reward' that gnaws at your ankles and eats some of your beans.",
            information=f"May eat between {LootBox.SMALL_MIN_BEANS} and {LootBox.SMALL_MAX_BEANS} beans. Never removes more beans than you own.",
            emoji="😠",
            cost=cost,
            value=None,
            hide_in_shop=True,
        )


class ChestLargeMimic(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Oh no, it's a LARGE Mimic!",
            type=ItemType.CHEST_LARGE_MIMIC,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="Lootbox 'reward' that can seriously mess you up. Removes a large amount of beans and sends you to jail as well.",
            information=(
                f"May eat between {LootBox.LARGE_MIN_BEANS} and {LootBox.LARGE_MAX_BEANS} beans. "
                "Never removes more beans than you own. Can only remove up to 10% of your total seasonal high score. "
                "If you have a hazmat suit equipped, it consumes up to 5 stacks of it instead of sending you to jail."
            ),
            emoji="😡",
            cost=cost,
            value=None,
            hide_in_shop=True,
        )


class ChestSpookMimic(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="AAAAAAH, it's a Spooky Mimic!",
            type=ItemType.CHEST_SPOOK_MIMIC,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="Lootbox 'reward' that gnaws at your ankles and eats some of your beans. It also possesses you with a random ghost.",
            information=(
                f"May eat between {LootBox.SMALL_MIN_BEANS} and {LootBox.SMALL_MAX_BEANS} beans. "
                "Never removes more beans than you own. The ghost will possess you for 15 of your messages."
            ),
            emoji="😨",
            cost=cost,
            value=None,
            hide_in_shop=True,
        )


# Garden Seeds


class BaseSeed(Item):

    SEED_TYPES = [
        ItemType.RARE_SEED,
        ItemType.SPEED_SEED,
        ItemType.BOX_SEED,
        ItemType.CAT_SEED,
        ItemType.CRYSTAL_SEED,
        ItemType.YELLOW_SEED,
        ItemType.GHOST_SEED,
        ItemType.BAKED_SEED,
        ItemType.FLASH_SEED,
        ItemType.KEY_SEED,
    ]

    SEED_PLANT_MAP = {
        ItemType.RARE_SEED: PlantType.RARE_BEAN,
        ItemType.SPEED_SEED: PlantType.SPEED_BEAN,
        ItemType.BOX_SEED: PlantType.BOX_BEAN,
        ItemType.CAT_SEED: PlantType.CAT_BEAN,
        ItemType.CRYSTAL_SEED: PlantType.CRYSTAL_BEAN,
        ItemType.YELLOW_SEED: PlantType.YELLOW_BEAN,
        ItemType.GHOST_SEED: PlantType.GHOST_BEAN,
        ItemType.BAKED_SEED: PlantType.BAKED_BEAN,
        ItemType.FLASH_SEED: PlantType.FLASH_BEAN,
        ItemType.KEY_SEED: PlantType.KEY_BEAN,
    }

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bean Seed",
            type=ItemType.BEAN_SEED,
            group=ItemGroup.SEED,
            shop_category=ShopCategory.GARDEN,
            description="Just your regular ol' bean, but you plant it in your garden.",
            information=(
                "Takes 3-6 Days to grow, depending on water."
                "\nProduces 450 - 550 beans when harvested."
            ),
            emoji=BeanPlant.READY_EMOJI,
            cost=cost,
            value=1,
            hide_in_shop=True,
        )


class RareSeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 3000
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Rare Bean Seed"
        self.type = ItemType.RARE_SEED
        self.description = (
            "You found this special shiny bean while harvesting your last bean plant. "
            "It looks really juicy, maybe it will produce even more beans!"
        )
        self.information = (
            "Has a small chance of dropping when harvesting any bean plant."
            "\nTakes 5-10 Days to grow, depending on water."
            "\nProduces 1900 - 2100 beans when harvested."
        )
        self.emoji = RareBeanPlant.READY_EMOJI


class SpeedSeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 3000
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Speed Bean Seed"
        self.type = ItemType.SPEED_SEED
        self.description = (
            "When picking up this bean it slips through your fingers and completely defies gravity "
            "by falling significantly faster than any other bean. Maybe it will grow just as fast. "
        )
        self.information = (
            "Has a small chance of dropping when harvesting any bean plant."
            "\nTakes 3-6 Hours to grow, depending on water."
            "\nProduces 90 - 110 beans when harvested."
        )
        self.emoji = SpeedBeanPlant.READY_EMOJI


class CrystalSeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 7000
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Crystal Bean Seed"
        self.type = ItemType.CRYSTAL_SEED
        self.description = (
            "WOAH! What a pretty little bean! This must be worth a fortune. "
            "Better plant it quick, just imagine the amount of beans you will make."
        )
        self.information = (
            "Has a super small chance of dropping when harvesting any bean plant."
            "\nTakes 7-14 Days to grow, depending on water."
            "\nProduces 5000 - 6000 beans when harvested."
        )
        self.emoji = CrystalBeanPlant.READY_EMOJI


class BoxSeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 1000
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Treasure Bean Seed"
        self.type = ItemType.BOX_SEED
        self.description = (
            "Aww look how cute this tiny bean looks! "
            "Maybe it will grow into a big beautiful treasure hoard "
            "when you plant it in your garden. Just pray it doesn't have teeth."
        )
        self.information = "Available as a rare drop from lootboxes."
        self.information = (
            "Available as a rare drop from lootboxes and encounters."
            "\nTakes 4-8 Days to grow, depending on water."
            "\nProduces 900 - 1100 beans when harvested."
            "\nDrops a personal x10 chest when harvested."
        )
        self.emoji = BoxBeanPlant.READY_EMOJI


class CatSeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 500
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Catgirl Bean Seed"
        self.type = ItemType.CAT_SEED
        self.description = (
            "You find an oddly cat-shaped pink bean, you can only begin to speculate what the hell this is. "
            "Plant it in your garden, who knows it might turn into catnip or something... that definitely won't end poorly right?"
        )
        self.information = (
            "Available as a rare drop from lootboxes and encounters."
            "\nTakes 3-6 Days to grow, depending on water."
            "\nProduces 450 - 550 beans when harvested."
            "\nAttracts useless catgirls with a small chance to attract a useful one."
        )
        self.emoji = CatBeanPlant.READY_EMOJI


class YellowSeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 1000
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Piss Bean Seed"
        self.type = ItemType.YELLOW_SEED
        self.description = (
            "This little stinker smells awful! You recognize the scent but it takes you a while to connect the dots. "
            "Yep, it's piss. And not a particularly healthy kind. Better go plant it quick. (Fertilizes the soil, making plants grow faster)"
        )
        self.information = (
            "Available as a rare drop from lootboxes and encounters."
            "\nTakes 2-4 Days to grow, depending on water."
            "\nProduces 200 - 300 beans when harvested."
            "\nFertilizes the plot it was planted on for 3 days, making beans grow 100% faster."
        )
        self.emoji = YellowBeanPlant.READY_EMOJI


class GhostSeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 1000
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Ghost Bean Seed"
        self.type = ItemType.GHOST_SEED
        self.description = (
            "OOoooOOoooo so spooky! You can even see through this bean, woah! "
            "Plant it in your garden and maybe youll get to see something amazing."
        )
        self.information = (
            "Available as a rare drop from lootboxes and encounters."
            "\nTakes 3-6 Days to grow, depending on water."
            "\nProduces 450 - 550 beans when harvested."
            "\nWhen harvested it will always drop a Spooky Bean that allwos you to curse others."
        )
        self.emoji = GhostBeanPlant.READY_EMOJI


class BakedSeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 850
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Baked Bean Seed"
        self.type = ItemType.BAKED_SEED
        self.description = (
            "You can hear the faint sound of reggea music as you pick up these beans. "
            "They look at you with deep red eyes and give off a toasty dank smell. "
            "Go plant them in your garden, im sure they wont care. "
        )
        self.information = (
            "Available as a rare drop from lootboxes and encounters."
            "\nTakes 2-4 Days to grow, depending on water."
            "\nProduces 420 - 690 beans when harvested."
            "\nWhen harvested they will make you stoned and turn your next few messages into stoner talk gibberish."
        )
        self.emoji = BakedBeanPlant.READY_EMOJI


class FlashSeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 6500
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Flash Bean Seed"
        self.type = ItemType.FLASH_SEED
        self.description = (
            "A Piss Bean survived and is back for one last run. It found its calling as the Flash! "
            "It's so fast, it helps you grow every plot at lightning speed! Until... "
            "(Makes all your plots age twice as fast while active)"
        )
        self.information = (
            "Available as a super rare drop from lootboxes and encounters."
            "\nTakes 2-4 Days to grow, depending on water."
            "\nProduces a random amount of encounter keys up to the current guild level."
        )
        self.emoji = FlashBeanPlant.SEED_EMOJI


class KeySeed(BaseSeed):

    def __init__(self, cost: int | None):
        defaultcost = 3000
        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.name = "Key Seed"
        self.type = ItemType.KEY_SEED
        self.description = (
            "This seed almost looks like it could unlock a door."
            "Maybe it will grow into something actually capable of doing so."
        )
        self.information = (
            "Available as a super rare drop from lootboxes and encounters."
            "\nWill be active for 3 days, boosting the growth of all of your plants by an additional 100%. "
            "This stacks additively with other flash beans, water and fertilizer."
            "\nProduces a Ghost Bean Seed when harvested."
        )
        self.emoji = KeyBeanPlant.READY_EMOJI


# Permanent Rare Items


class BetaBadge(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Beta Badge",
            type=ItemType.BETA_BADGE,
            group=ItemGroup.MISC,
            shop_category=ShopCategory.FUN,
            description="A token of appreciation for participating in a Beans Beta event. You are awesome!",
            information="Thank you so much! c: (Art by Smorlis)",
            emoji=1275081546713534464,
            cost=cost,
            value=1,
            hide_in_shop=True,
            permanent=True,
        )


class PrestigeBean(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Prestige Bean",
            type=ItemType.PRESTIGE_BEAN,
            group=ItemGroup.SUBSCRIPTION,
            shop_category=ShopCategory.FUN,
            description="A proof of your achievements in previous Bean seasons. Each of these will generate you one bean a day.",
            information="Given out at the end of a Beans season for every 10k Beans Score you aquired.",
            emoji="🅱️",
            cost=cost,
            value=1,
            trigger=ItemTrigger.DAILY,
            hide_in_shop=True,
            permanent=True,
        )


class PermPetBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Floof Paws",
            type=ItemType.PERM_PET_BOOST,
            group=ItemGroup.FLAT_BONUS,
            shop_category=ShopCategory.PET,
            description=(
                "These magical gloves will give you a permanent +1 to every pet."
                " It affects the base roll, so it will also scale with any bonus modifiers."
                " Possible side effects include randomly using the ':3' emote."
            ),
            information="Unique Item, Given out at the end of Beans Season 1.",
            emoji="🐾",
            cost=cost,
            value=1,
            trigger=[ItemTrigger.PET],
            hide_in_shop=True,
            permanent=True,
        )


class UsefulCatGirl(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Useful Catgirl",
            type=ItemType.USEFUL_CATGIRL,
            group=ItemGroup.FLAT_BONUS,
            shop_category=ShopCategory.INTERACTION,
            description=(
                "After housing so many useless catgirls you somehow managed to convince one of them to be useful. "
                "Whenever you slap someone, she'll also claw at them. Gain +1 to slaps. "
                "Whenever you pet someone she'll snuggle up close with them. Gain +1 to pets as well."
            ),
            information="Available as a super rare drop from lootboxes.",
            emoji="🐈",
            cost=cost,
            value=1,
            trigger=[ItemTrigger.PET, ItemTrigger.SLAP],
            hide_in_shop=True,
            permanent=True,
        )


class IncomingPetBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="E-Girl UwU",
            type=ItemType.INC_PET_BOOST,
            group=ItemGroup.INCOMING_FLAT_BONUS,
            shop_category=ShopCategory.PET,
            description=(
                "No one can match the cuteness of your UwUs. People love giving you heatpats, permanently "
                "increasing their effectiveness on you. +1 to each pet you recieve. "
                " This affects the base value, so it will also scale with any bonus modifiers."
            ),
            information="Unique Item, Given out at the end of Beans Season 1.",
            emoji="💄",
            cost=cost,
            value=1,
            trigger=[ItemTrigger.PET],
            hide_in_shop=True,
            permanent=True,
        )


class PermSlapBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bionic Cyborg Arm",
            type=ItemType.PERM_SLAP_BOOST,
            group=ItemGroup.FLAT_BONUS,
            shop_category=ShopCategory.SLAP,
            description=(
                "You initially got this for its 'personal fun time' programs, but "
                "it turns out this thing packs a punch! Permanently increases the "
                "power of your slaps by +1."
                " This affects the base value, so it will also scale with any bonus modifiers."
            ),
            information="Unique Item, Given out at the end of Beans Season 1.",
            emoji="🤖",
            cost=cost,
            value=1,
            trigger=[ItemTrigger.SLAP],
            hide_in_shop=True,
            permanent=True,
        )


class PermFartBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Big Dumpy",
            type=ItemType.PERM_FART_BOOST,
            group=ItemGroup.FLAT_BONUS,
            shop_category=ShopCategory.FART,
            description=(
                "Dayum, you got that cake, them sweet cheeks, you're packin' a wagon, "
                " thicker than a bowl of oatmeal, got that big booty and you know how to use it."
                " Permanently increases the power of your farts by +1."
                " This affects the base value, so it will also scale with any bonus modifiers."
                " (wont go over the possible max roll)"
            ),
            information="Unique Item, Given out at the end of Beans Season 1.",
            emoji="🍑",
            cost=cost,
            value=1,
            trigger=[ItemTrigger.FART],
            hide_in_shop=True,
            permanent=True,
        )


class UltraBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Beanz'n'Dreamz",
            type=ItemType.ULTRA_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.INTERACTION,
            description=(
                "You've heard stories of catgirls drinking these non-stop, maybe you even have one "
                "and just see empty cans everywhere. You finally cave in and decide to try "
                "one yourself and you instantly see why she's addicted. "
                "It will power up your next fart, pet or slap by x100!"
            ),
            information="Given out at the end of a Beans season as a bonus reward.",
            emoji="💯",
            cost=cost,
            value=100,
            trigger=[ItemTrigger.FART, ItemTrigger.PET, ItemTrigger.SLAP],
            hide_in_shop=True,
            controllable=True,
        )


class PermProtection(Item):

    def __init__(self, cost: int | None):
        defaultcost = 0

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Crippling Social Anxiety",
            type=ItemType.PERM_PROTECTION,
            group=ItemGroup.PROTECTION,
            shop_category=ShopCategory.INTERACTION,
            description=(
                "Years of dodging family get togethers, ghosting your friends messages asking you to hang out "
                "and never leaving your home has made you incredibly efficient at dodging not only responsibilities "
                "but also any harm coming your way. Permanently reduces any incoming jailtime by 1%."
            ),
            information="Unique Item, Given out at the end of Beans Season 1.",
            emoji="🙈",
            cost=cost,
            value=0.01,
            trigger=[ItemTrigger.FART, ItemTrigger.SLAP],
            hide_in_shop=True,
            permanent=True,
        )
