import sys
import json
from collections import defaultdict as dd

import search.board as bd
from search import util


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
    


def main():
    with open(sys.argv[1]) as file:
        b = bd.Board.create_from_json(file)

        print("Board:")
        util.print_board(b.get_print_dict())

        components = b.components()

        print("Components:")
        util.print_board(get_labeled_print(components))
        print("Explosion radii")
        util.print_board(get_labeled_print(bd.Board.explosion_radius(c) for c in components))
        print(b.intersecting_radii(color='b'))

    # TODO: find and print winning action sequence



if __name__ == '__main__':
    main()
