from collections import defaultdict as dd
import json
import itertools

BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

BOARD_LENGTH = 8


# *******************************************************************************
class Stack:

    def __init__(self, color, height, x, y):
        assert height >= 1 and (color == BLACK or color == WHITE)
        assert (x and y) in range(BOARD_LENGTH)
        self.color = color
        self.height = height
        self.x = x
        self.y = y

    def __str__(self):
        return self.color + str(self.height)

    def __repr__(self):
        return f"{type(self).__name__}(color={self.color}, height={self.height}, x = {self.x}, y = {self.y})"

    def merge(self, other):
        """ Creates a new stack from two other stacks.

            Args:
                other: a stack object of the same color as this stack
            
            Returns:
                A new stack object of the same color with height equal to 
                self.height + other.height
        """

        assert self.color == other.color
        return Stack(self.color, self.height + other.height, self.x, self.y)

    def get_explosion_radius(self):
        """ Finds the coordinates of the 3x3 radius surrounding the stack

            Args:
                stack: Stack object with its coordinate

            Returns:
                set of coordinates
        """
        radius = set()
        for i in range(self.x - 1, self.x + 2):
            if i < 0 or i >= BOARD_LENGTH:
                continue
            for j in range(self.y - 1, self.y + 2):
                if j < 0 or j >= BOARD_LENGTH or (i == self.x and j == self.y):
                    continue
                radius.update([(i, j)])
        return radius

    def is_in_explosion_radius(self, stack):
        diff_x = abs(stack.x - self.x)
        diff_y = abs(stack.y - self.y)
        return (diff_x + diff_y == 1) or (diff_x == 1 and diff_y == 1)


