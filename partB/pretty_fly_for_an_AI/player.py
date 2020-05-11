import numpy as np
from pretty_fly_for_an_AI import state

from pretty_fly_for_an_AI.minimax import alpha_beta_search_learned as minimax_learned
from pretty_fly_for_an_AI.minimax import alpha_beta_search_ml as minimax_ml

from pretty_fly_for_an_AI.state_logging import StateLogger
from pretty_fly_for_an_AI.evaluation import reward

import time

# weights for learning (can change)
WEIGHTS_W = "./pretty_fly_for_an_AI/weights_w.npy"
WEIGHTS_B = "./pretty_fly_for_an_AI/weights_b.npy"

# current best weights (must be updated manually)
LEARNED_WEIGHTS = "./pretty_fly_for_an_AI/weights_learned_w.npy"
LEARNED_WEIGHTS_BLACK = "./pretty_fly_for_an_AI/weights_learned_b.npy"

BLACK_COLOR = "black"
WHITE_COLOR = "white"

# time budget to use before decreasing minimax depth
TIME_THRESHOLD = 55


class Player:
    minimax_depth = 3

    # allow for different weights when white or black
    weights_white = np.load(LEARNED_WEIGHTS)
    weights_black = np.load(LEARNED_WEIGHTS_BLACK)

    # allow for different evaluation functions when white or black
    ev_white = lambda state: reward(state, Player.weights_white)
    ev_black = lambda state: reward(state, Player.weights_black)

    # Same expansion for black and white
    expander = lambda s, opponent, avoid=dict(): state.next_states(s, opponent, avoid=avoid)

    # opening moves
    moves_w = [("MOVE", 1, (0, 1), (1, 1)), ("MOVE", 2, (1, 1), (3, 1)), ("MOVE", 3, (3, 1), (4, 1))]
    moves_b = [("MOVE", 1, (3, 6), (3, 7)), ("MOVE", 1, (4, 6), (4, 7))]

    def __init__(self, color):

        self.state = state.create_start_state(color)
        self.counter = 0

        # Prev states initialised
        self.prev_states = set()
        self.prev_states.add(self.state.tobytes())

        self.timer = 0

        self.minimax_depth = Player.minimax_depth

        self.expander = Player.expander

        self.color = color
        if color == BLACK_COLOR:
            self.ev = Player.ev_black
            self.moves = Player.moves_b
        else:
            self.ev = Player.ev_white
            self.moves = Player.moves_w

    def action(self):

        t0 = time.time()
        if self.moves:
            return self.moves.pop(0)

        move = minimax_learned(self.state, depth=self.minimax_depth, ev=self.ev,
                               prev_states=self.prev_states, expan=self.expander)
        t1 = time.time()
        self.timer += (t1 - t0)
        return move

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

        # branching conditions in the opening book
        if self.counter == 5 and self.color == BLACK_COLOR:
            if self.state[44] == -2 or self.state[12] == -4 or self.state[14] == -4 or self.state[15] == -4:
                self.moves.append(("MOVE", 1, (1, 6), (1, 7)))
                self.moves.append(("MOVE", 2, (3, 7), (1, 7)))
            else:
                self.moves.append(("MOVE", 1, (6, 6), (6, 7)))
                self.moves.append(("MOVE", 2, (4, 7), (6, 7)))

        self.prev_states.add(self.state.tobytes())
        if self.timer >= TIME_THRESHOLD:
            self.minimax_depth = 1


class LearnerPlayer:
    minimax_depth = 3

    weights_w = np.load(WEIGHTS_W)
    weights_b = np.load(WEIGHTS_B)

    expander_w = lambda s, opponent, avoid=dict(): state.next_states(s, opponent, avoid=avoid)
    expander_b = lambda s, opponent, avoid=dict(): state.next_states(s, opponent, avoid=avoid)

    moves_w = [("MOVE", 1, (0, 1), (1, 1)), ("MOVE", 2, (1, 1), (3, 1)), ("MOVE", 3, (3, 1), (4, 1))]
    moves_b = [("MOVE", 1, (3, 6), (3, 7)), ("MOVE", 1, (4, 6), (4, 7))]

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
            self.moves = LearnerPlayer.moves_b
        else:
            self.expander = LearnerPlayer.expander_w
            self.ev = LearnerPlayer.ev_w
            self.moves = LearnerPlayer.moves_w

        with open("./pretty_fly_for_an_AI/ml_logging/color.color", "w") as fp:
            fp.write(color)

    def action(self):
        if self.moves:
            return self.moves.pop(0)
        return minimax_ml(self.state, depth=LearnerPlayer.minimax_depth, ev=self.ev, ml_logger=self.logger,
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
