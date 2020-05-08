from math import ceil, tanh, sqrt
import numpy as np

try:
    from pretty_fly_for_an_AI import state as st
except ModuleNotFoundError:
    import state as st

MAX_RECURS = 4


# Reward has to be passed prev states as well
def reward(state, weights):
    if st.is_gameover(state):
        if np.all(state == 0):
            return 0
        if np.all(state >= 0):
            return 1
        return -1

    feature_vals = feature(state)
    return tanh(sum(w * f for w, f in zip(feature_vals, weights)))


def feature(state):
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
            our_com_to_theirs = 1

    our_sum = np.sum(state[ours_idx])
    their_sum = np.sum(state[theirs_idx])
    diff = our_sum + their_sum

    return [
        ((diff ** 2) * np.sign(diff)) / 144,
        our_sum / (our_com_to_theirs * 12),
        their_sum / (our_com_to_theirs * 12),
        np.count_nonzero(state > 0) / 12,
        np.count_nonzero(state < 0) / 12
    ]


def dpartial_reward(state, weights, i):

    # I think these could be applied to some of my features??
    # if st.is_gameover(state) and (i == 1 or i == 2):
    #     return 0

    fv = feature(state)[i]

    return fv * (1 - (reward(state, weights) ** 2))


def manhattan(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
