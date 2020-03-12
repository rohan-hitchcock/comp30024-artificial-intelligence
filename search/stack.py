from collections import defaultdict as dd
import json
import itertools


BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

BOARD_LENGTH = 8

class Stack:

    def __init__(self, color, height):
        
        assert height >= 1 and (color == BLACK or color == WHITE) 

        self.color = color
        self.height = height
    
    def __str__(self):
        return self.color + str(self.height)

    def __repr__(self):
        return f"{type(self).__name__}(color={self.color}, height={self.height})"

    def merge(self, other):
        """ Creates a new stack from two other stacks.

            Args:
                other: a stack object of the same color as this stack
            
            Returns:
                A new stack object of the same color with height equal to 
                self.height + other.height
        """
        
        assert self.color == other.color
        return Stack(self.color, self.height + other.height)


class Board:

    def __init__(self):
        """ Creates an empty board"""
        self.stacks = dict()
    

    def get_print_dict(self):
        """ Returns a dictionary of this board suitible for printing by the 
            functions in util.py

            Returns:
                A dictionary of tuples representing board positions. The 
                value is the string to be printed on the board
                
        """

        c_dict = dict()
        for p in itertools.product(range(BOARD_LENGTH), repeat=2):
            
            c_dict[p] = str(self.stacks[p]) if p in self.stacks else ""
    
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
                b.stacks[(x, y)] = Stack(BLACK if c == J_BLACK_NAME else WHITE, h)
        return b



if __name__ == "__main__":

    import util

    infile = "../tests/test-level-2.json"

    with open(infile) as fp:
        board = Board.create_from_json(fp)

    util.print_board(board.get_print_dict())



        







    