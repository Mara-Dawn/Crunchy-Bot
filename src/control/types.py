from enum import Enum


class ControllerType(str, Enum):
    SHOP_VIEW = "ShopViewController"
    SHOP_RESPONSE_VIEW = "ShopResponseViewController"
    LOOTBOX_VIEW = "LootBoxViewController"
    RANKING_VIEW = "RankingViewController"
    PREDICTION_MODERATION_VIEW = "PredictionModerationViewController"
    PREDICTION_INTERACTION_VIEW = "PredictionInteractionViewController"
    PREDICTION_VIEW = "PredictionViewController"


class ControllerModuleMap(str, Enum):

    @staticmethod
    def get_module(controller_type: ControllerType):
        map = {
            ControllerType.SHOP_VIEW: "shop_view_controller",
            ControllerType.SHOP_RESPONSE_VIEW: "shop_response_view_controller",
            ControllerType.LOOTBOX_VIEW: "lootbox_view_controller",
            ControllerType.RANKING_VIEW: "ranking_view_controller",
            ControllerType.PREDICTION_MODERATION_VIEW: "prediction_moderation_view_controller",
            ControllerType.PREDICTION_INTERACTION_VIEW: "prediction_interaction_view_controller",
            ControllerType.PREDICTION_VIEW: "prediction_view_controller",
        }

        return map[controller_type]
