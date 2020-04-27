def minimax(state, depth, ev):
    alpha = -float("inf")
    beta = float("inf")
    for mv, st in state.next_states(opponent=False):

        val = minimax_min(st, depth, ev, alpha, beta)

        if val >= alpha:
            best_move = mv
            alpha = val
    return best_move


def minimax_max(state, depth, ev, alpha, beta):
    if depth == 0 or state.is_gameover():
        return ev(state)

    for mv, child_state in state.next_states(opponent=False):
        alpha = max(alpha, minimax_min(child_state, depth - 1, ev, alpha, beta))

        if beta <= alpha:
            return beta
    return alpha


def minimax_min(state, depth, ev, alpha, beta):
    if depth == 0 or state.is_gameover():
        return ev(state)

    for mv, child_state in state.next_states(opponent=True):
        beta = min(beta, minimax_max(child_state, depth - 1, ev, alpha, beta))

        if beta <= alpha:
            return alpha

    return beta


# New Implementation. Not sure If it works either.
def alpha_beta_search(state, depth, ev):
    alpha = -float("inf")
    beta = float("inf")
    v, mv = max_value(state, depth, ev, alpha, beta)
    return mv


def max_value(state, depth, ev, alpha, beta):
    if depth == 0 or state.is_gameover():
        return ev(state), ()

    v = -float("inf")
    for mv, child_state in state.next_states(opponent=False):
        v = max(v, min_value(child_state, depth - 1, ev, alpha, beta)[0])
        if v >= beta:
            return v, mv
        alpha = max(alpha, v)
    return v, mv


def min_value(state, depth, ev, alpha, beta):
    if depth == 0 or state.is_gameover():
        return ev(state), ()

    v = float("inf")
    for mv, child_state in state.next_states(opponent=True):
        v = min(v, max_value(child_state, depth - 1, ev, alpha, beta)[0])
        if v <= alpha:
            return v, mv
        beta = min(beta, v)
    return v, mv


if __name__ == "__main__":
    pass
