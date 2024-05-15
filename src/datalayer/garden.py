import datetime

from events.garden_event import GardenEvent
from events.types import GardenEventType

from datalayer.types import PlantType, PlotState


class PlotModifiers:

    def __init__(
        self,
        water_events: list[GardenEvent] = None,
        last_fertilized: float = None,
        flash_bean_events: list[GardenEvent] = None,
    ):
        self.water_events = water_events
        self.last_fertilized = last_fertilized
        self.flash_bean_events = flash_bean_events


class Plant:

    SEED_EMOJI = 1238648940992401439
    SEED_EMOJI_WATERED = 1238648945408872449
    GROWING_EMOJI = 1238648939058696296
    GROWING_EMOJI_WATERED = 1238648943806517248
    READY_EMOJI = 1238648937666318406

    IMAGE_DIR = "bean"

    IMAGE_MAP = {}

    EMOJI_MAP = {}

    MODIFIER_DURATON = 0
    MODIFIER = 0

    def __init__(self, plant_type: PlantType):
        self.type = plant_type
        self.seed_hours = 0
        self.grow_hours = 0
        self.allow_modifiers = True
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
        self.emoji = self.READY_EMOJI

    def get_status(self, age: int, watered: bool) -> PlotState:
        if age <= self.seed_hours:
            return (
                PlotState.SEED_PLANTED
                if not watered and self.allow_modifiers
                else PlotState.SEED_PLANTED_WET
            )
        elif age <= self.grow_hours:
            return (
                PlotState.GROWING
                if not watered and self.allow_modifiers
                else PlotState.GROWING_WET
            )
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
        self.grow_hours = 24 * 6 - 4
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
        self.grow_hours = 24 * 10 - 4
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
        self.grow_hours = 24 * 14 - 4
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
        self.grow_hours = 24 * 8 - 4
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
        self.grow_hours = 24 * 6 - 4
        # self.seed_hours = 2
        # self.grow_hours = 10


