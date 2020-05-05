from math import ceil, tanh
import numpy as np

try:
    from pretty_fly_for_an_AI import state as st
except ModuleNotFoundError:
    import state as st


def manhattan(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def reward(state, weights, prev_states):
    # revert to utility function if the game is over
    if st.is_gameover(state):
        if np.all(state == 0):
            return 0
        if np.all(state >= 0):
            return 1
        return -1

    if len(prev_states) == 4 and np.array_equal(np.maximum(state, 0), np.maximum(prev_states[0], 0)):
        return -1
    # print(tanh(0.001*sum(w * feature_val(state, i) for i, w in enumerate(weights))))
    return tanh(0.01 * sum(w * feature_val(state, i) for i, w in enumerate(weights)))


def feature_val(state, i):
    # using if statements to avoid calculating things we dont need
    if i == 0:
        # Similar to a tan function in shape, as the difference between our tokens and theirs grows, were
        # greater encouraged to take their tokens

        ours_idx = state > 0
        theirs_idx = state < 0

        ours_pos = np.flatnonzero(ours_idx)
        theirs_pos = np.flatnonzero(theirs_idx)

        if len(ours_pos) == 0 or len(theirs_pos) == 0:
            our_com_to_center = 0
            our_com_to_theirs = 1
        else:

            our_com = sum(np.array(st.itop(p)) for p in ours_pos) / len(ours_pos)
            their_com = sum(np.array(st.itop(p)) for p in theirs_pos) / len(theirs_pos)

            our_com_to_theirs = manhattan(our_com, their_com)
            if our_com_to_theirs == 0:
                return np.sum(state[state > 0])

        ours = state[state > 0]

        return np.sum(ours) / our_com_to_theirs

    if i == 1:
        # Similar to a tan function in shape, as the difference between our tokens and theirs grows, were
        # greater encouraged to take their tokens

        ours_idx = state > 0
        theirs_idx = state < 0

        ours_pos = np.flatnonzero(ours_idx)
        theirs_pos = np.flatnonzero(theirs_idx)

        if len(ours_pos) == 0 or len(theirs_pos) == 0:
            our_com_to_theirs = 1
        else:
            our_com = sum(np.array(st.itop(p)) for p in ours_pos) / len(ours_pos)
            their_com = sum(np.array(st.itop(p)) for p in theirs_pos) / len(theirs_pos)

            our_com_to_theirs = manhattan(our_com, their_com)
            if our_com_to_theirs == 0:
                return np.sum(state[state < 0])

        theirs = state[state < 0]

        return np.sum(theirs) / our_com_to_theirs

    elif i == 2:
        # Should have negative weight, encourages us to stack
        return np.count_nonzero(state[state > 0])

    elif i == 3:
        theirs = state[state < 0]
        ours = state[state > 0]
        return np.sum(ours) + np.sum(theirs)

    # elif i == 2:
    #     # Also encourages us to stack, but also encourages us to remove their tokens. My idea was that this might
    #     # come into play when we have more tokens, but want to sacrifice 1 for 1. A move like this isnt directly
    #     # rewarded
    #
    #     return 64 - np.count_nonzero(state)
    #
    # elif i == 3:
    #     # The reward for winning. Shifted inverse function. 0.1 and 10 chosen so that, for x = [1 --> 12],
    #     # y = [0.01 --> 0.008] but for x = 0, y = 10. Thus if the weight is 1000, the reward for winning is
    #     # 10000, but only 10 when the opposition has 1 token.
    #
    #     return ceil(1 / (0.1 + 10 * np.count_nonzero(state < 0)))
    #
    # elif i == 4:
    #     # The reward for winning. Shifted inverse function. 0.1 and 10 chosen so that, for x = [1 --> 12],
    #     # y = [0.01 --> 0.008] but for x = 0, y = 10. Thus if the weight is 1000, the reward for winning is
    #     # 10000, but only 10 when the opposition has 1 token.
    #
    #     return ceil(1 / (0.1 + 10 * np.count_nonzero(state > 0)))
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


def dpartial_reward(state, weights, i, prev_states):
    return feature_val(state, i) * (
            1 - (reward(state, weights, prev_states) ** 2))
