from dataclasses import dataclass

from combat.gear.types import Rarity
from forge.types import ForgeableType
from view.object.types import ObjectType


@dataclass
class Forgeable:
    name: str
    id: int
    forge_type: ForgeableType
    object_type: ObjectType
    value: int
    level: int = None
    rarity: Rarity = None
    emoji: str = None
    image_url: str = None

    def get_embed():
        pass


@dataclass
class Ingredient:
    forge_type: ForgeableType | None = None
    object_type: ObjectType | None = None
    value: int | None = None
    level: int | None = None
    rarity: Rarity | None = None

    def match(self, forgeable: Forgeable) -> bool:
        if self.forge_type is not None and self.forge_type != forgeable.forge_type:
            return False
        if self.object_type is not None and self.object_type != forgeable.object_type:
            return False
        if self.value is not None and self.value != forgeable.value:
            return False
        if self.level is not None and self.level != forgeable.level:
            return False
        if self.rarity is not None and self.rarity != forgeable.rarity:  # noqa: SIM103
            return False
        return True


@dataclass
class IngredientList:
    ingredients: tuple[Ingredient, Ingredient, Ingredient]

    def match(self, forgeable: Forgeable) -> bool:
        if self.forge_type is not None and self.forge_type != forgeable.forge_type:
            return False
        if self.object_type is not None and self.object_type != forgeable.object_type:
            return False
        if self.value is not None and self.value != forgeable.value:
            return False
        if self.level is not None and self.level != forgeable.level:
            return False
        if self.rarity is not None and self.rarity != forgeable.rarity:  # noqa: SIM103
            return False
        return True


@dataclass
class ForgeInventory:
    first: Forgeable | None = None
    second: Forgeable | None = None
    third: Forgeable | None = None

    @property
    def items(self) -> list[Forgeable]:
        return [self.first, self.second, self.third]

    @property
    def empty(self) -> bool:
        return all(forgeable is None for forgeable in self.items)

    def set(self, index: int, item: Forgeable):
        match index:
            case 0:
                self.first = item
            case 1:
                self.second = item
            case 2:
                self.third = item

    def add(self, item: Forgeable) -> bool:
        if item.id in [x.id for x in self.items if x is not None]:
            return False

        for idx, slot in enumerate(self.items):
            if slot is None:
                self.set(idx, item)
                return True
        return False

    def remove(self, item: Forgeable):
        for reverse_idx, slot in enumerate(reversed(self.items)):
            if slot.id == item.id:
                idx = len(self.items) - reverse_idx - 1
                self.remove_at(idx)
                return True
        return False

    def clear(self):
        self.first = None
        self.second = None
        self.third = None

    def remove_at(self, index: int):
        match index:
            case 0:
                self.first = None
            case 1:
                self.second = None
            case 2:
                self.third = None
