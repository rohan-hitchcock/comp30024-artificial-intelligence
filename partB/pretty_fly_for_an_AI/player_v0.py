import numpy as np
from pretty_fly_for_an_AI import state 
from pretty_fly_for_an_AI.minimax import alpha_beta_search as minimax
from pretty_fly_for_an_AI.state_logging import StateLogger
from pretty_fly_for_an_AI.evaluation import reward_v0 as reward

from collections import defaultdict as dd
from math import ceil

WEIGHTS_FILE = "./pretty_fly_for_an_AI/weights_pv0.npy"

class PlayerV0:
    minimax_depth = 3

    evaluation_function = lambda state: PlayerV0.new_eval(state)

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
        value += 50 * diff * diff * np.sign(diff)
        value -= 4 * len(ours)
        value += 4 * len(rest)

        #feature: winning
        if len(theirs) == 0:
            value += 100000

        # feature 2: Number of available moves
        # value += w_f2 * len(list(state.next_states(opponent=False)))
        # value -= b_f2 * len(list(state.next_states(opponent=True)))

        # feature 3: Distance to middle of the board. Late game
        if len(rest) > 59:
            for i in s:
                if i > 0:
                    value -= ceil(10*s[i]*PlayerV0.manhattan(state.itop(i), (3, 4)))

        # feature 4: Explosion radius. Should include whose turn it is into this
        # for i in range(64):
        #     sum = 0
        #     if state.board[i] != 0:
        #         for j in s.boom_radius(i):
        #             sum += state.board[j]
        #         value += 10 * (state.board[i] - sum)

        return value


    def __init__(self, color):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the 
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your 
        program will play as (White or Black). The value will be one of the 
        strings "white" or "black" correspondingly.
        """
        self.state = state.create_start_state(color)

        self.color = color

    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        return minimax(self.state, depth=PlayerV0.minimax_depth, ev=PlayerV0.evaluation_function)

    def update(self, color, action):
        """
        This method is called at the end of every turn (including your player’s 
        turns) to inform your player about the most recent action. You should 
        use this opportunity to maintain your internal representation of the 
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (White or Black). The value will be one of the strings "white" or
        "black" correspondingly.

        The parameter action is a representation of the most recent action
        conforming to the spec's instructions for representing actions.

        You may assume that action will always correspond to an allowed action 
        for the player colour (your method does not need to validate the action
        against the game rules).
        """

        action_type, data = action[0], action[1:]

        # check if this is an opponents move
        opponent = self.color != color

        if action_type == state.MOVE_ACTION:

            n, sp, ep = data
            self.state = state.move(self.state, n, state.ptoi(*sp), state.ptoi(*ep), opponent)
        else:

            pos = data[0]
            self.state = state.boom(self.state, state.ptoi(*pos))

class TrainedPlayerV0:
    
    minimax_depth = 3

    weights = np.load(WEIGHTS_FILE)
    
    ev = lambda state : reward(state, TrainedPlayerV0.weights)

    def __init__(self, color):

        self.state = state.create_start_state(color)

        self.logger = StateLogger()

        self.color = color

    def action(self):

        return minimax(self.state, depth=TrainedPlayerV0.minimax_depth, ev=TrainedPlayerV0.ev)

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

        if state.is_gameover(self.state):
            self.logger.add(self.state)

if __name__ == "__main__":
    pass
