from collections import defaultdict as dd
import json
import itertools

BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

BOARD_LENGTH = 8


class Stack:

    def __init__(self, color, height, coordinate):
        assert height >= 1 and (color == BLACK or color == WHITE)
        assert (coordinate[0] and coordinate[1]) in range(BOARD_LENGTH)
        self.color = color
        self.height = height
        self.coordinate = coordinate

    def __str__(self):
        return self.color + str(self.height)

    def __repr__(self):
        return f"{type(self).__name__}(color={self.color}, height={self.height}, coordinate = {self.coordinate})"

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
