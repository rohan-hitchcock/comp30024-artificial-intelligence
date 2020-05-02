import numpy as np
import itertools

BLACK_COLOR = "black"
WHITE_COLOR = "white"

#strings identifying move and boom actions
MOVE_ACTION = "MOVE"
BOOM_ACTION = "BOOM"

#the x/y length of the board
BOARD_SIZE = 8

#explosion radius
ER = 1

#the starting board in a flattened byte array when positive entries are white 
# stacks and negative entries are black stacks
BOARD_START = np.array([ 1,  1,  0,  1,  1,  0,  1,  1,  1,  1,  0,  1,  1,  0, 
                         1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  
                         0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  
                         0,  0,  0,  0,  0,  0, -1, -1,  0, -1, -1,  0, -1, -1, 
                        -1, -1,  0, -1, -1,  0, -1, -1], dtype=np.int8)


#empty board, for debugging
BOARD_EMPTY = np.zeros(BOARD_SIZE ** 2, dtype=np.int8)

class State:
    """ Represents a state of the game
    
        Attributes:
            board: a numpy byte array of length BOARD_INDEX ** 2. Each entry 
            corresponds to a position on the board (see functions ptoi and itop)
            Positive entries are the players stacks, negative the opponent's 
            stacks and Zero entries a free space. The absolute value of an entry
            is the height of the stack at that position.
    """

    def __init__(self, board):
        """ Initializes a State. 

            Args:
                board: a numpy array (see description of board attribute).
        """
        self.board = board

    def __str__(self):
        board_2d = np.reshape(self.board, (BOARD_SIZE, BOARD_SIZE))
        out = ""
        for y, row in reversed(list(enumerate(board_2d))):
            
            out += f" {y} |"

            for h in row:

                if h == 0:
                    out += "    |"
                elif h > 0:
                    out += f" p{abs(h)} |"
                else:
                    out += f" o{abs(h)} |"

            out += "\n"
            out += "---+" + 8 * "----+" + "\n"
        out += "y/x|  0 |  1 |  2 |  3 |  4 |  5 |  6 |  7 |\n"
        return out

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.board)})"

    def __eq__(self, other):
        return self.board == other.board

    def move(self, num_tokens, si, ei, opponent):
        """ Returns a new state object which is the result of applying move.
        
            No validation is done. May not throw an error if move is invalid.
            
            Args:
                num_tokens: the number of tokens being moved.
                si: the starting board index of the move
                ei: the ending board index of the move
                opponent: set to True if the oponent is making the move
            
            Returns:
                A new State object which is the result of executing the move on
                this state object.
        """
        #opponent stacks are stored as negative values
        if opponent:
            num_tokens = -num_tokens    

        next_board = self.board.copy()
        
        next_board[si] -= num_tokens
        next_board[ei] += num_tokens
        return State(next_board)

    def boom(self, i):
        """ Returns a new state object which is the result of the token at pos
            exploding. 

            No validation is done. May not throw an error if the move is invalid.

            Args:
                i: the board index at which to boom

            Returns:
                A new State object which is the result of execting the boom on
                this state object.
        """
        next_board = self.board.copy()

        to_boom = {i}
        while to_boom:

            boom = to_boom.pop()

            #remove piece
            next_board[boom] = 0

            #set all token indexes (the non-zero entries of board) in radius to boom
            radius = boom_radius(boom)
            to_boom.update(radius[next_board[radius] != 0])

        return State(next_board)

    def next_states(self, opponent):
        """ A generator for the states accessible from this state via valid moves.
        
            Produces the State as well as an identifier for the action taken.
            
            Args:
                opponent: set to True if the opponent is making the move.
                
            Yields:
                tuples of the form (name, state) where name is the identifier 
                of the action and state is the State object resulting from the 
                action.
        """
        #get the indexes of the stacks of the player making the move
        stacks = np.flatnonzero(self.board < 0) if opponent else np.flatnonzero(self.board > 0)

        for si in stacks:
            
            # The boom move. If the opponent is moving it is simplest to include
            #this move every time (although optimising here is worth looking into)
            #if we are moving it never makes sense to boom a token if it does 
            #not remove at least one oponent token from the board
            if opponent:
                yield boom_name(si), self.boom(si)
            elif any(pos < 0 for pos in self.board[boom_radius(si)]):
                yield boom_name(si), self.boom(si)

            height = abs(self.board[si])

            for to_i in move_positions(si, height):
                #checks if to_i is either empty or the same color as si
                if self.board[to_i] * self.board[si] >= 0:
                    yield from ((move_name(n, si, to_i), self.move(n, si, to_i, opponent))
                                for n in range(1, height + 1))

    def is_gameover(self):
        return np.all(self.board >= 0) or np.all(self.board <= 0)

    @staticmethod
    def create_start_state(color):
        """ Creates the starting baord state.

            Args:
                color: the color of the player (either BLACK_COLOR or WHITE_COLOR)

            Returns:
                A State object
        """
        if color == BLACK_COLOR:
            return State((-1) * BOARD_START)
        elif color == WHITE_COLOR:
            return State(BOARD_START)

def ptoi(x, y):
    """ Converts a board position to a board index """
    return x + BOARD_SIZE * y

def itop(i):
    """ Converts a board index to a board coordinate """
    return (i % BOARD_SIZE, i // BOARD_SIZE)


def boom_radius(i):
    """ Finds the board indexes which are in the radius of a boom at i

        Args:
            i: a board index

        Returns:
            A numpy array of vaid board indexes in the radius of i (excluding i)
    """
    x0, y0 = itop(i)

    poss = [(x0 - 1, y0 - 1), (x0 - 1, y0), (x0 - 1, y0 + 1),
            (x0, y0 - 1), (x0, y0 + 1),
            (x0 + 1, y0 - 1), (x0 + 1, y0), (x0 + 1, y0 + 1)] 
    
    return np.array([
        ptoi(x, y) for x, y in poss if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE
    ])

def move_positions(stack_i, height):
    """ Finds the board indexes which a stack at board index stack_i can move to

        Args:
            stack_i: a board index of the stack
            height: the height of the stack
        
        Returns:
            The board indexes which stack_i may move to
    """
    mp = []

    x0, y0 = itop(stack_i)

    # iterate over move distances
    for d in range(1, height + 1):
        
        if 0 <= y0 - d: mp.append(ptoi(x0, y0 - d))
        if BOARD_SIZE > y0 + d: mp.append(ptoi(x0, y0 + d))
        if 0 <= x0 - d: mp.append(ptoi(x0 - d, y0))
        if BOARD_SIZE > x0 + d: mp.append(ptoi(x0 + d, y0))
    
    return np.array(mp)

def move_name(num_tokens, si, ei):
    """ Gets the identifier for a move sending num_tokens from board index si 
        to board index ei """
    return (MOVE_ACTION, num_tokens, itop(si), itop(ei))

def boom_name(i):
    """ Gets the identifier for a boom at board index i"""
    return (BOOM_ACTION, itop(i))


if __name__ == "__main__":
    
    pos = (4, 4)
    height = 4

    pos2 = (3, 3)
    height2 = 3
    

    board = BOARD_EMPTY.copy()


    board[ptoi(*pos)] = height 
    board[ptoi(*pos2)] = -height2

    s = State(board)

    print(s)
    for mv, ns in s.next_states(opponent=True):
        print(f"Action: {mv}")
        print(str(ns))
