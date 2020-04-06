from collections import defaultdict as dd
from collections import namedtuple
import json
import itertools

BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

BOARD_LENGTH = 8

EXPL_RAD = 1


class Board:
    length = BOARD_LENGTH
    expl_rad = EXPL_RAD

    def __init__(self):
        """ Initialises and empty Board """
        self.black = dict()
        self.white = dict()

    def height_at(self, p, color=None):
        """ Returns the height of the stack at the given position, or 0 if no
            stack exists.

            Args:
                p: a valid board position
                color: (optional) if set to either BLACK or WHITE only checks
                for stacks of the selected color

            Returns:
                An integer with the number of tokens (of the selected color) at
                position p
        """
        if color == WHITE:
            h = self.white.get(p)
            return h if h is not None else 0
        elif color == BLACK:
            h = self.black.get(p)
            return h if h is not None else 0

        h_b = self.black.get(p)
        if h_b is not None:
            return h_b

        h_w = self.white.get(p)
        if h_w is not None:
            return h_w
        return 0

    def stack_positions(self, color=None):
        """ An iterator over every board position containing a stack.

            Args:
                color: (optional) set to BLACK or WHITE to only get positions
                of the selected color

            Yields:
                Board positions p for which self.height_at(p, color) is not 0
        """
        if color is None:
            stacks = itertools.chain(self.black, self.white)
        else:
            stacks = self.white if color == WHITE else self.black
        yield from stacks

    def merge_stacks(self, pos1, pos2, color=WHITE):
        """ A function handling the stacking of two stacks, pos1 onto pos2

            Args:
                pos1: The position of the stack moving
                pos2: The position of the stack being stacked upon
                color: (optional) set to BLACK or WHITE to specify the color of
                the stacks being merged
        """
        if color == WHITE:
            self.white[pos2] = self.height_at(pos2, WHITE) + self.white.pop(pos1, 0)
        else:
            self.black[pos2] = self.height_at(pos2, BLACK) + self.black.pop(pos1, 0)

    def unmerge_stacks(self, pos1, color=WHITE):
        if color == WHITE:
            self.white[pos1] = self.height_at(pos1, WHITE) - 1
        else:
            self.black[pos1] = self.height_at(pos1, BLACK) - 1

    def move(self, pos1, pos2, height, color=WHITE):
        if self.height_at(pos1) == height:
            if color == WHITE:
                self.white[pos2] = self.white.pop(pos1, 0)
            else:
                self.black[pos2] = self.black.pop(pos1, 0)
        elif 0 < height < self.height_at(pos1):
            if color == WHITE:
                self.white[pos2] = height
                self.white[pos1] = self.white[pos1] - height
            else:
                self.black[pos2] = height
                self.black[pos1] = self.black[pos1] - height
        else:
            print("BIG NO MATE")

    def as_string(self, p):
        if self.height_at(p, color=BLACK) > 0:
            return BLACK + str(self.black[p])
        elif self.height_at(p, color=WHITE) > 0:
            return WHITE + str(self.white[p])
        return ""

    def get_print_dict(self):
        """ Returns a dictionary of this board suitible for printing"""
        return {p: self.as_string(p) for p in Board.positions()}

    def components(self, color=None):
        """ Finds the groups of stacks in the same 'explosion component', that
            a group of stacks which will explode if any member in the group
            explodes.

            Args:
                color: (optional) set WHITE or BLACK to only look at tokens of
                a particular color

            Returns:
                A list of disjoint sets, where each set contains the positions
                of stacks which will explode if any other member of the stack
                explodes.
        """
        ungrouped_stacks = set(self.stack_positions(color=color))

        compontents = []
        while ungrouped_stacks:
            to_visit = {ungrouped_stacks.pop()}
            component = set()
            while to_visit:

                s = to_visit.pop()
                for n in ungrouped_stacks:
                    if Board.in_explosion_radius(s, n) and (n not in component):
                        to_visit.add(n)

                component.add(s)

            compontents.append(component)
            ungrouped_stacks -= component
        return compontents

    def possible_moves(self, wp, h):
        """ Generates all moves possible for a given white position wp.

            Args:
                wp: the coordinate of a white stack
                h: the height of wp

            Yields:
                positions on this board which are a valid move for a white
                stack at wp
        """
        wpx, wpy = wp

        # tests whether a generated position e is a valid move from s
        valid = lambda s, e: Board.is_valid_position(e) and (s != e) and (e not in self.black)

        return itertools.chain(
            ((x, wpy) for x in range(wpx - h, wpx + h + 1) if valid(wp, (x, wpy))),
            ((wpx, y) for y in range(wpy - h, wpy + h + 1) if valid(wp, (wpx, y)))
        )

    def possible_moves_new(self, wp):
        """ Generates all moves possible for a given white position wp.

            Args:
                wp: the coordinate of a white stac

            Yields:
                positions on this board which are a valid move for a white
                stack at wp
        """
        wpx, wpy = wp
        h = self.height_at(wp)

        # tests whether a generated position e is a valid move from s
        valid = lambda s, e: Board.is_valid_position(e) and (s != e) and (e not in self.black)

        return itertools.chain(
            ((x, wpy) for x in range(wpx - h, wpx + h + 1) if valid(wp, (x, wpy))),
            ((wpx, y) for y in range(wpy - h, wpy + h + 1) if valid(wp, (wpx, y)))
        )

    @staticmethod
    def positions():
        """ Iterates over every valid board position

            Yields:
                valid board positions.
        """
        yield from itertools.product(range(Board.length), repeat=2)

    @staticmethod
    def explosion_radius(ps):
        """ Iterates over the points inside an explosion centered on p

            Args:
                ps: An iterable of valid board positions

            Yields:
                Valid board positions in the explosion radius of ps
        """
        for p in ps:
            x, y = p
            yield from (
                p for p in itertools.product(
                range(x - EXPL_RAD, x + EXPL_RAD + 1),
                range(y - EXPL_RAD, y + EXPL_RAD + 1)
            ) if Board.is_valid_position(p)
            )

    @staticmethod
    def in_explosion_radius(p1, p2):
        """ Checks whether two positions are in the same explosion radius

            Args:
                p1, p2: valid board positions

            Returns:
                True if p1 and p2 are in eachothers explosion radius and false
                otherwise
        """
        return all(abs(x - y) <= Board.expl_rad for x, y in zip(p1, p2))

    @staticmethod
    def manhattan(p1, p2):
        """ Finds the Manhattan distance between two positions

            Args:
                p1: tuple for board coordinate
                p2: tuple for board coordinate

            Returns:
                Manhattan distance (distance only moving in 4 cardinal directions)
        """
        return sum(abs(x - y) for x, y in zip(p1, p2))

    @staticmethod
    def is_valid_position(p):
        """ Checks that the provided position is a valid board position

            Args:
                pos: the position to be checked
            Returns:
                A boolean representing if the position is valid or not
        """
        return all(0 <= x < Board.length for x in p)

    @staticmethod
    def create_from_json(json_fp):
        """ Creates a board object from a json file"""
        b = Board()

        for c, stacks in json.load(json_fp).items():

            for height, x, y in stacks:

                if c == J_BLACK_NAME:
                    b.black[(x, y)] = height
                else:
                    b.white[(x, y)] = height
        return b


if __name__ == "__main__":

    import util
    import random

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

        # randomly increase stack sizes
        for white_stack in board.stack_positions(color=WHITE):
            board.white[white_stack] += random.randint(0, 2)

        # pylint:disable=no-member
        print_dict = board.get_print_dict()
        # util.print_board(print_dict)

        for white_stack in board.stack_positions(color=WHITE):
            print(f"{white_stack} can move to {list(board.possible_moves(white_stack), board.height_at(white_stack))}")

        for i, x in enumerate(board.intersecting_radii(color=BLACK)):

            for p in x:
                print_dict[p] += str(i)

        util.print_board(print_dict)