# *******************************************************************************
class Board:

    def __init__(self):
        """ Creates an empty board"""
        self.stacks_white = list()
        self.stacks_black = list()
        self.groups = dict()
        self.state = list()

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
            c_dict[(s.x, s.y)] = str(s)

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

    def get_print_dict(self):
        """ Returns a dictionary of this board suitible for printing by the 
            functions in util.py

            Returns:
                A dictionary of tuples representing board positions. The 
                value is the string to be printed on the board      
        """
        c_dict = dict()
        stack_positions = self.coordinate_view()
        for p in itertools.product(range(BOARD_LENGTH), repeat=2):
            c_dict[p] = str(stack_positions[p]) if p in stack_positions else ""

        return c_dict

    def stacks(self, color=None):
        """ A generator for all stacks of the selected color.

            Args:
                color: (optional) If set to either WHITE or BLACK only returns
                stacks of that color.
            
            Yields:
                Each Stack object on the board.
        """

        if color is None:
            stacks = itertools.chain(self.black_stacks, self.white_stacks)
        else:
            stacks = self.white_stacks if color == WHITE else self.black_stacks

        yield from stacks

    def stack_at(self, pos):
        """ Gets the stack at position pos.
        
            Args:
                pos: a tuple which is a valid coordinate on the board.
                
            Returns:
                The Stack object at position pos or None if no such Stack exists
        """
        for s in self.stacks():
            if s.pos == pos:
                return s

        return None

    def coordinate_view(self, color=None):
        """ Gets a view of the board where stacks can be looked up by coordinate, 
            i.e. a dictionary of stacks keyed by their position. Coordinates 
            where there is no stack are not present. Each time this method is 
            called a new dictionary is created, so avoid calling it many times
            if the board is not changing.

            Args:
                color: (optional) if left unset all stacks are in the returned
                dictionary. Otherwise set to BLACK or WHITE to get a dictionary
                only containing stacks of that color.

            Returns:
                A dictionary of Stack objected keyed by their coordinate (tuple).
        """
        return {s.pos: s for s in self.stacks(color=color)}

    @staticmethod
    def create_from_json(json_fp):
        """ Creates a board from a json file (see spec for format).

            Args:
                json_fp: a file pointer to a json file of a board.

            Returns:
                The Board object representing the board described in the file.
        """

        b = Board()

        for i in range(BOARD_LENGTH):
            row = []
            for j in range(BOARD_LENGTH):
                row.append(0)
            b.state.append(row)

        for c, stacks in json.load(json_fp).items():
            for stack_data in stacks:
                h, x, y = stack_data
                if c == J_WHITE_NAME:
                    b.stacks_white.append(Stack(WHITE, h, x, y))

                else:
                    b.stacks_black.append(Stack(BLACK, h, x, y))
                    b.state[x][y] = 1
        # b.stacks_black.sort(key=lambda s: (s.coordinate[0], s.coordinate[1]))
        # b.stacks_white.sort(key=lambda s: (s.coordinate[0], s.coordinate[1]))
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
    def manhattan(x1, y1, x2, y2):
        """ Finds the Manhattan distance between two positions

            Args:
                x1: x coordinate of first position
                y1: y coordinate of first position
                x2: x coordinate of second position
                y2: y coordinate of second position

            Returns:
                Manhattan distance (distance only moving in 4 cardinal directions)
        """
        return abs(x1 - x2) + abs(y1 - y2)

    # This was my original way of immediately finding the sets of group radii from
    # black stack list, dont think it's great though
    # def find_groups(self):
    #     """ Finds the groups of recursively adjacent black stacks
    #
    #         Returns:
    #             list of sets of coordinates
    #     """
    #     groups = []
    #     blacks = self.stacks_black.copy()
    #     blacks_to_remove = []
    #     for stack in blacks:
    #         blacks_to_remove.append(stack.coordinate)
    #         radius = self.get_explosion_radius(stack)
    #         for other_stack in blacks:
    #             if other_stack.coordinate in radius:
    #                 blacks_to_remove.append(other_stack.coordinate)
    #                 radius.update(self.get_explosion_radius(other_stack))
    #         for s in blacks:
    #             if s.coordinate in blacks_to_remove:
    #                 blacks.remove(s)
    #         groups.append(radius)
    #     self.groups = groups

    # At the moment this method has exact same logic as Stack.get_explosion_radius
    # except that it takes in a coordinate, and a boolean to determine whether or not
    # the coordinate whose neighbours we want should be kept. I needed this for other functions
    # and cant use stack for here.
    @staticmethod
    def coordinate_neighbours(x, y, include_self):
        """ Finds the 8 neighbours of a coordinate if they are on the board

            Args:
                x: x coordinate of position
                y: y coordinate of position
                include_self: boolean to indicate whether we want to keep the
                coordinate itself.

            Returns:
                list of neighbouring coordinates on the board
        """
        neighbours = set()
        for i in range(x - 1, x + 2):
            if i < 0 or i >= BOARD_LENGTH:
                continue
            for j in range(y - 1, y + 2):
                if j < 0 or j >= BOARD_LENGTH or (not include_self and i == x and j == y):
                    continue
                neighbours.add((i, j))
        return neighbours

    def flood_fill(self, x, y, label):
        """ recursively gives neighbours the same label

            Args:
                x: x coordinate of position
                y: y coordinate of position
                label: label to be given
        """
        self.state[x][y] = label
        self.groups[label].update([(x, y)])
        for tup in Board.coordinate_neighbours(x, y, False):
            if self.state[tup[0]][tup[1]] == 1:
                self.flood_fill(tup[0], tup[1], label)

    def cc(self):
        """ Finds all connected components on a board state

            Returns:
                dictionary of labels and the set of coordinates associated with that label
                suitable for printing with given print_board function
        """
        label = 1
        for j in range(BOARD_LENGTH - 1, -1, -1):
            for i in range(BOARD_LENGTH):
                if self.state[i][j] == 1:
                    label += 1
                    self.groups[label] = set()
                    self.flood_fill(i, j, label)
        groups = dict()
        for j in range(BOARD_LENGTH - 1, -1, -1):
            for i in range(BOARD_LENGTH):
                groups[(i, j)] = self.state[i][j]
        return groups

    def get_group_radii(self):
        """ Finds the detonation area of each group of connected black stacks.
            Does not include the coordinates of the stacks belonging to that group

            Returns:
                a list of sets of coordinates
        """
        radii = list()
        for group in self.groups.values():
            radius = set()
            for tup in group:
                radius.update(Board.coordinate_neighbours(tup[0], tup[1], True))
            radius = radius - group
            radii.append(radius)
        return radii

    @staticmethod
    def is_valid_position(pos):
        if len(pos) != 2:
            return False

        x, y = pos
        return x >= 0 and x < BOARD_LENGTH and y >= 0 and y < BOARD_LENGTH


if __name__ == "__main__":

    import util

    all_tests = [

        "../tests/test-level-1.json",
        "../tests/test-level-2.json",
        "../tests/test-level-3.json",
        "../tests/test-level-4.json"
    ]

    for infile in all_tests:
        print("\n" + infile)
        with open(infile) as fp:
            board = Board.create_from_json(fp)

        util.print_board(board.get_print_dict())
