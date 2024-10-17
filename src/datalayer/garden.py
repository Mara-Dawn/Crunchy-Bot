import datetime

from combat.types import UnlockableFeature
from datalayer.types import PlantType, PlotState
from events.garden_event import GardenEvent
from events.types import GardenEventType


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
        if self.water_events is None:
            self.water_events = []
        if self.flash_bean_events is None:
            self.flash_bean_events = []


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

    def get_status(self, age: float, watered: bool) -> PlotState:
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

    def get_status_image(self, age: float, watered: bool) -> str:
        return self.IMAGE_MAP[self.get_status(age, watered)]

    def get_status_emoji(self, age: float, watered: bool):
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
    MODIFIER = 1

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


class KeyBeanPlant(Plant):

    SEED_EMOJI = 1282316870782947399
    SEED_EMOJI_WATERED = 1282316867415048193
    GROWING_EMOJI = 1282316875807854634
    GROWING_EMOJI_WATERED = 1282316872682831942
    READY_EMOJI = 1282316862654513283
    IMAGE_DIR = "key_bean"

    def __init__(self):
        super().__init__(PlantType.KEY_BEAN)
        self.seed_hours = 24
        self.grow_hours = 24 * 4 - 4


class FlashBeanPlant(Plant):

    SEED_EMOJI = 1240215495957811210
    SEED_EMOJI_WATERED = 1240215495957811210
    GROWING_EMOJI = 1240215495957811210
    GROWING_EMOJI_WATERED = 1240215495957811210
    READY_EMOJI = 1240215497241530430
    IMAGE_DIR = "flash_bean"

    MODIFIER_DURATON = 24 * 3
    MODIFIER = 1

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

    TIME_MODIFIER = 60 * 60
    # TIME_MODIFIER = 60

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
        if self.modifiers is None:
            self.modifiers = PlotModifiers()

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

    def get_age(self) -> float:
        if self.plant is None:
            return 0

        now = datetime.datetime.now()
        delta = now - self.plant_datetime
        age = delta.total_seconds() / self.TIME_MODIFIER

        if not self.plant.allow_modifiers:
            return age

        watered_hours = self.get_watered_hours()
        fertile_hours = self.get_fertilizer_hours()
        flash_bean_data = self.get_flash_bean_hours()

        flash_bean_hours = 0
        for hours in flash_bean_data:
            flash_bean_hours += hours

        return age + watered_hours + fertile_hours + flash_bean_hours

    def is_watered(self) -> bool:
        hours = self.get_hours_since_last_water()
        if hours is None:
            return False
        return hours < 24

    def get_hours_since_last_water(self) -> float | None:
        if (
            self.modifiers is None
            or self.modifiers.water_events is None
            or len(self.modifiers.water_events) <= 0
        ):
            return None

        now = datetime.datetime.now()
        delta = now - self.modifiers.water_events[0].datetime
        hours = delta.total_seconds() / self.TIME_MODIFIER
        return hours

    def get_dry_datetime(self) -> datetime.datetime:
        if (
            self.modifiers is None
            or self.modifiers.water_events is None
            or len(self.modifiers.water_events) <= 0
        ):
            return None

        latest = self.modifiers.water_events[0].datetime
        return latest + datetime.timedelta(hours=24)

    def get_hours_since_last_flash_bean(self) -> float | None:
        if self.modifiers is None or len(self.modifiers.flash_bean_events) <= 0:
            return None

        now = datetime.datetime.now()
        delta = now - self.modifiers.flash_bean_events[0].datetime
        hours = delta.total_seconds() / self.TIME_MODIFIER
        return hours

    def get_active_flash_bean_count(self) -> int | None:
        if self.modifiers is None or len(self.modifiers.flash_bean_events) <= 0:
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

    def get_watered_hours(self) -> float:
        now = datetime.datetime.now()
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

        return watered_hours

    def get_fertilizer_hours(self) -> float:
        now = datetime.datetime.now()
        delta = now - self.plant_datetime
        age = delta.total_seconds() / self.TIME_MODIFIER

        last_fertilized = self.modifiers.last_fertilized
        fertile_hours = 0
        if last_fertilized is not None and self.plant.allow_modifiers:
            fertilizer_active_before_plant = max(0, last_fertilized - age)
            fertilizer_active = min(last_fertilized, YellowBeanPlant.MODIFIER_DURATON)
            fertile_hours = max(
                0, min(age, fertilizer_active - fertilizer_active_before_plant)
            )
            fertile_hours = fertile_hours * YellowBeanPlant.MODIFIER

        return fertile_hours

    def get_flash_bean_hours(self, remaining_growth: bool = False) -> list[float]:
        now = datetime.datetime.now()
        delta = now - self.plant_datetime
        age = delta.total_seconds() / self.TIME_MODIFIER

        flash_bean_events = self.modifiers.flash_bean_events
        flash_bean_hours = []
        threshold = FlashBeanPlant.MODIFIER_DURATON + self.plant.grow_hours
        if len(flash_bean_events) > 0 and self.plant.allow_modifiers:
            remove_events = {}
            for event in flash_bean_events:
                if (
                    event.garden_event_type == GardenEventType.REMOVE
                    or event.garden_event_type == GardenEventType.HARVEST
                ):
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

                if remaining_growth:
                    remaining = max(0, max_duration - flash_bean_active)
                    if remaining > 0:
                        flash_bean_hours.append(remaining * FlashBeanPlant.MODIFIER)
                        continue

                hours = max(
                    0, min(age, flash_bean_active - flash_bean_active_before_plant)
                )
                if hours > 0:
                    flash_bean_hours.append(hours * FlashBeanPlant.MODIFIER)

        return flash_bean_hours

    def get_estimated_harvest_datetime(self) -> datetime.datetime:
        if self.plant is None:
            return None

        if self.get_status() == PlotState.READY:
            return None

        now = datetime.datetime.now()
        age = self.get_age()
        hours_until_ready = self.plant.grow_hours - age

        if not self.plant.allow_modifiers:
            ready_datetime = now + datetime.timedelta(hours=hours_until_ready)
            return ready_datetime

        modifiers = []

        projected_water_hours = hours_until_ready
        if projected_water_hours > 0:
            modifiers.append((projected_water_hours, 1))

        projected_fertile_hours = 0
        last_fertilized = self.modifiers.last_fertilized
        if last_fertilized is not None:
            fertilizer_left = YellowBeanPlant.MODIFIER_DURATON - last_fertilized
            projected_fertile_hours = max(0, fertilizer_left)
        if projected_fertile_hours > 0:
            modifiers.append((projected_fertile_hours, YellowBeanPlant.MODIFIER))

        flash_bean_hours = self.get_flash_bean_hours(remaining_growth=True)
        for hours in flash_bean_hours:
            hours_normalized = hours / FlashBeanPlant.MODIFIER
            if hours_normalized > 0:
                modifiers.append((hours_normalized, FlashBeanPlant.MODIFIER))

        remaining_hours = 0
        while hours_until_ready > 0:
            shortest = None

            if len(modifiers) <= 0:
                remaining_hours += hours_until_ready
                break

            # modifiers is a list of tuples (avtive_hours, buff_modifier)
            # active hours is the time the buff will be active from this point onward
            # find shortest active_hours of all buffs to determine interval where all buffs are active
            for hours, _ in modifiers:
                if shortest is None or shortest > hours:
                    shortest = hours

            # calculate the total modifier for the previously determined interval
            new_modifiers = []
            modifier_sum = 1
            for hours, modifier in modifiers:
                modifier_sum += modifier
                if hours > shortest:
                    remaining = hours - shortest
                    new_modifiers.append((remaining, modifier))

            shortest_total_value = shortest * modifier_sum

            if shortest_total_value < hours_until_ready:
                # if plant is not ready after shortest inverval passed
                # remove shortest interval from modifier list
                # add the normalized interval to remaining grow hours
                # find next shortest interval starting after the previous shortest
                hours_until_ready -= shortest_total_value
                modifiers = new_modifiers
                remaining_hours += shortest / modifier_sum
                continue

            # plant will be ready within shortest interval:
            # sum of modifiers will be active for the entire remaining duration
            remaining_hours += hours_until_ready / modifier_sum
            hours_until_ready = 0

        ready_datetime = now + datetime.timedelta(hours=remaining_hours)
        return ready_datetime

    def empty(self):
        return self.plant is None


