import numpy as np
from pretty_fly_for_an_AI import state 
from pretty_fly_for_an_AI.minimax import alpha_beta_search as minimax
from pretty_fly_for_an_AI.minimax import alpha_beta_search_ml as minimax_ml
from pretty_fly_for_an_AI.state_logging import StateLogger
from pretty_fly_for_an_AI.evaluation import reward

from collections import defaultdict as dd
from math import ceil

WEIGHTS_FILE = "./pretty_fly_for_an_AI/weights.npy"

class Player:
    minimax_depth = 3

    weights = np.load(WEIGHTS_FILE)

    ev = lambda state : reward(state, Player.weights)

    def __init__(self, color):
        
        self.state = state.create_start_state(color)

        self.color = color

    def action(self):
        
        return minimax(self.state, depth=Player.minimax_depth, ev=Player.ev)

    def update(self, color, action):
        

        action_type, data = action[0], action[1:]

        # check if this is an opponents move
        opponent = self.color != color

        if action_type == state.MOVE_ACTION:

            n, sp, ep = data
            self.state = state.move(self.state, n, state.ptoi(*sp), state.ptoi(*ep), opponent)
        else:

            pos = data[0]
            self.state = state.boom(self.state, state.ptoi(*pos))

class LearnerPlayer:
    
    minimax_depth = 3

    weights = np.load(WEIGHTS_FILE)
    
    ev = lambda state : reward(state, LearnerPlayer.weights)

    def __init__(self, color):

        self.state = state.create_start_state(color)

        self.logger = StateLogger()

        self.color = color

    def action(self):

        return minimax_ml(self.state, depth=LearnerPlayer.minimax_depth, ev=LearnerPlayer.ev, ml_logger=self.logger)

    def update(self, color, action):

        action_type, data = action[0], action[1:]

        # check if this is an opponents move
        opponent = self.color != color

        if action_type == state.MOVE_ACTION:

            n, sp, ep = data
            self.state = state.move(self.state, n, state.ptoi(*sp), state.ptoi(*ep), opponent)
        else:

            pos = data[0]
            self.state = state.boom(self.state, state.ptoi(*pos))

if __name__ == "__main__":
    pass