class YellowBeanPlant(Plant):

    SEED_EMOJI = 1239500356141187174
    SEED_EMOJI_WATERED = 1239500353586724874
    GROWING_EMOJI = 1239500354941354034
    GROWING_EMOJI_WATERED = 1239500352324239381
    READY_EMOJI = 1239500357407870986
    IMAGE_DIR = "yellow_bean"

    MODIFIER_DURATON = 24 * 3
    MODIFIER = 0.5

    def __init__(self):
        super().__init__(PlantType.YELLOW_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 4 - 4
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
        self.grow_hours = 24 * 6 - 4
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
        self.grow_hours = 24 * 4 - 4
        # self.seed_hours = 2
        # self.grow_hours = 5


class FlashBeanPlant(Plant):

    SEED_EMOJI = 1240215495957811210
    SEED_EMOJI_WATERED = 1240215495957811210
    GROWING_EMOJI = 1240215495957811210
    GROWING_EMOJI_WATERED = 1240215495957811210
    READY_EMOJI = 1240215497241530430
    IMAGE_DIR = "flash_bean"

    MODIFIER_DURATON = 24 * 3
    MODIFIER = 0.5

    def __init__(self):
        super().__init__(PlantType.FLASH_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 3
        self.allow_modifiers = False

        self.IMAGE_MAP = {
            PlotState.SEED_PLANTED: f"{self.IMAGE_DIR}/planted.png",
            PlotState.SEED_PLANTED_WET: f"{self.IMAGE_DIR}/planted.png",
            PlotState.GROWING: f"{self.IMAGE_DIR}/planted.png",
            PlotState.GROWING_WET: f"{self.IMAGE_DIR}/planted.png",
            PlotState.READY: f"{self.IMAGE_DIR}/ready.png",
        }
        self.emoji = self.SEED_EMOJI


class Plot:

    EMPTY_PLOT_EMOJI = 1238648942489505864

    # TIME_MODIFIER = 60 * 60
    TIME_MODIFIER = 60

    def __init__(
        self,
        id: int,
        garden_id: int,
        x: int,
        y: int,
        plant: Plant = None,
        plant_datetime: datetime.datetime = None,
        notified: bool = False,
        modifiers: PlotModifiers = None,
    ):
        self.id = id
        self.garden_id = garden_id
        self.plant = plant
        self.plant_datetime = plant_datetime
        self.x = x
        self.y = y
        self.notified = notified
        self.modifiers = modifiers

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

        if not self.plant.allow_modifiers:
            return age

        water_events = self.modifiers.water_events
        watered_hours = 0
        if (
            water_events is not None
            and len(water_events) > 0
            and self.plant.allow_modifiers
        ):
            previous = now
            for event in water_events:
                delta = previous - event.datetime
                hours = delta.total_seconds() / self.TIME_MODIFIER
                watered_hours += min(24, hours)
                previous = event.datetime

        last_fertilized = self.modifiers.last_fertilized
        fertile_hours = 0
        if last_fertilized is not None and self.plant.allow_modifiers:
            fertilizer_active_before_plant = max(0, last_fertilized - age)
            fertilizer_active = min(last_fertilized, YellowBeanPlant.MODIFIER_DURATON)
            fertile_hours = min(age, fertilizer_active - fertilizer_active_before_plant)
            fertile_hours = fertile_hours * YellowBeanPlant.MODIFIER

        flash_bean_events = self.modifiers.flash_bean_events
        flash_bean_hours = 0
        threshold = FlashBeanPlant.MODIFIER_DURATON + self.plant.grow_hours
        if len(flash_bean_events) > 0 and self.plant.allow_modifiers:
            remove_events = {}
            for event in flash_bean_events:
                if event.garden_event_type == GardenEventType.REMOVE:
                    remove_events[event.plot_id] = event.datetime
                    continue

                delta = now - event.datetime
                last_flash_bean = delta.total_seconds() / self.TIME_MODIFIER
                if last_flash_bean > threshold:
                    continue

                last_flash_bean = delta.total_seconds() / self.TIME_MODIFIER
                flash_bean_active_before_plant = max(0, last_flash_bean - age)

                max_duration = FlashBeanPlant.MODIFIER_DURATON

                # In case Flash Bean was removed early
                if event.plot_id in remove_events:
                    duration_delta = remove_events[event.plot_id] - event.datetime
                    max_duration = min(
                        max_duration,
                        duration_delta.total_seconds() / self.TIME_MODIFIER,
                    )
                    del remove_events[event.plot_id]

                flash_bean_active = min(last_flash_bean, max_duration)
                hours = max(
                    0, min(age, flash_bean_active - flash_bean_active_before_plant)
                )
                flash_bean_hours += hours * FlashBeanPlant.MODIFIER

        return int(age + watered_hours + fertile_hours + flash_bean_hours)

    def is_watered(self) -> bool:
        hours = self.get_hours_since_last_water()
        if hours is None:
            return False
        return self.get_hours_since_last_water() < 24

    def get_hours_since_last_water(self) -> int | None:
        if self.modifiers.water_events is None or len(self.modifiers.water_events) <= 0:
            return None

        now = datetime.datetime.now()
        delta = now - self.modifiers.water_events[0].datetime
        hours = int(delta.total_seconds() / self.TIME_MODIFIER)
        return hours

    def get_hours_since_last_flash_bean(self) -> int | None:
        if len(self.modifiers.flash_bean_events) <= 0:
            return None

        now = datetime.datetime.now()
        delta = now - self.modifiers.flash_bean_events[0].datetime
        hours = int(delta.total_seconds() / self.TIME_MODIFIER)
        return hours

    def get_active_flash_bean_count(self) -> int | None:
        if len(self.modifiers.flash_bean_events) <= 0:
            return 0
        count = 0
        now = datetime.datetime.now()
        remove_events = {}
        for event in self.modifiers.flash_bean_events:
            if event.garden_event_type == GardenEventType.REMOVE:
                remove_events[event.plot_id] = event.datetime
                continue
            delta = now - event.datetime
            flash_bean_age = delta.total_seconds() / self.TIME_MODIFIER

            max_duration = FlashBeanPlant.MODIFIER_DURATON
            if event.plot_id in remove_events:
                duration_delta = remove_events[event.plot_id] - event.datetime
                max_duration = min(
                    max_duration,
                    duration_delta.total_seconds() / self.TIME_MODIFIER,
                )
                del remove_events[event.plot_id]

            if flash_bean_age <= max_duration:
                count += 1

        return count

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
            case PlantType.FLASH_BEAN:
                return FlashBeanPlant()
        return None