class UserGarden:
    MAX_PLOTS = 12
    PLOT_UNLOCKS = {
        UnlockableFeature.GARDEN_1: 3,
        UnlockableFeature.GARDEN_2: 6,
        UnlockableFeature.GARDEN_3: 9,
        UnlockableFeature.GARDEN_4: 12,
    }
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
        (3, 0),
        (3, 1),
        (3, 2),
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

    def get_plot_number(self, plot: Plot):
        return self.PLOT_ORDER.index((plot.x, plot.y)) + 1

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

    def get_next_harvest_plot(self) -> Plot:
        soonest_plot = None
        timestamp = None

        for plot in self.plots:
            if plot.plant is None:
                continue
            if plot.get_status() == PlotState.READY:
                continue
            harvest = plot.get_estimated_harvest_datetime()
            if harvest is None:
                continue
            if timestamp is None or timestamp > harvest:
                timestamp = harvest
                soonest_plot = plot

        return soonest_plot

    def get_next_water_plot(self) -> Plot:
        soonest_plot = None
        hours = 0

        for plot in self.plots:
            if plot.plant is None:
                continue
            if plot.get_status() == PlotState.READY:
                continue
            if not plot.plant.allow_modifiers:
                continue
            last_watered = plot.get_hours_since_last_water()
            if last_watered is not None and last_watered > hours:
                hours = last_watered
                soonest_plot = plot

        return soonest_plot

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
            case PlantType.KEY_BEAN:
                return KeyBeanPlant()
        return None
