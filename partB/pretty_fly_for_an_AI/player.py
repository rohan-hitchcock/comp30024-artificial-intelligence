import numpy as np
from pretty_fly_for_an_AI import state
from pretty_fly_for_an_AI.minimax import alpha_beta_search as minimax

import pretty_fly_for_an_AI.evaluation as ev

from pretty_fly_for_an_AI.minimax import alpha_beta_search_ml as minimax_ml
from pretty_fly_for_an_AI.state_logging import StateLogger
from pretty_fly_for_an_AI.evaluation import reward
from collections import deque

from math import ceil

WEIGHTS_FILE = "./pretty_fly_for_an_AI/weights.npy"


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
        rest = s[s == 0]
        diff = (np.sum(ours) + np.sum(theirs))

        # feature 1: Number of pieces for each player
        value += 50 * diff
        # value -= 4 * len(ours)
        # value += 4 * len(rest)

        # feature: winning
        if len(theirs) == 0:
            value += 100000

        # feature 2: Number of available moves
        # value += w_f2 * len(list(state.next_states(opponent=False)))
        # value -= b_f2 * len(list(state.next_states(opponent=True)))

        # feature 3: Distance to middle of the board. Late game
        if len(rest) > 56:
            for i in s:
                if i > 0:
                    value -= ceil(100 * s[i] * Player.manhattan(state.itop(i), (3, 4)))

        # feature 4: Explosion radius. Should include whose turn it is into this
        # for i in range(64):
        #     sum = 0
        #     if state.board[i] != 0:
        #         for j in s.boom_radius(i):
        #             sum += state.board[j]
        #         value += 10 * (state.board[i] - sum)

        return value

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

    ev = lambda state, prev_states: reward(state, LearnerPlayer.weights, prev_states)

    def __init__(self, color):

        self.state = state.create_start_state(color)
        self.prev_states = deque()
        self.prev_states.append(self.state)

        self.logger = StateLogger()

        self.color = color

    def action(self):

        return minimax_ml(self.state, depth=LearnerPlayer.minimax_depth, ev=LearnerPlayer.ev, ml_logger=self.logger,
                          prev_states=self.prev_states)

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

        self.prev_states.append(self.state)
        if len(self.prev_states) == 5:
            self.prev_states.popleft()

        if state.is_gameover(self.state):
            self.logger.record_prev(self.prev_states)


if __name__ == "__main__":
    pass
