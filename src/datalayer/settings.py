from dataclasses import dataclass
from typing import Any, Type, TypeVar

from control.types import UserSettingType


class Setting:

    def __init__(
        self, parent_key: str, key: str, default, title: str, handler: str = ""
    ):
        self.key = key
        self.default = default
        self.title = title
        self.handler = handler
        self.parent_key = parent_key


class ModuleSettings:

    def __init__(self, key: str, name: str):
        self.name = name
        self.key = key
        self.settings: dict[str, Setting] = {}

    def add_setting(self, key: str, default, title: str, handler: str = "") -> None:
        self.settings[key] = Setting(self.key, key, default, title, handler)

    def get_setting(self, key: str) -> Setting:
        if key not in self.settings:
            return None
        return self.settings[key]


class GuildSettings:

    def __init__(self):
        self.settings: dict[str, ModuleSettings] = {}

    def add_module(self, module_settings: ModuleSettings) -> ModuleSettings:
        self.settings[module_settings.key] = module_settings

    def get_module(self, key: str) -> None | ModuleSettings:
        if key not in self.settings:
            return None

        return self.settings[key]

    def get_modules(self) -> dict[str, ModuleSettings]:
        return self.settings

    def get_default_setting(self, module: str, setting: str):
        if module not in self.settings:
            return None

        module_settings = self.settings[module]
        module_setting = module_settings.get_setting(setting)
        if module_setting is None:
            return None

        return module_setting.default


@dataclass
class UserSetting:
    T = TypeVar("T")
    setting_type: UserSettingType
    value_type: T
    options: dict[str, T] | None
    default: T
    title: str
    description: str
