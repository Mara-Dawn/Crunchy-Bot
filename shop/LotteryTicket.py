import datetime
from RoleManager import RoleManager
from datalayer.ItemTrigger import ItemTrigger
from events.EventManager import EventManager
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class LotteryTicket(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 100
        
        if cost is None:
            cost = defaultcost
            
        super().__init__(
            name = 'Lottery Ticket',
            type = ItemType.LOTTERY_TICKET,
            group = ItemGroup.LOTTERY,
            description = 'Enter the Weekly Crunchy Bean Lottery© and win big! Max 3 tickets per person.',
            emoji = '🎫',
            cost = cost,
            value = 1,
            view_class = None,
            allow_amount = False,
            base_amount = 1,
            max_amount = 3,
            trigger = None
        )
        
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
        