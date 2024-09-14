import discord

from combat.engine.states.state import State


class Game:
    def __init__(self, thread: discord.Thread, states: list[State], start_state: State):
        self.done = False
        self.states = states
        self.current_state = start_state
        self.state = self.states[self.current_state]

    def state_transition(self):
        next_state = self.state.next_state
        self.state.done = False
        self.current_state = next_state
        self.state = self.states[self.current_state]
        self.state.startup()

    def update(self):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.state_transition()
        self.state.update()

    def draw(self):
        self.state.draw(self.screen)

    def handle(self, event):
        self.state.handle(event)
        self.update()
        self.draw()
