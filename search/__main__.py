import sys
import json
from collections import defaultdict as dd
import itertools

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

def reconstruct_action(state_from, state_to):

    white_from = state_from.white
    white_to = state_to.white

    stacks_start = list(white_from.difference(white_to))
    stacks_end = list(white_to.difference(white_from))

    assert 1 <= len(stacks_start) <= 2 and 0 <= len(stacks_end) <= 2

    #stack exploded
    if len(stacks_end) == 0:
        x_start, y_start = stacks_start[0].pos
        util.print_boom(x_start, y_start)
        return

    #an entire stack moved
    if len(stacks_end) == 1 and len(stacks_start) == 1:
        
        start = stacks_start[0]
        end = stacks_end[0]
        num_tokens = stacks_start[0].height
    
    #something more complicated happened
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
        b = State.create_from_json(file)

    print("Board:")
    util.print_board(b.get_print_dict())

    state_seq = searcher.whole_board_search(b)
    if state_seq is None:
        print("No path found.")
    else:
        print("State sequence: ")
        
        #iterate through actions defined by pairs of states
        for state_start, state_end in zip(state_seq, state_seq[1:]):
            reconstruct_action(state_start, state_end)

if __name__ == '__main__':
    main()
