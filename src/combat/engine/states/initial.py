from combat.engine.states.state import State
from combat.engine.types import EncounterState


class Initial(State):
    def __init__(self):
        self.state_type: EncounterState = EncounterState.INITIAL
        self.done = False
        self.quit = False
        self.next_state = None

    def startup(self):
        pass

    def get_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass
