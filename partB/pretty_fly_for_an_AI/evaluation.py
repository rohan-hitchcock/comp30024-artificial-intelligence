from math import ceil
import numpy as np


def manhattan(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def evaluation_function(state, weights):
    value = 0
    for i in range(len(weights)):
        value += weights[i] * dpartial_reward(state, weights, i)
    return value


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
