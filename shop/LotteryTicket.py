import datetime
from RoleManager import RoleManager
from datalayer.ItemTrigger import ItemTrigger
from datalayer.UserInteraction import UserInteraction
from events.EventManager import EventManager
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
        
    async def obtain(self, role_manager: RoleManager, event_manager: EventManager, guild_id: int, member_id: int, beans_event_id: int = 0, amount: int = 1):
        event_manager.dispatch_inventory_event(
            datetime.datetime.now(), 
            guild_id,
            member_id,
            self.get_type(),
            beans_event_id,
            amount
        )
        
        await role_manager.add_lottery_role(guild_id, member_id)
    
    async def use(self, role_manager: RoleManager, event_manager: EventManager, guild_id: int, member_id: int, amount: int = 1):
        event_manager.dispatch_inventory_event(
            datetime.datetime.now(), 
            guild_id,
            member_id,
            self.get_type(),
            0,
            -amount
        )
        
        await role_manager.remove_lottery_role(guild_id, member_id)
        return self.value
        