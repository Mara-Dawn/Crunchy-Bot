from enum import Enum


class ObjectType(str, Enum):
    ITEM = "Item"
    GEAR = "Gear"
    ENCHANTMENT = "Enchantment"
    SKILL = "Skill"


class ValueType(str, Enum):
    PERCENTAGE = "Percentage"
    FLOAT = "Float"
    INT = "Int"
    STRING = "String"
    NONE = "None"


class BlockType(str, Enum):
    ANSI = "ansi"
    PYTHON = "python"
    RAW = ""


class ValueColor(str, Enum):
    NONE = "[0m"
    GREY = "[30m"
    RED = "[31m"
    GREEN = "[32m"
    YELLOW = "[33m"
    BLUE = "[34m"
    PINK = "[35m"
    CYAN = "[36m"
    WHITE = "[37m"


class ValueColorBold(str, Enum):
    NONE = "[0m"
    GREY = "[1;30m"
    RED = "[1;31m"
    GREEN = "[1;32m"
    YELLOW = "[1;33m"
    BLUE = "[1;34m"
    PINK = "[1;35m"
    CYAN = "[1;36m"
    WHITE = "[1;37m"


class ValueColorHex(str, Enum):
    GREY = "979c9f"
    RED = "a43033"
    YELLOW = "b58900"
    BLUE = "268bd2"
    CYAN = "2aa198"
    WHITE = "ffffff"
