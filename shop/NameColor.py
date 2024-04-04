import datetime

from RoleManager import RoleManager
from datalayer.ItemTrigger import ItemTrigger
from events.EventManager import EventManager
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType
from view.ShopCategory import ShopCategory

class NameColor(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 100
        
        if cost is None:
            cost = defaultcost

        super().__init__(
            name = 'Name Color Change',
            type = ItemType.NAME_COLOR,
            group = ItemGroup.SUBSCRIPTION,
            shop_category = ShopCategory.FUN,
            description = 'Paint your discord name in your favourite color! Grab one weeks worth of color tokens. Each day, a token gets consumed until you run out.',
            emoji = '🌈',
            cost = cost,
            value = 1,
            view_class = 'ShopColorSelectView',
            allow_amount = True,
            base_amount = 7,
            max_amount = None,
            trigger = [ItemTrigger.DAILY]
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
        
        await role_manager.update_username_color(guild_id, member_id)
    
    async def use(self, role_manager: RoleManager, event_manager: EventManager, guild_id: int, member_id: int, amount: int = 1):
        event_manager.dispatch_inventory_event(
            datetime.datetime.now(), 
            guild_id,
            member_id,
            self.get_type(),
            0,
            -amount
        )
        
        await role_manager.update_username_color(guild_id, member_id)
        return self.value
        
                