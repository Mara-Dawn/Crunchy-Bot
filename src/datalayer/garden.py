import datetime
from abc import ABC, abstractmethod

from events.garden_event import GardenEvent

from datalayer.types import PlantType, PlotState


class Plant(ABC):

    def __init__(self, plant_type: PlantType):
        self.type = plant_type

    @abstractmethod
    def get_status_emoji(self, age: int):
        pass


class BeanPlant(Plant):

    SEED_EMOJI = 1238648940992401439
    SEED_EMOJI_WATERED = 1238648945408872449
    GROWING_EMOJI = 1238648939058696296
    GROWING_EMOJI_WATERED = 1238648943806517248
    READY_EMOJI = 1238648937666318406

    IMAGE_MAP = {
        PlotState.SEED_PLANTED: "bean_planted.png",
        PlotState.SEED_PLANTED_WET: "bean_planted_wet.png",
        PlotState.GROWING: "bean_growing.png",
        PlotState.GROWING_WET: "bean_growing_wet.png",
        PlotState.READY: "bean_ready.png",
    }

    EMOJI_MAP = {
        PlotState.SEED_PLANTED: SEED_EMOJI,
        PlotState.SEED_PLANTED_WET: SEED_EMOJI_WATERED,
        PlotState.GROWING: GROWING_EMOJI,
        PlotState.GROWING_WET: GROWING_EMOJI_WATERED,
        PlotState.READY: READY_EMOJI,
    }

    def __init__(self):
        super().__init__(PlantType.BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 6

    def get_status(self, age: int, watered: bool) -> PlotState:
        if age <= self.seed_hours:
            return PlotState.SEED_PLANTED if not watered else PlotState.SEED_PLANTED_WET
        elif age <= self.grow_hours:
            return PlotState.GROWING if not watered else PlotState.GROWING_WET
        else:
            return PlotState.READY

    def get_status_image(self, age: int, watered: bool) -> str:
        return self.IMAGE_MAP[self.get_status(age, watered)]

    def get_status_emoji(self, age: int, watered: bool):
        return self.EMOJI_MAP[self.get_status(age, watered)]


class Plot:

    EMPTY_PLOT_EMOJI = 1238648942489505864

    def __init__(
        self,
        id: int,
        garden_id: int,
        x: int,
        y: int,
        plant: Plant = None,
        plant_datetime: datetime.datetime = None,
        water_events: list[GardenEvent] = None,
    ):
        self.id = id
        self.garden_id = garden_id
        self.plant = plant
        self.water_events = water_events
        if self.water_events is None:
            self.water_events = []
        self.plant_datetime = plant_datetime
        self.x = x
        self.y = y

    def get_status_emoji(self):
        if self.empty():
            return self.EMPTY_PLOT_EMOJI
        return self.plant.get_status_emoji(self.get_age(), self.watered())

    def get_status_image(self) -> str:
        if self.empty():
            return "plot_empty.png"
        return self.plant.get_status_image(self.get_age(), self.watered())

    def get_status(self) -> PlotState:
        if self.empty():
            return PlotState.EMPTY
        return self.plant.get_status(self.get_age(), self.watered())

    def get_age(self) -> int:
        if self.plant is None:
            return 0

        now = datetime.datetime.now()
        delta = now - self.plant_datetime
        age = int(delta.total_seconds() / 60 / 60)

        if len(self.water_events) <= 0:
            return age

        watered_hours = 0
        previous = now
        for event in self.water_events:
            delta = previous - event.datetime
            hours = int(delta.total_seconds() / 60 / 60)
            watered_hours += min(24, hours)
            previous = event.datetime

        return age + watered_hours

    def watered(self):
        if len(self.water_events) <= 0:
            return False

        now = datetime.datetime.now()
        delta = now - self.water_events[0].datetime
        hours = int(delta.total_seconds() / 60 / 60)
        return hours < 24

    def empty(self):
        return self.plant is None


class UserGarden:
    MAX_PLOTS = 9
    PLOT_ORDER = [
        (0, 0),
        (1, 0),
        (2, 0),
        (0, 1),
        (1, 1),
        (2, 1),
        (0, 2),
        (1, 2),
        (2, 2),
    ]

    def __init__(
        self,
        id: int,
        guild_id: int,
        member_id: int,
        plots: list[Plot],
        user_seeds: dict[PlantType, int],
    ):
        self.id = id
        self.guild_id = guild_id
        self.member_id = member_id
        self.plots = plots
        self.user_seeds = user_seeds

    def get_plot(self, x: int, y: int) -> Plot:
        for plot in self.plots:
            if plot.x == x and plot.y == y:
                return plot
        return None

    def get_plot_status(self, x: int, y: int) -> PlotState:
        plot = self.get_plot(x, y)
        if plot is None:
            return PlotState.EMPTY
        return plot.get_status()

    @staticmethod
    def get_plant_by_type(plant_type: PlantType):
        match plant_type:
            case PlantType.BEAN:
                return BeanPlant()
        return None
