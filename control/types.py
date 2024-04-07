from enum import Enum


class ControllerType(str, Enum):
    SHOP_VIEW = "ShopViewController"
    SHOP_RESPONSE_VIEW = "ShopResponseViewController"
    LOOTBOX_VIEW = "LootBoxViewController"


class ControllerModuleMap(str, Enum):

    @staticmethod
    def get_module(controller_type: ControllerType):
        map = {
            ControllerType.SHOP_VIEW: "shop_view_controller",
            ControllerType.SHOP_RESPONSE_VIEW: "shop_response_view_controller",
            ControllerType.LOOTBOX_VIEW: "lootbox_view_controller",
        }

        return map[controller_type]
