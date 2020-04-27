def minimax_noprune(state, depth, ev):
    children = (
        (mv, minimax_min_noprune(ch, depth - 1, ev))
        for mv, ch in state.next_states(opponent=False)
    )

    best_move, val = max(children, key=lambda t: t[-1])
    return best_move

def minimax_max_noprune(state, depth, ev):
    if depth == 0 or state.is_gameover():
        return ev(state)

    children = (
        minimax_min_noprune(ch, depth - 1, ev) 
        for mv, ch in state.next_states(opponent=False)
    )

    return max(children)

def minimax_min_noprune(state, depth, ev):
    if depth == 0 or state.is_gameover():
        return ev(state)

    children = (
        minimax_max_noprune(ch, depth - 1, ev) 
        for mv, ch in state.next_states(opponent=True)
    )

    return min(children)



def minimax(state, depth, ev):
    alpha = -float("inf")
    beta = float("inf")
    for mv, st in state.next_states(opponent=False):

        val = minimax_min(st, depth - 1, ev, alpha, beta)

        print(mv, val)

        if val >= alpha:
            best_move = mv
            alpha = val

    
    return best_move


def minimax_max(state, depth, ev, alpha, beta):
    if depth == 0 or state.is_gameover():
        return ev(state)

    max_val = -float("inf")

    for mv, child_state in state.next_states(opponent=False):
        max_val = max(max_val, minimax_min(child_state, depth - 1, ev, alpha, beta))


        alpha = max(alpha, max_val)
        if beta <= alpha:
            return max_val
    return max_val


def minimax_min(state, depth, ev, alpha, beta):
    if depth == 0 or state.is_gameover():
        return ev(state)

    min_val = float("inf")
    for mv, child_state in state.next_states(opponent=True):
        min_val = min(min_val, minimax_max(child_state, depth - 1, ev, alpha, beta))

        beta = min(beta, min_val)

        if beta <= alpha:
            return min_val

    return min_val


# New Implementation. Not sure If it works either.
def alpha_beta_search(state, depth, ev):
    alpha = -float("inf")
    beta = float("inf")
    v, mv = max_value(state, depth, ev, alpha, beta)
    print(v)
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
