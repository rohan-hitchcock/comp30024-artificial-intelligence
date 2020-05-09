from pretty_fly_for_an_AI import state as st
import numpy as np


# IMPLEMENTATION FOR MODERATE PLAYER
def alpha_beta_search(state, depth, ev):
    alpha = -float("inf")
    beta = float("inf")
    v, mv = max_value(state, depth, ev, alpha, beta)
    # print("summary: v= " + str(v) + " on move: " + str(mv))
    return mv


def max_value(state, depth, ev, alpha, beta):
    if depth == 0 or st.is_gameover(state):
        return ev(state), None

    v = -float("inf")
    child = None
    move = None
    for mv, child_state in st.next_states(state, opponent=False):
        score, came_from = min_value(child_state, depth - 1, ev, alpha, beta)
        if score > v:
            v = score
            child = came_from
            move = mv
        # v = max(v, min_value(child_state, depth - 1, ev, alpha, beta)[0])

        if v >= beta:
            # print("summary max: v= " + str(v) + " from: " + str(child) + " on move: " + str(move))

            return v, move
        alpha = max(alpha, v)
    # print("summary max: v= " + str(v) + " from: " + str(child) + " on move: " + str(move))
    return v, move


def min_value(state, depth, ev, alpha, beta):
    if depth == 0 or st.is_gameover(state):
        return ev(state), None

    v = float("inf")
    move = None
    child = None
    for mv, child_state in st.next_states(state, opponent=True):
        score, came_from = max_value(child_state, depth - 1, ev, alpha, beta)
        if score < v:
            v = score
            child = came_from
            move = mv
        # v = min(v, max_value(child_state, depth - 1, ev, alpha, beta)[0])

        if v <= alpha:
            # print("summary min: v= " + str(v) + " from: " + str(child) + " on move: " + str(move))
            return v, move
        beta = min(beta, v)
    # print("summary min: v= " + str(v) + " from: " + str(child) + " on move: " + str(move))
    return v, move


# ----------------------------------------- LEARNER ----------------------------------- #
# New Implementation. Prev states now need to be passed into here so they can be passed to reward!!!
def alpha_beta_search_ml(state, depth, ev, ml_logger, prev_states, expan):
    alpha = -float("inf")
    beta = float("inf")

    if np.count_nonzero(state) < 6:
        expander = lambda s, opponent: st.next_states_black(s, opponent, avoid=prev_states)
    else:
        expander = lambda s, opponent: expan(s, opponent, avoid=prev_states)

    v, mv, pred_state = max_value_ml(state, depth, ev, alpha, beta, expander)
    ml_logger.add(pred_state)
    return mv


def max_value_ml(state, depth, ev, alpha, beta, expander):
    if depth == 0 or st.is_gameover(state):
        return ev(state), None, state

    v = -float("inf")
    move = None
    pred_state = None
    for mv, child_state in expander(state, False):
        score, came_from, leaf_state = min_value_ml(child_state, depth - 1, ev, alpha, beta, expander)
        if score > v:
            v = score
            pred_state = leaf_state
            move = mv

        if v >= beta:
            return v, move, pred_state

        alpha = max(alpha, v)
    return v, move, pred_state


def min_value_ml(state, depth, ev, alpha, beta, expander):
    if depth == 0 or st.is_gameover(state):
        return ev(state), None, state

    v = float("inf")
    move = None
    pred_state = None
    for mv, child_state in expander(state, True):
        score, came_from, leaf_state = max_value_ml(child_state, depth - 1, ev, alpha, beta, expander)
        if score < v:
            v = score
            pred_state = leaf_state
            move = mv

        if v <= alpha:
            return v, move, pred_state
        beta = min(beta, v)
    return v, move, pred_state


# ------------------------------------------ LEARNED -----------------------------------------#
counter = 0


# Implementation for learned player
def alpha_beta_search_learned(state, depth, ev, prev_states, expan):
    alpha = -float("inf")
    beta = float("inf")
    # if np.count_nonzero(state) > 19:
    #     depth = 1
    #     expander = lambda s, opponent: expan(s, opponent, avoid=prev_states)
    # elif np.count_nonzero(state) < 5:
    #     depth = 5
    #     expander = lambda s, opponent: st.next_states_end(s, opponent, avoid=prev_states)
    # else:
    expander = lambda s, opponent: expan(s, opponent, avoid=prev_states)

    v, mv = max_value_learned(state, depth, ev, alpha, beta, expander)
    global counter
    print(counter)
    return mv


def max_value_learned(state, depth, ev, alpha, beta, expander):
    if depth == 0 or st.is_gameover(state):
        return ev(state), None

    v = -float("inf")
    move = None
    for mv, child_state in expander(state, False):
        global counter
        counter += 1
        score, came_from = min_value_learned(child_state, depth - 1, ev, alpha, beta, expander)
        if score > v:
            v = score
            move = mv

        if v >= beta:
            return v, move

        alpha = max(alpha, v)
    return v, move


def min_value_learned(state, depth, ev, alpha, beta, expander):
    if depth == 0 or st.is_gameover(state):
        return ev(state), None

    v = float("inf")
    move = None
    for mv, child_state in expander(state, True):
        global counter
        counter += 1
        score, came_from = max_value_learned(child_state, depth - 1, ev, alpha, beta, expander)
        if score < v:
            v = score
            move = mv

        if v <= alpha:
            return v, move
        beta = min(beta, v)
    return v, move


if __name__ == "__main__":
    pass
