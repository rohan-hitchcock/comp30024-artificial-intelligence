from pretty_fly_for_an_AI import state as st
import numpy as np
import math


# Learner variation with logging ----------------------------------- #

def alpha_beta_search_ml(state, depth, ev, ml_logger, prev_states, expan):
    alpha = -float("inf")
    beta = float("inf")

    if np.count_nonzero(state) < 6:
        expander = lambda s, opponent: st.next_states_end(s, opponent, avoid=prev_states)
    else:
        expander = lambda s, opponent: expan(s, opponent, avoid=prev_states)

    v, mv, pred_state = max_value_ml(state, depth, ev, alpha, beta, expander)
    if mv is None:
        expander = lambda s, opponent: st.next_states_black(s, opponent)
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


# Standard best player variation -------------------------------------- #
def alpha_beta_search_learned(state, depth, ev, prev_states, expan):
    alpha = -float("inf")
    beta = float("inf")
    if np.count_nonzero(state) < 6:
        expander = lambda s, opponent: st.next_states_end(s, opponent, avoid=prev_states)
    else:
        expander = lambda s, opponent: expan(s, opponent, avoid=prev_states)

    v, mv = max_value_learned(state, depth, ev, alpha, beta, expander)

    if mv is None:
        expander = lambda s, opponent: st.next_states_end(s, opponent)
        v, mv, pred_state = max_value_ml(state, depth, ev, alpha, beta, expander)

    return mv


def max_value_learned(state, depth, ev, alpha, beta, expander):
    if depth == 0 or st.is_gameover(state):
        return ev(state), None

    v = -float("inf")
    move = None
    for mv, child_state in expander(state, False):
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
        score, came_from = max_value_learned(child_state, depth - 1, ev, alpha, beta, expander)
        if score < v:
            v = score
            move = mv

        if v <= alpha:
            return v, move
        beta = min(beta, v)
    return v, move


# Implementation for moderate player ------------------------------------------ #
def alpha_beta_search(state, depth, ev):
    alpha = -float("inf")
    beta = float("inf")
    v, mv = max_value(state, depth, ev, alpha, beta)
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

        if v >= beta:
            return v, move
        alpha = max(alpha, v)
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

        if v <= alpha:
            return v, move
        beta = min(beta, v)

    return v, move


# Principle variation seach experiment ---------------------------------------- #
def principle_variation_search(state, depth, ev, prev_states):
    expander = lambda s, opponent: st.next_states(s, opponent, avoid=prev_states)
    _, move = pvs_algorithm(state, depth, -float("inf"), float("inf"), False, ev, expander)

    if move is None:
        print("oh no!")

    return move


def pvs_algorithm(state, depth, alpha, beta, opponent, ev, expander):
    if depth == 0 or st.is_gameover(state):
        sgn = -1 if opponent else 1
        return sgn * ev(state), None

    is_first = True
    move = None
    for mv, child in expander(state, opponent):

        if is_first:
            score, _ = pvs_algorithm(child, depth - 1, -beta, -alpha, not opponent, ev, expander)
            score = -score

            is_first = False
        else:
            score, _ = pvs_algorithm(child, depth - 1, -alpha - 1, -alpha, not opponent, ev, expander)
            score = -score

            if alpha < score < beta:
                score, _ = pvs_algorithm(child, depth - 1, -beta, -score, not opponent, ev, expander)
                score = -score

        if score > alpha:
            alpha = score
            move = mv

        if alpha >= beta:
            break

    return alpha, move


if __name__ == "__main__":
    pass
