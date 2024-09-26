import os
import random
from typing import Any

from discord.ext import commands
from imgurpython import ImgurClient

from combat.encounter import Encounter
from combat.enemies.types import EnemyType
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent


class ImgurManager(Service):

    KEY = "IMGUR_API_KEY"
    SECRET = "IMGUR_API_SECRET"

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.log_name = "Imgur"

        self.token = os.environ.get(self.KEY)

        self.secret = os.environ.get(self.SECRET)

        self.client = ImgurClient(self.token, self.secret)

        self.image_cache: dict[Any, str] = {}

    async def listen_for_event(self, event: BotEvent) -> str:
        pass

    async def get_random_encounter_image(self, encounter: Encounter):
        match encounter.enemy_type:
            case EnemyType.SCRIBBLER:
                return await self.get_random_album_image(
                    ["f4pqgvP", "Wygs1pV"], encounter.id
                )
        return None

    async def get_random_album_image(self, album_ids: list[str], seed: Any):
        if seed is None:
            seed = random.randint(-9999, -1)

        if seed in self.image_cache:
            return self.image_cache[seed]
        images = []
        try:
            for album_id in album_ids:
                images.extend(self.client.get_album_images(album_id))
        except:  # noqa: E722
            return None

        if images is None or len(images) <= 0:
            return None

        choice = random.choice(images)

        self.image_cache[seed] = choice.link
        return choice.link
