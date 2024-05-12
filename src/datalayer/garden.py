import datetime

from events.garden_event import GardenEvent

from datalayer.types import PlantType, PlotState


class Plant:

    IMAGE_MAP = {}
    EMOJI_MAP = {}

    def __init__(self, plant_type: PlantType):
        self.type = plant_type
        self.seed_hours = 0
        self.grow_hours = 0

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

    IMAGE_MAP = {
        PlotState.SEED_PLANTED: "bean/planted.png",
        PlotState.SEED_PLANTED_WET: "bean/planted_wet.png",
        PlotState.GROWING: "bean/growing.png",
        PlotState.GROWING_WET: "bean/growing_wet.png",
        PlotState.READY: "bean/ready.png",
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
        # self.seed_hours = 1
        # self.grow_hours = 10


class RareBeanPlant(Plant):

    SEED_EMOJI = 1239252755567218709
    SEED_EMOJI_WATERED = 1239252752723607583
    GROWING_EMOJI = 1239252754321510430
    GROWING_EMOJI_WATERED = 1239252750877982771
    READY_EMOJI = 1239252756884099183

    IMAGE_MAP = {
        PlotState.SEED_PLANTED: "rare_bean/planted.png",
        PlotState.SEED_PLANTED_WET: "rare_bean/planted_wet.png",
        PlotState.GROWING: "rare_bean/growing.png",
        PlotState.GROWING_WET: "rare_bean/growing_wet.png",
        PlotState.READY: "rare_bean/ready.png",
    }

    EMOJI_MAP = {
        PlotState.SEED_PLANTED: SEED_EMOJI,
        PlotState.SEED_PLANTED_WET: SEED_EMOJI_WATERED,
        PlotState.GROWING: GROWING_EMOJI,
        PlotState.GROWING_WET: GROWING_EMOJI_WATERED,
        PlotState.READY: READY_EMOJI,
    }

    def __init__(self):
        super().__init__(PlantType.RARE_BEAN)
        self.seed_hours = 24 * 2
        self.grow_hours = 24 * 12
        # self.seed_hours = 1
        # self.grow_hours = 10


class CrystalBeanPlant(Plant):

    SEED_EMOJI = 1239224172853592098
    SEED_EMOJI_WATERED = 1239224176162635859
    GROWING_EMOJI = 1239224174782976051
    GROWING_EMOJI_WATERED = 1239224178582880297
    READY_EMOJI = 1239224180164005948

    IMAGE_MAP = {
        PlotState.SEED_PLANTED: "crystal_bean/planted.png",
        PlotState.SEED_PLANTED_WET: "crystal_bean/planted_wet.png",
        PlotState.GROWING: "crystal_bean/growing.png",
        PlotState.GROWING_WET: "crystal_bean/growing_wet.png",
        PlotState.READY: "crystal_bean/ready.png",
    }

    EMOJI_MAP = {
        PlotState.SEED_PLANTED: SEED_EMOJI,
        PlotState.SEED_PLANTED_WET: SEED_EMOJI_WATERED,
        PlotState.GROWING: GROWING_EMOJI,
        PlotState.GROWING_WET: GROWING_EMOJI_WATERED,
        PlotState.READY: READY_EMOJI,
    }

    def __init__(self):
        super().__init__(PlantType.CRYSTAL_BEAN)
        self.seed_hours = 24 * 2
        self.grow_hours = 24 * 14
        # self.seed_hours = 1
        # self.grow_hours = 10


class SpeedBeanPlant(Plant):

    SEED_EMOJI = 1239222810015174718
    SEED_EMOJI_WATERED = 1239222813550841988
    GROWING_EMOJI = 1239222811344502855
    GROWING_EMOJI_WATERED = 1239222815044009984
    READY_EMOJI = 1239222816641913033

    IMAGE_MAP = {
        PlotState.SEED_PLANTED: "speed_bean/planted.png",
        PlotState.SEED_PLANTED_WET: "speed_bean/planted_wet.png",
        PlotState.GROWING: "speed_bean/growing.png",
        PlotState.GROWING_WET: "speed_bean/growing_wet.png",
        PlotState.READY: "speed_bean/ready.png",
    }

    EMOJI_MAP = {
        PlotState.SEED_PLANTED: SEED_EMOJI,
        PlotState.SEED_PLANTED_WET: SEED_EMOJI_WATERED,
        PlotState.GROWING: GROWING_EMOJI,
        PlotState.GROWING_WET: GROWING_EMOJI_WATERED,
        PlotState.READY: READY_EMOJI,
    }

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

    IMAGE_MAP = {
        PlotState.SEED_PLANTED: "box_bean/planted.png",
        PlotState.SEED_PLANTED_WET: "box_bean/planted_wet.png",
        PlotState.GROWING: "box_bean/growing.png",
        PlotState.GROWING_WET: "box_bean/growing_wet.png",
        PlotState.READY: "box_bean/ready.png",
    }

    EMOJI_MAP = {
        PlotState.SEED_PLANTED: SEED_EMOJI,
        PlotState.SEED_PLANTED_WET: SEED_EMOJI_WATERED,
        PlotState.GROWING: GROWING_EMOJI,
        PlotState.GROWING_WET: GROWING_EMOJI_WATERED,
        PlotState.READY: READY_EMOJI,
    }

    def __init__(self):
        super().__init__(PlantType.BOX_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 4
        # self.seed_hours = 1
        # self.grow_hours = 5


class CatBeanPlant(Plant):

    SEED_EMOJI = 1239283615247106159
    SEED_EMOJI_WATERED = 1239283612365488198
    GROWING_EMOJI = 1239283617306513550
    GROWING_EMOJI_WATERED = 1239283611077972018
    READY_EMOJI = 1239283613984362548

    IMAGE_MAP = {
        PlotState.SEED_PLANTED: "cat_bean/planted.png",
        PlotState.SEED_PLANTED_WET: "cat_bean/planted_wet.png",
        PlotState.GROWING: "cat_bean/growing.png",
        PlotState.GROWING_WET: "cat_bean/growing_wet.png",
        PlotState.READY: "cat_bean/ready.png",
    }

    EMOJI_MAP = {
        PlotState.SEED_PLANTED: SEED_EMOJI,
        PlotState.SEED_PLANTED_WET: SEED_EMOJI_WATERED,
        PlotState.GROWING: GROWING_EMOJI,
        PlotState.GROWING_WET: GROWING_EMOJI_WATERED,
        PlotState.READY: READY_EMOJI,
    }

    def __init__(self):
        super().__init__(PlantType.CAT_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 3
        # self.seed_hours = 2
        # self.grow_hours = 10


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
        notified: bool = False,
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
        # age = int(delta.total_seconds() / 60)
        age = int(delta.total_seconds() / 60 / 60)

        if len(self.water_events) <= 0:
            return age

        watered_hours = 0
        previous = now
        for event in self.water_events:
            delta = previous - event.datetime
            # hours = int(delta.total_seconds() / 60)
            hours = int(delta.total_seconds() / 60 / 60)
            watered_hours += min(24, hours)
            previous = event.datetime

        return age + watered_hours

    def watered(self):
        if len(self.water_events) <= 0:
            return False

        now = datetime.datetime.now()
        delta = now - self.water_events[0].datetime
        # hours = int(delta.total_seconds() / 60)
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
        return None
