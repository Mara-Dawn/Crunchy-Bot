from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class JailReduction(Item):

    def __init__(
        self,
        cost: int|None
    ):
        defaultcost = 100
        
        if cost is None:
            cost = defaultcost

        super().__init__(
            name = 'Gaslight the Guards',
            type = ItemType.JAIL_REDUCTION,
            group = ItemGroup.IMMEDIATE_USE,
            description = 'Manipulate the mods into believing your jail sentence is actually 30 minutes shorter than it really is. (Cuts off at 30 minutes left)',
            emoji = '🥺',
            cost = cost,
            value = 30,
            view_class = 'ShopConfirmView',
            allow_amount = True,
            base_amount = 1,
            max_amount = None,
            trigger = None
        )