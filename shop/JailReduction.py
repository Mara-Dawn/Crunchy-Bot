from shop.IsntantItem import InstantItem
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class JailReduction(InstantItem):

    def __init__(
        self,
        cost: int|None
    ):
        name = 'Gaslight the Guards'
        type = ItemType.JAIL_REDUCTION
        group = ItemGroup.IMMEDIATE_USE
        description = 'Manipulate the mods into believing your jail sentence is actually 30 minutes shorter than it really is. (Cuts off at 30 minutes left)'
        defaultcost = 100
        emoji = '🥺'
        view = 'ShopConfirmView'
        allow_amount = True
        value = 30
        
        if cost is None:
            cost = defaultcost

        super().__init__(name, type, group, description, emoji, cost, view, value, allow_amount=allow_amount)

            