import sys
import json
from collections import defaultdict as dd

from search import util
from search import searcher
from search.state import State


def get_labeled_print(components):
    """ Accepts a finite iterable of iterables of valid board positions. 
        Returns a dictionary suitible for printing where each position is labeled
        by the index of the iterable containing it in components"""

    print_dict = dd(str)
    for component_id, component in enumerate(components):
        for pos in component:

            if str(component_id) not in print_dict[pos]:
                print_dict[pos] += str(component_id)

    return print_dict


def decide_print(move):
    pos1, pos2, h = move
    if pos1 == pos2:
        x, y = pos1
        util.print_boom(x, y)
    else:
        x1, y1 = pos1
        x2, y2 = pos2
        util.print_move(h, x1, y1, x2, y2)


def main():
    with open(sys.argv[1]) as file:
        b = State.create_from_json(file)

    print("Board:")
    util.print_board(b.get_print_dict())

    """
    print("States:")
    for l in b.generate_states(State.create_from_dict(b.white)):
        print(l)
    
    paths = searcher.find_paths(b)

    print("\nall paths:")
    for w, p in paths.items():
        print(f"{w} follows {p}")

    print("\n\n\nNEW: _____________________________________________")
    """
    state_seq = None
    state_seq = searcher.whole_board_search(b)
    if state_seq is None:
        print("No path found.")
    else:
        print("State sequence: ")
        for s in state_seq[1:]:
            decide_print(s.created_from)
        for w in state_seq[-1].white.keys():
            x, y = w
            util.print_boom(x, y)


if __name__ == '__main__':
    main()
