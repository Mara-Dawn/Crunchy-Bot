from datalayer.types import ItemTrigger

from items.item import Item
from items.types import ItemGroup, ItemType, ShopCategory


class Arrest(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Citizens Arrest",
            item_type=ItemType.ARREST,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="Take the law into your own hands and arrest a user of choice for 30 minutes.",
            emoji="🚨",
            cost=cost,
            value=None,
            view_class="ShopUserSelectView",
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )


class AutoCrit(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Magic Beans",
            item_type=ItemType.AUTO_CRIT,
            group=ItemGroup.AUTO_CRIT,
            shop_category=ShopCategory.INTERACTION,
            description="Let these rainbow colored little beans guide your next slap, pet or fart to a guaranteed critical hit.",
            emoji="💥",
            cost=cost,
            value=True,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
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
            item_type=ItemType.BAILOUT,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="Pay off the mods with beans to let you out of jail early.",
            emoji="🗿",
            cost=cost,
            value=None,
            view_class="ShopConfirmView",
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )


class Bat(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1337

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Baseball Bat",
            item_type=ItemType.BAT,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.INTERACTION,
            description="Sneak up on someone and knock them out for 20 minutes, making them unable to use and buy items or gamba their beans.",
            emoji="💫",
            cost=cost,
            value=20,
            view_class="ShopUserSelectView",
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )


class BonusFart(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bonus Fart",
            item_type=ItemType.BONUS_FART,
            group=ItemGroup.BONUS_ATTEMPT,
            shop_category=ShopCategory.FART,
            description="Allows you to continue farting on a jailed person after using your guaranteed one.",
            emoji="😂",
            cost=cost,
            value=True,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
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
            item_type=ItemType.BONUS_PET,
            group=ItemGroup.BONUS_ATTEMPT,
            shop_category=ShopCategory.PET,
            description="Allows you to continue giving pets to a jailed person after using your guaranteed one.",
            emoji="🥰",
            cost=cost,
            value=True,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.PET],
            weight=150,
            controllable=True,
        )


class UltraPet(Item):

    def __init__(self, cost: int | None):
        defaultcost = 900

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="The Most Gentle Pet Ever",
            item_type=ItemType.ULTRA_PET,
            group=ItemGroup.MAJOR_JAIL_ACTION,
            shop_category=ShopCategory.PET,
            description="You feel a weird tingle in your hand, almost as if the next person to recieve your pets will be instantly freed from jail.",
            emoji="😳",
            cost=cost,
            value=True,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.PET],
            lootbox_exclusive=True,
            controllable=True,
        )


class PenetratingPet(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Gamer Hands Pet",
            item_type=ItemType.PENETRATING_PET,
            group=ItemGroup.MAJOR_JAIL_ACTION,
            shop_category=ShopCategory.PET,
            description="Years of hardcore sweaty gaming, dorito dust and a lack of hygiene turned your hands into incredibly effective weapons. Your next pet instantly dissolves any protection the target might have had.",
            emoji="🎮",
            cost=cost,
            value=True,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.PET],
            lootbox_exclusive=True,
            controllable=True,
        )


class BonusSlap(Item):

    def __init__(self, cost: int | None):
        defaultcost = 35

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Bonus Slap",
            item_type=ItemType.BONUS_SLAP,
            group=ItemGroup.BONUS_ATTEMPT,
            shop_category=ShopCategory.SLAP,
            description="Allows you to continue slapping a jailed person after using your guaranteed one.",
            emoji="✋",
            cost=cost,
            value=True,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.SLAP],
            weight=150,
            controllable=True,
        )


class SwapSlap(Item):

    def __init__(self, cost: int | None):
        defaultcost = 6000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="No U",
            item_type=ItemType.SWAP_SLAP,
            group=ItemGroup.MAJOR_ACTION,
            shop_category=ShopCategory.SLAP,
            description="Limited edition uno reverse card. If you are jailed, your next slap against a non jailed user will make them trade places with you.",
            emoji="🔁",
            cost=cost,
            value=None,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.SLAP],
            lootbox_exclusive=True,
            controllable=True,
        )


class UltraSlap(Item):

    def __init__(self, cost: int | None):
        defaultcost = 3000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Infinity and Beyond Glove",
            item_type=ItemType.ULTRA_SLAP,
            group=ItemGroup.MAJOR_ACTION,
            shop_category=ShopCategory.SLAP,
            description="This glove will slap people into another dimension, completely annihilating them and erasing their existence. Your next slap will stun your target for 5 hours.",
            emoji="🥊",
            cost=cost,
            value=60 * 5,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.SLAP],
            lootbox_exclusive=True,
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
            item_type=ItemType.EXPLOSIVE_FART,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description=description,
            emoji="😨",
            cost=cost,
            value=1,
            view_class="ShopConfirmView",
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )


class UltraFartBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Nuclear Lunch Codes",
            item_type=ItemType.ULTRA_FART_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.FART,
            description="You try to cook a nice lunch, but your cooking skills are so abysmal that the brave souls who 'agreed' to eat it have a near death experience. Powers up your next Fart by x50.",
            emoji="🤮",
            cost=cost,
            value=50,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.FART],
            lootbox_exclusive=True,
            controllable=True,
        )


class FartBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 150

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="UK Breakfast Beans",
            item_type=ItemType.FART_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.FART,
            description="Extremely dangerous, multiplies the power of your next fart by 3.",
            emoji="🤢",
            cost=cost,
            value=3,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
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
            item_type=ItemType.FART_PROTECTION,
            group=ItemGroup.PROTECTION,
            shop_category=ShopCategory.INTERACTION,
            description="According to him his grandpa took it from a dead guy in ww2. The next 5 interactions negatively affecting your jailtime will be reduced by 50%",
            emoji="☣",
            cost=cost,
            value=0.5,
            view_class=None,
            allow_amount=False,
            base_amount=5,
            max_amount=5,
            trigger=[ItemTrigger.FART, ItemTrigger.SLAP],
            controllable=True,
        )


class AdvancedFartProtection(FartProtection):

    def __init__(self, cost: int | None):
        defaultcost = 1500

        if cost is None:
            cost = defaultcost

        super().__init__(cost)
        self.base_amount = 15
        self.max_amount = 30
        self.name = self.name + " x3"
        self.description = "A poor paranoid soul sewed 5 hazmat suits into one, making this one much stronger than what you would usually find in a store. (caps out at 25 stacks)"
        self.lootbox_exclusive = True


class FartStabilizer(Item):

    def __init__(self, cost: int | None):
        defaultcost = 45

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Ass ACOG",
            item_type=ItemType.FART_STABILIZER,
            group=ItemGroup.STABILIZER,
            shop_category=ShopCategory.FART,
            description="Stabilizes your aim and increases your rectal precision. Your next fart cannot roll below 0.",
            emoji="🔭",
            cost=cost,
            value=10,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
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
            item_type=ItemType.FARTVANTAGE,
            group=ItemGroup.ADVANTAGE,
            shop_category=ShopCategory.FART,
            description="Couldn't hold back again, hm? Better go empty your bowels on some poor loser. Rolls your next fart twice and takes the better result.",
            emoji="🍔",
            cost=cost,
            value=2,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
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
            item_type=ItemType.GIGA_FART,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.FART,
            description="Works better than any laxative and boosts the pressure of your next fart by x10. Try not to hurt yourself.",
            emoji="💀",
            cost=cost,
            value=10,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
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
            item_type=ItemType.JAIL_REDUCTION,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="Manipulate the mods into believing your jail sentence is actually 30 minutes shorter than it really is. (Cuts off at 30 minutes left)",
            emoji="🥺",
            cost=cost,
            value=30,
            view_class="ShopConfirmView",
            allow_amount=True,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )


class LootBoxItem(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Random Treasure Chest",
            item_type=ItemType.LOOTBOX,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="No need to wait for loot box drops, just buy your own!",
            emoji="🧰",
            cost=cost,
            value=None,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )


class LootBoxItemBundle(Item):

    def __init__(self, cost: int | None):
        defaultcost = 500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Random Treasure Chest x5",
            item_type=ItemType.LOOTBOX_BUNDLE,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="Too addicted? Just buy 5 at once! All neatly contained within a single Box.",
            emoji="🧰",
            cost=cost,
            value=None,
            view_class=None,
            allow_amount=False,
            base_amount=5,
            max_amount=None,
            trigger=None,
        )


class PocketMimic(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Pocket Mimic",
            item_type=ItemType.MIMIC,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="Use this item from your inventory to spawn a large mimic. It will look like a regular chest spawn to other people.",
            emoji="🧰",
            cost=cost,
            value=None,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
            controllable=True,
            lootbox_exclusive=True,
            useable=True,
        )


class CatGirl(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Useless Cat Girl",
            item_type=ItemType.CATGIRL,
            group=ItemGroup.LOOTBOX,
            shop_category=ShopCategory.LOOTBOX,
            description="She is lazy, sleeply, does nothing all day and apparently lives in your inventory now.",
            emoji="🐱",
            cost=cost,
            value=None,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
            lootbox_exclusive=True,
        )


