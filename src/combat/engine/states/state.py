from abc import ABC, abstractmethod

from combat.encounter import EncounterContext
from combat.engine.common import CommonService
from combat.engine.types import StateType
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.combat_skill_manager import CombatSkillManager
from control.combat.context_loader import ContextLoader
from control.combat.discord_manager import DiscordManager
from control.combat.effect_manager import CombatEffectManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.item_manager import ItemManager
from control.jail_manager import JailManager
from control.settings_manager import SettingsManager
from control.user_settings_manager import UserSettingsManager
from datalayer.database import Database
from events.bot_event import BotEvent


class State(ABC):
    def __init__(self, controller: Controller, context: EncounterContext):
        self.state_type: StateType = None
        self.done: bool = False
        self.quit: bool = False
        self.next_state: StateType = None

        self.context = context
        self.controller = controller
        self.bot = controller.bot
        self.database: Database = self.controller.database
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.user_settings_manager: UserSettingsManager = self.controller.get_service(
            UserSettingsManager
        )
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
        )
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.effect_manager: CombatEffectManager = self.controller.get_service(
            CombatEffectManager
        )
        self.context_loader: ContextLoader = self.controller.get_service(ContextLoader)
        self.discord: DiscordManager = self.controller.get_service(DiscordManager)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.jail_manager: JailManager = self.controller.get_service(JailManager)
        self.common: CommonService = self.controller.get_service(CommonService)

        self.logger = self.controller.logger
        self.log_name = "Combat Engine"

    @abstractmethod
    async def startup(self):
        pass

    @abstractmethod
    async def handle(self, event: BotEvent) -> bool:
        return False

    @abstractmethod
    async def update(self):
        pass
