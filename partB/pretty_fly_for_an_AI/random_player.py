import numpy as np
import random
from pretty_fly_for_an_AI import state as s

class RandomPlayer:
    """ This player makes moves randomly """
    def __init__(self, color):
        
        
        self.state = s.State.create_start_state(color)

        self.color = color

    def action(self):
        #pylint: disable=unused-variable
        action_id, next_state = random.choice(list(self.state.next_states(opponent=False)))
        return action_id

    def update(self, color, action):
        
        action_type, data = action[0], action[1:]

        #check if this is an opponents move
        opponent = self.color != color

        if action_type == s.MOVE_ACTION:
            n, sp, ep = data
            self.state = self.state.move(n, s.ptoi(*sp), s.ptoi(*ep), opponent)

        else:
            pos = data[0]
            self.state = self.state.boom(s.ptoi(*pos))
            