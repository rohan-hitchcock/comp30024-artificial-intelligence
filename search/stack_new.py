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

        ungrouped_stacks = set(self.stack_positions(color=color))

        compontents = []
        while ungrouped_stacks:

            to_visit = [ungrouped_stacks.pop()]
            component = set()
            while to_visit:

                s = to_visit.pop()

                for n in ungrouped_stacks:
                    if Board.in_explosion_radius(s, n):
                        to_visit.append(n)

                component.add(s)
            
            compontents.append(component)
            ungrouped_stacks -= component
        return compontents




    


    @staticmethod
    def positions():
        """ Iterates over every valid board position

            Yields:
                valid board positions.
        """
        yield from itertools.product(range(Board.length), repeat=2)

    @staticmethod
    def explosion_radius(p):
        """ Iterates over the points inside an explosion centered on p

            Args:
                p: A valid board position

            Yields:
                Valid board positions in the explosion radius of p
        """
        x, y = p
        return (
            p for p in itertools.product(range(x - Board.expl_rad, x + Board.expl_rad + 1), range(y - Board.expl_rad, y + Board.expl_rad + 1))
            if Board.is_valid_position(p)
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
        return all (0 <= x < Board.length for x in p)

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



