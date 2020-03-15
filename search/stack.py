from collections import defaultdict as dd
import json
import itertools

BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

BOARD_LENGTH = 8

#*******************************************************************************
class Stack:

    def __init__(self, color, height, pos):
        
        assert height >= 1 and (color == BLACK or color == WHITE) 

        self.color = color
        self.height = height
        self.pos = tuple(pos)
    
    def __str__(self):
        return self.color + str(self.height)

    def __repr__(self):
        return f"{type(self).__name__}(color={self.color}, height={self.height}, pos={self.pos})"

    def merge(self, other):
        """ Creates a new stack from two other stacks.

            Args:
                other: a stack object of the same color as this stack
            
            Returns:
                A new stack object of the same color with height equal to 
                self.height + other.height
        """
        
        assert self.color == other.color and self.pos == other.pos
        return Stack(self.color, self.height + other.height, self.pos)

    def is_valid_move(self, new_pos):
        
        curr_x, curr_y = self.pos
        new_x, new_y = new_pos

        return (
                    (curr_x == new_x or curr_y == new_y) and 
                    (abs(curr_x - new_x + curr_y - new_y) <= self.height)
                )

#*******************************************************************************
class Board:

    def __init__(self):
        """ Creates an empty board"""
        self.white_stacks = []
        self.black_stacks = [] 

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
        for c, stacks in json.load(json_fp).items():
            
            for stack_data in stacks:
                h, x, y = stack_data
                
                if c == J_BLACK_NAME:
                    b.black_stacks.append(Stack(BLACK, h, (x, y)))

                else:
                    b.white_stacks.append(Stack(WHITE, h, (x, y)))
        return b

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
