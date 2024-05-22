from combat.gear.types import GearRarity

if __name__ == "__main__":

    RARITY_SCALING = {
        GearRarity.NORMAL: -15,
        GearRarity.MAGIC: 1,
        GearRarity.RARE: 6,
        GearRarity.LEGENDARY: 1,
        GearRarity.UNIQUE: 1.5,
    }

    rarity_weights = {
        GearRarity.NORMAL: 100,
        GearRarity.MAGIC: 50,
        GearRarity.RARE: 10,
        GearRarity.LEGENDARY: 1,
        GearRarity.UNIQUE: 5,
    }

    min_rarity_lvl = {
        GearRarity.NORMAL: 0,
        GearRarity.MAGIC: 1,
        GearRarity.RARE: 3,
        GearRarity.LEGENDARY: 5,
        GearRarity.UNIQUE: 4,
    }

    levels = range(1, 13)

    for level in levels:
        print(f"\nlevel: {level}")
        weights = {}

        for rarity, weight in rarity_weights.items():
            weight += level * RARITY_SCALING[rarity]

            weight = max(0, weight)

            if min_rarity_lvl[rarity] > level:
                weight = 0

            weights[rarity] = weight

        sum_weights = sum(weights.values())
        # weights = {k: v / sum_weights for k, v in weights.items()}

        for rarity, weight in weights.items():
            percent = weight / sum_weights * 100
            print(f"{rarity.value}: {percent:.02f}%")
