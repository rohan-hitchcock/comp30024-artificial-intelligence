import numpy as np
from pretty_fly_for_an_AI import state
from pretty_fly_for_an_AI.minimax import alpha_beta_search as minimax
from pretty_fly_for_an_AI.minimax import alpha_beta_search_learned as minimax_learned

import pretty_fly_for_an_AI.evaluation as ev

from pretty_fly_for_an_AI.minimax import alpha_beta_search_ml as minimax_ml
from pretty_fly_for_an_AI.state_logging import StateLogger
from pretty_fly_for_an_AI.evaluation import reward
from collections import deque
from collections import defaultdict as dd

from math import ceil

WEIGHTS_W = "./pretty_fly_for_an_AI/weights_w.npy"
WEIGHTS_B = "./pretty_fly_for_an_AI/weights_b.npy"
LEARNED_WEIGHTS = "./pretty_fly_for_an_AI/weights_learned.npy"
LEARNED_WEIGHTS_BLACK = "./pretty_fly_for_an_AI/weights_learned.npy"

BLACK_COLOR = "black"
WHITE_COLOR = "white"


# This is a moderate player, its the one we can now beat
class Player:
    minimax_depth = 3

    ev = lambda state: Player.new_eval(state)

    @staticmethod
    def manhattan(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    @staticmethod
    def new_eval(s):

        value = 0

        ours = s[s > 0]
        theirs = s[s < 0]
        diff = (np.sum(ours) + np.sum(theirs))

        # feature 1: Number of pieces for each player
        value += 50 * diff

        # feature: winning
        if len(theirs) == 0:
            value += 100000

        return value

    def __init__(self, color):

        self.state = state.create_start_state(color)

        self.color = color

        self.counter = 0

    def action(self):

        return minimax(self.state, depth=Player.minimax_depth, ev=Player.ev)

    def update(self, color, action):

        action_type, data = action[0], action[1:]

        # check if this is an opponents move
        opponent = self.color != color

        self.counter += 1
        print(self.counter)

        if action_type == state.MOVE_ACTION:

            n, sp, ep = data
            self.state = state.move(self.state, n, state.ptoi(*sp), state.ptoi(*ep), opponent)
        else:

            pos = data[0]
            self.state = state.boom(self.state, state.ptoi(*pos))


class LearnerPlayer:
    minimax_depth = 3

    weights_w = np.load(WEIGHTS_W)
    weights_b = np.load(WEIGHTS_B)

    expander_w = lambda s, opponent, avoid=dict(): state.next_states(s, opponent, avoid=avoid)
    expander_b = lambda s, opponent, avoid=dict(): state.next_states(s, opponent, avoid=avoid)

    ev_w = lambda state: reward(state, LearnerPlayer.weights_w)
    ev_b = lambda state: reward(state, LearnerPlayer.weights_b)

    def __init__(self, color):

        self.state = state.create_start_state(color)

        # Prev states initialised
        self.prev_states = set()
        self.prev_states.add(self.state.tobytes())
        self.counter = 0
        self.logger = StateLogger()

        self.color = color
        if color == BLACK_COLOR:
            self.expander = LearnerPlayer.expander_b
            self.ev = LearnerPlayer.ev_b
        else:
            self.expander = LearnerPlayer.expander_w
            self.ev = LearnerPlayer.ev_w

        with open("./pretty_fly_for_an_AI/ml_logging/color.color", "w") as fp:
            fp.write(color)

    def action(self):

        return minimax_ml(self.state, depth=LearnerPlayer.minimax_depth, ev=self.ev, ml_logger=self.logger,
                          prev_states=self.prev_states, expan=self.expander)

    def update(self, color, action):

        action_type, data = action[0], action[1:]

        # check if this is an opponents move
        opponent = self.color != color

        self.counter += 1
        print(self.counter)

        if action_type == state.MOVE_ACTION:

            n, sp, ep = data
            self.state = state.move(self.state, n, state.ptoi(*sp), state.ptoi(*ep), opponent)
        else:

            # previous states can now never occur, safe to clear memory
            del self.prev_states
            self.prev_states = set()

            pos = data[0]
            self.state = state.boom(self.state, state.ptoi(*pos))

        self.prev_states.add(self.state.tobytes())


class LearnedPlayer:
    minimax_depth = 3

    weights_white = np.load(LEARNED_WEIGHTS)
    weights_black = np.load(LEARNED_WEIGHTS_BLACK)

    ev_white = lambda state: reward(state, LearnedPlayer.weights_white)
    ev_black = lambda state: reward(state, LearnedPlayer.weights_black)

    expander_w = lambda s, opponent, avoid=dict(): state.next_states(s, opponent, avoid=avoid)
    expander_b = lambda s, opponent, avoid=dict(): state.next_states_black(s, opponent, avoid=avoid)

    moves_w = [("MOVE", 1, (0, 1), (1, 1)), ("MOVE", 2, (1, 1), (3, 1)), ("MOVE", 3, (3, 1), (4, 1))]
    moves_b = [("MOVE", 1, (3, 6), (3, 7)), ("MOVE", 1, (4, 6), (4, 7))]

    def __init__(self, color):

        self.state = state.create_start_state(color)
        self.counter = 0
        # Prev states initialised
        self.prev_states = set()
        self.prev_states.add(self.state.tobytes())

        self.color = color
        if color == BLACK_COLOR:
            self.ev = LearnedPlayer.ev_black
            self.expander = LearnedPlayer.expander_b
            self.moves = LearnedPlayer.moves_b
        else:
            self.ev = LearnedPlayer.ev_white
            self.expander = LearnedPlayer.expander_w
            self.moves = LearnedPlayer.moves_w

    def action(self):

        if self.moves:
            return self.moves.pop(0)

        return minimax_learned(self.state, depth=LearnedPlayer.minimax_depth, ev=self.ev,
                               prev_states=self.prev_states, expan=self.expander)

    def update(self, color, action):

        action_type, data = action[0], action[1:]

        # check if this is an opponents move
        opponent = self.color != color

        self.counter += 1

        if action_type == state.MOVE_ACTION:

            n, sp, ep = data
            self.state = state.move(self.state, n, state.ptoi(*sp), state.ptoi(*ep), opponent)
        else:

            # previous states can now never occur, safe to clear memory
            del self.prev_states
            self.prev_states = set()

            pos = data[0]
            self.state = state.boom(self.state, state.ptoi(*pos))

        if self.counter == 5 and self.color == BLACK_COLOR:
            if self.state[44] == -2 or self.state[12] == -4 or self.state[14] == -4 or self.state[15] == -4:
                self.moves.append(("MOVE", 1, (1, 6), (1, 7)))
                self.moves.append(("MOVE", 2, (3, 7), (1, 7)))
            else:
                self.moves.append(("MOVE", 1, (6, 6), (6, 7)))
                self.moves.append(("MOVE", 2, (4, 7), (6, 7)))

        self.prev_states.add(self.state.tobytes())


if __name__ == "__main__":
    pass
