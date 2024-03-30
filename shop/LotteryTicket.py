from datalayer.ItemTrigger import ItemTrigger
from datalayer.UserInteraction import UserInteraction
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from shop.TriggerItem import TriggerItem

class LotteryTicket(TriggerItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Lottery Ticket'
        type = ItemType.LOTTERY_TICKET
        group = ItemGroup.VALUE_MODIFIER
        description = 'Enter the Weekly Crunchy Bean Lottery© and win big! Max 3 tickets per person.'
        defaultcost = 100
        emoji = '🎫'
        trigger = [ItemTrigger.LOTTERY]
        value = 1
        max_amount = 3
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(name, type, group, description, emoji, cost, trigger, value, max_amount=max_amount)