from combat.enemies.types import EnemyType


class Config:

    # Lootbox Settings
    MIMIC_CHANCE = 0.1
    LARGE_CHEST_CHANCE = 0.03
    LARGE_MIMIC_CHANCE = 0.02
    SPOOK_MIMIC_CHANCE = 0
    LUCKY_ITEM_CHANCE = 0.05

    # General Combat
    MAX_LVL = 7

    COMBAT_INITIAL_WAIT = 90

    DEFAULT_TIMEOUT = 60 * 3
    SHORT_TIMEOUT = 60
    DM_PING_TIMEOUT = 30
    TIMEOUT_COUNT_LIMIT = 2
    TIMEOUT_JAIL_TIME = 30
    KICK_JAIL_TIME = 60

    ENEMY_HEALTH_SCALING = {
        1: 8.40,
        2: 15.93,
        3: 38.41,
        4: 96.22,
        5: 190.19,
        6: 356.37,
        7: 771.77,
    }

    OPPONENT_DAMAGE_BASE = {
        1: 250,
        2: 272.80,
        3: 335.54,
        4: 418.76,
        5: 595.03,
        6: 748.42,
        7: 834.09,
    }

    AVERAGE_PLAYER_POTENCY = {
        1: 2,
        2: 2.2,
        3: 2.4,
        4: 2.6,
        5: 2.8,
        6: 3,
        7: 3.2,
    }

    CHARACTER_BASE_INITIATIVE = 10
    CHARACTER_LVL_HP_INCREASE = 25
    CHARACTER_ENCOUNTER_SCALING_FACOTR = 1
    OPPONENT_ENCOUNTER_SCALING_FACTOR = 0.95
    OPPONENT_LEVEL_SCALING_FACTOR = 1
    OPPONENT_DAMAGE_VARIANCE = 0.05
    SKILL_TYPE_PENALTY = 0.2

    ENCOUNTER_MIN_LVL_SCALING = 0.65
    ENCOUNTER_MAX_LVL_SIZE_SCALING = 2 / 3
    ENEMY_HEALTH_LVL_FALLOFF = 0.95

    HEAL_CRIT_MODIFIER = 1.5

    # Status Effects
    BLEED_SCALING = 0.25
    LEECH_SCALING = 0.20
    POISON_SCALING = 0.15
    RANDOM_POSITIVE_CHANCE = 0.15
    FROST_DEX_PENALTY = 5
    FROST_HEAL_MODIFIER = 0.5
    BLIND_MISS_CHANCE = 0.35
    BLIND_BOSS_MISS_CHANCE = 0.25
    BLIND_DIMINISHING_RETURNS = 0.6
    FROGGED_FAIL_CHANCE = 0.5
    RAGE_QUIT_THRESHOLD = 0.1

    VULNERABLE_SCALING = 1.15
    MAGIC_VULN_SCALING = 1.25
    PHYS_VULN_SCALING = 1.25

    # Code Block Formatting
    ENEMY_MAX_WIDTH = 30
    COMBAT_EMBED_MAX_WIDTH = 44
    ITEM_MAX_WIDTH = 40
    SHOP_ITEM_MAX_WIDTH = 40
    INVENTORY_ITEM_MAX_WIDTH = 50

    # Guild Level Requirements
    LEVEL_REQUIREMENTS = {
        1: 100,
        2: 250,
        3: 300,
        4: 369,
        5: 420,
        6: 500,
        7: 9999999,
    }
    BOSS_LEVELS = [3, 6, 9, 12]
    BOSS_RETRY_REQUIREMENT = 15
    BOSS_KEY_CLAIM_DELAY = 180

    BOSS_TYPE = {
        3: EnemyType.DADDY_P1,
        6: EnemyType.WEEB_BALL,
        # 9: None,
        # 12: None,
    }

    BOSS_LEVEL = {v: k for k, v in BOSS_TYPE.items()}

    FORGE_UNLOCK_REQUIREMENT = 15

    # Scrap
    SCRAP_FORGE_MULTI = 1.5
    SCRAP_SHOP_MULTI = 30
