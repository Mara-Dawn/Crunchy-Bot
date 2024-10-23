from dataclasses import dataclass
from enum import Enum


class UserSettingType(str, Enum):
    GAMBA_DEFAULT = "gamba_default"
    AUTO_SCRAP = "auto_scrap"
    REFRESH_SKILLS = "refresh_skills"
    DM_PING = "dm_ping"

    def get_title(option: "UserSettingType") -> str:
        title_map = {
            UserSettingType.GAMBA_DEFAULT: "Default Gamba Amount",
            UserSettingType.AUTO_SCRAP: "Auto Scrap Level",
            UserSettingType.REFRESH_SKILLS: "Auto Replenish Skills of Same Type",
            UserSettingType.DM_PING: "DM combat notifications",
        }
        return title_map[option]


class UserSettingsToggle(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"


class SkillRefreshOption(str, Enum):
    DISABLED = "disabled"
    SAME_RARITY = "same_rarity"
    LOWEST_RARITY = "lowest_rarity"
    HIGHEST_RARITY = "highest_rarity"

    def get_title(option: "SkillRefreshOption") -> str:
        title_map = {
            SkillRefreshOption.DISABLED: "Disabled",
            SkillRefreshOption.SAME_RARITY: "Same Rarity",
            SkillRefreshOption.LOWEST_RARITY: "Lowest Rarity",
            SkillRefreshOption.HIGHEST_RARITY: "Highest Rarity",
        }
        return title_map[option]


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
    MAIN_MENU = "MainMenuViewController"
    COMBAT = "CombatViewController"
    EQUIPMENT = "EquipmentViewController"
    USER_SETTING = "UserSettingViewController"

    BASIC_ENEMY = "BasicEnemyController"
    BOSS_DADDY = "DaddyController"
    BOSS_WEEB = "WeebController"


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
            ControllerType.MAIN_MENU: "main_menu_controller",
            ControllerType.EQUIPMENT: "equipment_view_controller",
            ControllerType.USER_SETTING: "user_setting_view_controller",
            ControllerType.BASIC_ENEMY: "basic_enemy",
            ControllerType.BOSS_DADDY: "daddy",
            ControllerType.BOSS_WEEB: "weeb",
        }

        return map[controller_type]


@dataclass
class FieldData:
    name: str
    value: str
    inline: bool
