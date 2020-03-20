import sys
import json

from stack import Board, Stack
from util import print_move, print_boom, print_board


def main():
    with open(sys.argv[1]) as file:
        b = Board.create_from_json(file)
        print_board(b.get_print_dict())
        print_board(b.cc())
        print(b.groups)
        print_board(b.get_print_dict_from_groups(b.get_group_radii()))
        print(b.get_group_radii())
        print(b.intersecting_groups())
        print(list(b.get_group_radii().values())==b.intersecting_groups())
    # TODO: find and print winning action sequence



if __name__ == '__main__':
    main()
