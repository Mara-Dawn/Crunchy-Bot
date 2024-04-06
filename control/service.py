from abc import ABC, abstractmethod

from control import Controller
from events import BotEvent


class Service(ABC):

    def __init__(self):
        self.controller = None

    def register_controller(self, controller: Controller) -> None:
        self.controller = controller

    @abstractmethod
    async def listen_for_event(self, event: BotEvent) -> None:
        pass
