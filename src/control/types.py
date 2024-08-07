from enum import Enum


class ControllerType(str, Enum):
    SHOP_VIEW = "ShopViewController"
    SHOP_RESPONSE_VIEW = "ShopResponseViewController"
    LOOTBOX_VIEW = "LootBoxViewController"
    RANKING_VIEW = "RankingViewController"
    PREDICTION_MODERATION_VIEW = "PredictionModerationViewController"
    PREDICTION_INTERACTION_VIEW = "PredictionInteractionViewController"
    PREDICTION_VIEW = "PredictionViewController"
    INVENTORY_VIEW = "InventoryViewController"
    GARDEN_VIEW = "GardenViewController"
    COMBAT = "CombatViewController"
    EQUIPMENT = "EquipmentViewController"

    BASIC_ENEMY = "BasicEnemyController"
    BOSS_DADDY = "DaddyController"


class AIVersion(str, Enum):
    GPT3_5 = "gpt-3.5-turbo"
    GPT4_O = "gpt-4o"
    GPT4_O_MINI = "gpt-4o-mini"


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
            ControllerType.INVENTORY_VIEW: "inventory_view_controller",
            ControllerType.GARDEN_VIEW: "garden_view_controller",
            ControllerType.COMBAT: "combat_view_controller",
            ControllerType.EQUIPMENT: "equipment_view_controller",
            ControllerType.BASIC_ENEMY: "basic_enemy",
            ControllerType.BOSS_DADDY: "daddy",
        }

        return map[controller_type]
