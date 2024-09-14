from combat.engine.types import EncounterState


class State:
    def __init__(self):
        self.state_type: EncounterState = None
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
