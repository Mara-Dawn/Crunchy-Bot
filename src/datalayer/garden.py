import datetime

from events.garden_event import GardenEvent

from datalayer.types import PlantType, PlotState


class Plant:

    SEED_EMOJI = 1238648940992401439
    SEED_EMOJI_WATERED = 1238648945408872449
    GROWING_EMOJI = 1238648939058696296
    GROWING_EMOJI_WATERED = 1238648943806517248
    READY_EMOJI = 1238648937666318406

    IMAGE_DIR = "bean"

    IMAGE_MAP = {}

    EMOJI_MAP = {}

    def __init__(self, plant_type: PlantType):
        self.type = plant_type
        self.seed_hours = 0
        self.grow_hours = 0
        self.IMAGE_MAP = {
            PlotState.SEED_PLANTED: f"{self.IMAGE_DIR}/planted.png",
            PlotState.SEED_PLANTED_WET: f"{self.IMAGE_DIR}/planted_wet.png",
            PlotState.GROWING: f"{self.IMAGE_DIR}/growing.png",
            PlotState.GROWING_WET: f"{self.IMAGE_DIR}/growing_wet.png",
            PlotState.READY: f"{self.IMAGE_DIR}/ready.png",
        }

        self.EMOJI_MAP = {
            PlotState.SEED_PLANTED: self.SEED_EMOJI,
            PlotState.SEED_PLANTED_WET: self.SEED_EMOJI_WATERED,
            PlotState.GROWING: self.GROWING_EMOJI,
            PlotState.GROWING_WET: self.GROWING_EMOJI_WATERED,
            PlotState.READY: self.READY_EMOJI,
        }

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


