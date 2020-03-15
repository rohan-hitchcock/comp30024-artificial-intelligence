from collections import defaultdict as dd
import json
from stack import Stack

BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

BOARD_LENGTH = 8


class Board:

    def __init__(self):
        """ Creates an empty board"""
        self.stacks_white = list()
        self.stacks_black = list()
        self.groups = list()

    def get_print_dict(self):
        """ Returns a dictionary of this board suitible for printing by the
            functions in util.py

            Returns:
                A dictionary of tuples representing board positions. The
                value is the string to be printed on the board

        """

        c_dict = dict()
        all_stacks = self.stacks_white + self.stacks_black
        for s in all_stacks:
            c_dict[s.coordinate] = str(s)

        return c_dict

    def get_print_dict_from_groups(self):
        """ Returns a dictionary of this boards target groups suitible for printing by the
            functions in util.py

            Returns:
                A dictionary of tuples representing each groups explosion radius positions.
                The value is the string to be printed on the board

        """

        c_dict = dict()
        for s in self.groups:
            for c in s:
                c_dict[c] = "*"

        return c_dict

    @staticmethod
    def create_from_json(json_fp):
        """ Creates a board from a json file (see spec for format).

            Args:
                json_fp: a file pointer to a json file of a board.

            Returns:
                The Board object representing the board described in the file.
        """

        b = Board()

        for c, stacks in json.load(json_fp).items():
            for stack_data in stacks:
                h, x, y = stack_data
                if c == J_WHITE_NAME:
                    b.stacks_white.append(Stack(WHITE, h, (x, y)))
                    b.stacks_white.sort(key=lambda s: (s.coordinate[0], s.coordinate[1]))
                else:
                    b.stacks_black.append(Stack(BLACK, h, (x, y)))
                    b.stacks_black.sort(key=lambda s: (s.coordinate[0], s.coordinate[1]))
        return b

    @staticmethod
    def manhattan(pos1, pos2):
        """ Finds the Manhattan distance between two positions

            Args:
                pos1: tuple for board coordinate
                pos2: tuple for board coordinate

            Returns:
                Manhattan distance (distance only moving in 4 cardinal directions)
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    @staticmethod
    def get_explosion_radius(stack):
        """ Finds the coordinates of the 3x3 radius surrounding the stack

            Args:
                stack: Stack object with its coordinate

            Returns:
                set of coordinates
        """
        x = stack.coordinate[0]
        y = stack.coordinate[1]
        radius = set()
        for i in range(x - 1, x + 2):
            if i < 0 or i >= BOARD_LENGTH:
                continue
            for j in range(y - 1, y + 2):
                if j < 0 or j >= BOARD_LENGTH or (i == x and j == y):
                    continue
                radius.update([(i, j)])
        return radius

    def find_groups(self):
        """ Finds the groups of recursively adjacent black stacks

            Returns:
                list of sets of coordinates
        """
        groups = []
        blacks = self.stacks_black.copy()
        blacks_to_remove = []
        for stack in blacks:
            blacks_to_remove.append(stack.coordinate)
            radius = self.get_explosion_radius(stack)
            for other_stack in blacks:
                if other_stack.coordinate in radius:
                    blacks_to_remove.append(other_stack.coordinate)
                    radius.update(self.get_explosion_radius(other_stack))
            for s in blacks:
                if s.coordinate in blacks_to_remove:
                    blacks.remove(s)
            groups.append(radius)
        self.groups = groups

    def find_group_intersections(self):
        """ Finds intersections of groups of black stacks. Needed if
            Number of white stacks less than number of groups

            Returns:
                set of coordinates
        """
        intersections = set()
        for i in range(len(self.groups)):
            for j in range(i+1, len(self.groups)):
                intersections.update(self.groups[i].intersection(self.groups[j]))
        return intersections

if __name__ == "__main__":
    import util

    infile = "../tests/test-level-2.json"

    with open(infile) as fp:
        board = Board.create_from_json(fp)

    util.print_board(board.get_print_dict())
