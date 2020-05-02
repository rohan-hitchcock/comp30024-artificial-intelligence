import numpy as np
from pretty_fly_for_an_AI import state as s
from pretty_fly_for_an_AI.minimax import alpha_beta_search as minimax
from collections import defaultdict as dd
from math import ceil


class Player:
    minimax_depth = 3

    evaluation_function = lambda state: Player.new_eval(state)

    @staticmethod
    def manhattan(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    @staticmethod
    def evaluation_function(state, weights):
        value = 0
        for i in range(len(weights)):
            value += weights[i] * Player.dpartial_reward(state, weights, i)
        return value

    @staticmethod
    def dpartial_reward(state, weights, i):

        # using if statements to avoid calculating things we dont need
        if i == 0:
            # Similar to a tan function in shape, as the difference between our tokens and theirs grows, were
            # greater encouraged to take their tokens
            ours = state.board[state.board > 0]
            theirs = state.board[state.board < 0]
            diff = (np.sum(ours) + np.sum(theirs))
            return diff * diff * np.sign(diff)

        elif i == 1:
            # Should have negative weight, encourages us to stack
            return len(state.board[state.board > 0])

        elif i == 2:
            # Also encourages us to stack, but also encourages us to remove their tokens. My idea was that this might
            # come into play when we have more tokens, but want to sacrifice 1 for 1. A move like this isnt directly
            # rewarded
            return len(state.board[state.board == 0])

        elif i == 3:
            # The reward for winning. Shifted inverse function. 0.1 and 10 chosen so that, for x = [1 --> 12],
            # y = [0.01 --> 0.008] but for x = 0, y = 10. Thus if the weight is 1000, the reward for winning is
            # 10000, but only 10 when the opposition has 1 token.
            return ceil(1 / (0.1 + 10 * len(state.board[state.board < 0])))

        # ------------------- FEATURES TO KEEP IN MIND ------------------ #

        # Encourages the player to move to the centre of the board when there are little stacks remaining.
        # I think this is important, but hard to flatten into a straight assignment. Will leave commented for now.
        # distance = lambda index: ceil(state.board[index]*Player.manhattan(s.itop(index), (3, 4)))
        # feat_5 = 0
        # if len(rest) > 59:
        #     for i in state.board:
        #         if i > 0:
        #             feat_5 -= 10* distance(i)

        # feature: Number of available moves
        # value += w_f2 * len(list(state.next_states(opponent=False)))
        # value -= b_f2 * len(list(state.next_states(opponent=True)))

        # feature: Explosion radius. Should include whose turn it is into this
        # for i in range(64):
        #     sum = 0
        #     if state.board[i] != 0:
        #         for j in s.boom_radius(i):
        #             sum += state.board[j]
        #         value += 10 * (state.board[i] - sum)


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
        self.state = s.State.create_start_state(color)

        self.color = color

    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        return minimax(self.state, depth=Player.minimax_depth, ev=Player.evaluation_function)

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

        if action_type == s.MOVE_ACTION:

            n, sp, ep = data
            self.state = self.state.move(n, s.ptoi(*sp), s.ptoi(*ep), opponent)
        else:

            pos = data[0]
            self.state = self.state.boom(s.ptoi(*pos))


if __name__ == "__main__":
    pass
