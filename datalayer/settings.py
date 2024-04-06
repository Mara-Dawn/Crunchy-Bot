class Setting:

    def __init__(
        self, parent_key: str, key: str, default, title: str, handler: str = ""
    ):
        self.key = key
        self.default = default
        self.title = title
        self.handler = handler
        self.parent_key = parent_key

    def get_key(self) -> str:
        return self.key

    def get_default(self):
        return self.default

    def get_title(self) -> str:
        return self.title

    def get_handler(self) -> str:
        return self.handler

    def get_parent_key(self) -> str:
        return self.parent_key


class ModuleSettings:

    def __init__(self, key: str, name: str):
        self.name = name
        self.key = key
        self.settings: dict[str, Setting] = {}

    def get_name(self) -> str:
        return self.name

    def get_key(self) -> str:
        return self.key

    def add_setting(self, key: str, default, title: str, handler: str = "") -> None:
        self.settings[key] = Setting(self.key, key, default, title, handler)

    def get_setting(self, key: str) -> Setting:
        if key not in self.settings:
            return None
        return self.settings[key]

    def get_settings(self) -> dict[str, Setting]:
        return self.settings


class GuildSettings:

    def __init__(self):
        self.settings: dict[str, ModuleSettings] = {}

    def add_module(self, module_settings: ModuleSettings) -> ModuleSettings:
        self.settings[module_settings.get_key()] = module_settings

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

        return module_setting.get_default()
