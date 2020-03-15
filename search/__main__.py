import sys
import json

from util import print_move, print_boom, print_board
from board import Board


def main():
    with open(sys.argv[1]) as file:
        # data = json.load(file)
        b = Board.create_from_json(file)
        print_board(b.get_print_dict())
        b.find_groups()
        print_board(b.get_print_dict_from_groups())
    # TODO: find and print winning action sequence


if __name__ == '__main__':
    main()
