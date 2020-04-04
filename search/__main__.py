import sys
import json
import itertools

from search import util
from search import searcher
from search.state import State


def reconstruct_action(state_from, state_to):
    """ Given a pair of states seperated by an action, prints the action using
        util corresponding to that action.

        Args:
            state_from: starting State
            state_to: State as the result of applying some action to state_from
    """
    white_from = state_from.white
    white_to = state_to.white

    stacks_start = list(white_from.difference(white_to))
    stacks_end = list(white_to.difference(white_from))

    assert 1 <= len(stacks_start) and 0 <= len(stacks_end)

    # stack exploded
    if len(stacks_end) == 0:
        x_start, y_start = stacks_start[0].pos
        util.print_boom(x_start, y_start)
        return

    # an entire stack moved
    if len(stacks_end) == 1 and len(stacks_start) == 1:

        start = stacks_start[0]
        end = stacks_end[0]
        num_tokens = stacks_start[0].height

    # something more complicated happened
    else:
        for s, e in itertools.product(stacks_start, stacks_end):

            if s.pos == e.pos:

                if s.height > e.height:
                    start = s
                    num_tokens = s.height - e.height
                    end = stacks_end[0] if e == stacks_end[-1] else stacks_end[-1]
                    break

                if s.height < e.height:
                    end = e
                    num_tokens = e.height - s.height

                    start = stacks_start[0] if s == stacks_start[-1] else stacks_start[-1]
                    break

    x_start, y_start = start.pos
    x_end, y_end = end.pos

    util.print_move(num_tokens, x_start, y_start, x_end, y_end)


def main():
    with open(sys.argv[1]) as file:
        start = State.create_from_json(file)

    print("Board:")
    util.print_board(start.get_board_dict())

    state_seq = searcher.search_board_states(start)
    if state_seq is None:
        print("No path found.")
    else:
        print("State sequence: ")

        # iterate through actions defined by pairs of states
        for state_start, state_end in zip(state_seq, state_seq[1:]):
            reconstruct_action(state_start, state_end)


if __name__ == '__main__':
    main()