class BeanPlant(Plant):

    SEED_EMOJI = 1238648940992401439
    SEED_EMOJI_WATERED = 1238648945408872449
    GROWING_EMOJI = 1238648939058696296
    GROWING_EMOJI_WATERED = 1238648943806517248
    READY_EMOJI = 1238648937666318406
    IMAGE_DIR = "bean"

    def __init__(self):
        super().__init__(PlantType.BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 6 - 2
        # self.seed_hours = 1
        # self.grow_hours = 10


class RareBeanPlant(Plant):

    SEED_EMOJI = 1239252755567218709
    SEED_EMOJI_WATERED = 1239252752723607583
    GROWING_EMOJI = 1239252754321510430
    GROWING_EMOJI_WATERED = 1239252750877982771
    READY_EMOJI = 1239252756884099183
    IMAGE_DIR = "rare_bean"

    def __init__(self):
        super().__init__(PlantType.RARE_BEAN)
        self.seed_hours = 24 * 2
        self.grow_hours = 24 * 10 - 2
        # self.seed_hours = 1
        # self.grow_hours = 10


class CrystalBeanPlant(Plant):

    SEED_EMOJI = 1239224172853592098
    SEED_EMOJI_WATERED = 1239224176162635859
    GROWING_EMOJI = 1239224174782976051
    GROWING_EMOJI_WATERED = 1239224178582880297
    READY_EMOJI = 1239224180164005948
    IMAGE_DIR = "crystal_bean"

    def __init__(self):
        super().__init__(PlantType.CRYSTAL_BEAN)
        self.seed_hours = 24 * 2
        self.grow_hours = 24 * 14 - 2
        # self.seed_hours = 1
        # self.grow_hours = 10


class SpeedBeanPlant(Plant):

    SEED_EMOJI = 1239222810015174718
    SEED_EMOJI_WATERED = 1239222813550841988
    GROWING_EMOJI = 1239222811344502855
    GROWING_EMOJI_WATERED = 1239222815044009984
    READY_EMOJI = 1239222816641913033
    IMAGE_DIR = "speed_bean"

    def __init__(self):
        super().__init__(PlantType.SPEED_BEAN)
        self.seed_hours = 2
        self.grow_hours = 6
        # self.seed_hours = 1
        # self.grow_hours = 5


class BoxBeanPlant(Plant):

    SEED_EMOJI = 1239271629000015924
    SEED_EMOJI_WATERED = 1239271627984732271
    GROWING_EMOJI = 1239271630656635011
    GROWING_EMOJI_WATERED = 1239271626475044954
    READY_EMOJI = 1239271631516598374
    IMAGE_DIR = "box_bean"

    def __init__(self):
        super().__init__(PlantType.BOX_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 8 - 2
        # self.seed_hours = 1
        # self.grow_hours = 5


class CatBeanPlant(Plant):

    SEED_EMOJI = 1239283615247106159
    SEED_EMOJI_WATERED = 1239283612365488198
    GROWING_EMOJI = 1239283617306513550
    GROWING_EMOJI_WATERED = 1239283611077972018
    READY_EMOJI = 1239283613984362548
    IMAGE_DIR = "cat_bean"

    def __init__(self):
        super().__init__(PlantType.CAT_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 6 - 2
        # self.seed_hours = 2
        # self.grow_hours = 10


class YellowBeanPlant(Plant):

    SEED_EMOJI = 1239500356141187174
    SEED_EMOJI_WATERED = 1239500353586724874
    GROWING_EMOJI = 1239500354941354034
    GROWING_EMOJI_WATERED = 1239500352324239381
    READY_EMOJI = 1239500357407870986
    IMAGE_DIR = "yellow_bean"

    FERTILE_TIME = 24 * 3
    # FERTILE_TIME = 12

    def __init__(self):
        super().__init__(PlantType.YELLOW_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 4 - 2
        # self.seed_hours = 2
        # self.grow_hours = 10


class GhostBeanPlant(Plant):

    SEED_EMOJI = 1239503898713002055
    SEED_EMOJI_WATERED = 1239503895517069422
    GROWING_EMOJI = 1239503897471483914
    GROWING_EMOJI_WATERED = 1239503893592014900
    READY_EMOJI = 1239503901091172382
    IMAGE_DIR = "ghost_bean"

    def __init__(self):
        super().__init__(PlantType.GHOST_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 6 - 2
        # self.seed_hours = 2
        # self.grow_hours = 5


class BakedBeanPlant(Plant):

    SEED_EMOJI = 1239505232421982262
    SEED_EMOJI_WATERED = 1239505228634521662
    GROWING_EMOJI = 1239505230635339817
    GROWING_EMOJI_WATERED = 1239505226969645099
    READY_EMOJI = 1239505234435244042
    IMAGE_DIR = "baked_bean"

    def __init__(self):
        super().__init__(PlantType.BAKED_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 4 - 2
        # self.seed_hours = 2
        # self.grow_hours = 5


class Plot:

    EMPTY_PLOT_EMOJI = 1238648942489505864

    TIME_MODIFIER = 60 * 60

    def __init__(
        self,
        id: int,
        garden_id: int,
        x: int,
        y: int,
        plant: Plant = None,
        plant_datetime: datetime.datetime = None,
        water_events: list[GardenEvent] = None,
        notified: bool = False,
        last_fertilized_event: GardenEvent = None,
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
        self.notified = notified
        self.last_fertilized_event = last_fertilized_event

    def get_status_emoji(self):
        if self.empty():
            return self.EMPTY_PLOT_EMOJI
        return self.plant.get_status_emoji(self.get_age(), self.is_watered())

    def get_status_image(self) -> str:
        if self.empty():
            return "plot_empty.png"
        return self.plant.get_status_image(self.get_age(), self.is_watered())

    def get_status(self) -> PlotState:
        if self.empty():
            return PlotState.EMPTY
        return self.plant.get_status(self.get_age(), self.is_watered())

    def get_age(self) -> int:
        if self.plant is None:
            return 0

        now = datetime.datetime.now()
        delta = now - self.plant_datetime
        age = delta.total_seconds() / self.TIME_MODIFIER

        if len(self.water_events) <= 0:
            return int(age)

        watered_hours = 0
        previous = now
        for event in self.water_events:
            delta = previous - event.datetime
            hours = delta.total_seconds() / self.TIME_MODIFIER
            watered_hours += min(24, hours)
            previous = event.datetime

        last_fertilized = self.hours_since_last_fertilized()
        fertile_hours = 0
        if last_fertilized is not None:
            fertile_hours = max(0, YellowBeanPlant.FERTILE_TIME - last_fertilized)
            fertile_hours = min(age, fertile_hours)
            fertile_hours = fertile_hours * 0.5

        return int(age + watered_hours + fertile_hours)

    def is_watered(self) -> bool:
        hours = self.hours_since_last_water()
        if hours is None:
            return False
        return self.hours_since_last_water() < 24

    def hours_since_last_water(self) -> int | None:
        if len(self.water_events) <= 0:
            return None

        now = datetime.datetime.now()
        delta = now - self.water_events[0].datetime
        hours = int(delta.total_seconds() / self.TIME_MODIFIER)
        return hours

    def hours_since_last_fertilized(self) -> int | None:
        if self.last_fertilized_event is None:
            return None

        now = datetime.datetime.now()
        delta = now - self.last_fertilized_event.datetime
        hours = int(delta.total_seconds() / self.TIME_MODIFIER)
        return hours

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

    def notification_pending_plots(self, no_spam: bool = True) -> list[Plot]:
        plots = []
        for plot in self.plots:
            if plot.get_status() == PlotState.READY:
                if not plot.notified:
                    plots.append(plot)
                if plot.notified and no_spam:
                    return []
        return plots

    @staticmethod
    def get_plant_by_type(plant_type: PlantType):
        match plant_type:
            case PlantType.BEAN:
                return BeanPlant()
            case PlantType.RARE_BEAN:
                return RareBeanPlant()
            case PlantType.SPEED_BEAN:
                return SpeedBeanPlant()
            case PlantType.BOX_BEAN:
                return BoxBeanPlant()
            case PlantType.CAT_BEAN:
                return CatBeanPlant()
            case PlantType.CRYSTAL_BEAN:
                return CrystalBeanPlant()
            case PlantType.YELLOW_BEAN:
                return YellowBeanPlant()
            case PlantType.GHOST_BEAN:
                return GhostBeanPlant()
            case PlantType.BAKED_BEAN:
                return BakedBeanPlant()
        return None
