import datetime

from RoleManager import RoleManager
from datalayer.ItemTrigger import ItemTrigger
from events.EventManager import EventManager
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class ReactionSpam(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 200
        
        if cost is None:
            cost = defaultcost

        super().__init__(
            name = 'Bully for Hire',
            type = ItemType.REACTION_SPAM,
            group = ItemGroup.SUBSCRIPTION,
            description = 'Hire a personal bully to react to every single message of your victim with an emoji of your choice. One purchase amounts to 10 message reactions. Only one bully can be active at a time.',
            emoji = '🤡',
            cost = cost,
            value = 1,
            view_class = 'ReactionSelectView',
            allow_amount = True,
            base_amount = 10,
            max_amount = None,
            trigger = [ItemTrigger.USER_MESSAGE]
        )