class LotteryTicket(Item):

    def __init__(self, cost: int | None):
        defaultcost = 150

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Lottery Ticket",
            item_type=ItemType.LOTTERY_TICKET,
            group=ItemGroup.LOTTERY,
            shop_category=ShopCategory.FUN,
            description="Enter the Weekly Crunchy Bean Lottery© and win big! Max 3 tickets per person.",
            emoji="🎫",
            cost=cost,
            value=1,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=3,
            trigger=None,
        )


class NameColor(Item):

    def __init__(self, cost: int | None):
        defaultcost = 100

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Name Color Change",
            item_type=ItemType.NAME_COLOR,
            group=ItemGroup.SUBSCRIPTION,
            shop_category=ShopCategory.FUN,
            description="Paint your discord name in your favourite color! Grab one weeks worth of color tokens. Each day, a token gets consumed until you run out.",
            emoji="🌈",
            cost=cost,
            value=1,
            view_class="ShopColorSelectView",
            allow_amount=True,
            base_amount=7,
            max_amount=None,
            trigger=[ItemTrigger.DAILY],
        )


class PetBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 120

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Big Mama Bear Hug",
            item_type=ItemType.PET_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.PET,
            description="When a normal pet just isnt enough. Powers up your next pet by 5x.",
            emoji="🧸",
            cost=cost,
            value=5,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
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
            item_type=ItemType.REACTION_SPAM,
            group=ItemGroup.SUBSCRIPTION,
            shop_category=ShopCategory.FUN,
            description="Hire a personal bully to react to every single message of your victim with an emoji of your choice. One purchase amounts to 10 message reactions. Only one bully can be active at a time.",
            emoji="🤡",
            cost=cost,
            value=1,
            view_class="ShopReactionSelectView",
            allow_amount=True,
            base_amount=10,
            max_amount=None,
            trigger=[ItemTrigger.USER_MESSAGE],
        )


class Release(Item):

    def __init__(self, cost: int | None):
        defaultcost = 1000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Get out of Jail Fart",
            item_type=ItemType.RELEASE,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="Due to dietary advancements your farts can now help a friend out of jail for one time only.",
            emoji="🔑",
            cost=cost,
            value=None,
            view_class="ShopUserSelectView",
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )


class RouletteFart(Item):

    def __init__(self, cost: int | None):
        defaultcost = 500

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Russian Roulette",
            item_type=ItemType.ROULETTE_FART,
            group=ItemGroup.IMMEDIATE_USE,
            shop_category=ShopCategory.JAIL,
            description="After a night of heavy drinking you decide to gamble on a fart to prank your friend. 50% chance to jail the target, 50% chance to shit yourself and go to jail instead. (30 minutes)",
            emoji="🔫",
            cost=cost,
            value=None,
            view_class="ShopUserSelectView",
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=None,
        )


class SatanBoost(Item):

    def __init__(self, cost: int | None):
        defaultcost = 2345

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Satan's Nuclear Hellfart",
            item_type=ItemType.SATAN_FART,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.FART,
            description="A x25 fart boost that sends a jailed person to the shadow realm but with a high risk of the farter being caught in the blast. 75% chance to jail yourself too with the same duration.",
            emoji="😈",
            cost=cost,
            value=25,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
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
            item_type=ItemType.SLAP_BOOST,
            group=ItemGroup.VALUE_MODIFIER,
            shop_category=ShopCategory.SLAP,
            description="For when someone has been extra horny. Powers up your next slap by 5x.",
            emoji="🔨",
            cost=cost,
            value=5,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.SLAP],
            controllable=True,
        )


class NoLimitGamba(Item):

    def __init__(self, cost: int | None):
        defaultcost = 8000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Unlimited Gamba",
            item_type=ItemType.UNLIMITED_GAMBA,
            group=ItemGroup.GAMBA,
            shop_category=ShopCategory.FUN,
            description="This item removes the Limit for your next gamba. You can bet as much as you want. Good luck.",
            emoji="🎰",
            cost=cost,
            value=1,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.GAMBA],
            controllable=True,
        )


class NoCooldownGamba(Item):

    def __init__(self, cost: int | None):
        defaultcost = 4000

        if cost is None:
            cost = defaultcost

        super().__init__(
            name="Instant Gamba",
            item_type=ItemType.INSTANT_GAMBA,
            group=ItemGroup.GAMBA,
            shop_category=ShopCategory.FUN,
            description="Allows you to ignore the cooldown on your next gamba.",
            emoji="🎰",
            cost=cost,
            value=1,
            view_class=None,
            allow_amount=False,
            base_amount=1,
            max_amount=None,
            trigger=[ItemTrigger.GAMBA],
            controllable=True,
        )
