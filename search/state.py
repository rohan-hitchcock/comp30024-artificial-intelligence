import itertools
import json
from collections import namedtuple

from search.explosions import ExplosionComponent
from search import board

BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

#Represents stacks, pos is board position (a 2-tuple) and height an integer
Stack = namedtuple("Stack", ["pos", "height"])

class State:
    """ A State is an immutable object describing the state of a board, that is 
        the white and black stack data. It also stores information about the 
        current goals in this State, in the context of a search problem"""

    def __init__(self, white, black, goals):
        """ Initializes a State. 

            Args:
                white: a frozenset of Stack objects representing white tokens
                black: a frozenset of Stack objects representing black tokens
                goals: a frozenset of frozensets of goal positions
                move: the move taken to get ot this state.
        """
        self.white = white
        self.black = black
        self.goals = goals

    def __str__(self):
        return f"w: {set(self.white)}\nb: {set(self.black)}\ng: {set(self.goals)}\n"

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.white)}, {repr(self.black)}, {repr(self.goals)})"

    def __hash__(self):
        return hash((self.white, self.black, self.goals))
        
    def __eq__(self, other):
        return self.white == other.white and self.black == other.black and self.goals == other.goals

    def stack_positions(self, color=None):
        """ An iterator over every position containing a stack.

            Args:
                color: (optional) set to BLACK or WHITE to only get positions
                of the selected color

            Yields:
                Board positions (2-tuples) which are the locations of stacks
        """  
        if color is None:
            stacks = itertools.chain(
                (b.pos for b in self.black), 
                (w.pos for w in self.white)
                )
        else:
            if color == WHITE:
                stacks = (w.pos for w in self.white)
            else:
                stacks = (b.pos for b in self.black)
        yield from stacks
        
    def as_string(self, p):
        """ Gets whatever is at position p (possibly nothing) as a string 
            suitible for printing on a board.
            
            Args:
                p: a valid board position
            Returns:
                A string describing whatever is at position p in this state.
        """

        for b in self.black:
            if p == b.pos:
                return BLACK + str(b.height)

        for w in self.white:
            if p == w.pos:
                return WHITE + str(w.height)
        return "" 
    
    def get_board_dict(self):
        """ Returns a dictionary of this board suitible for printing"""
        return {p: self.as_string(p) for p in board.positions()}

    def generate_next_states(self):
        """ Finds the State objects reachable from the current state

            Returns:
                A list of State objects
        """
        states = []

        for white_stack in self.white:

            #check if a boom action is sensible
            if any((white_stack.pos in g) for g in self.goals):
                states.append(self.change_state_boom(white_stack))
            
            #look for valid move actions
            for pos, num_tokens in self.possible_moves(white_stack):
                states.append(self.change_state_move(white_stack, pos, num_tokens))
        return states

    def change_state_boom(self, stack):
        """ Generates the State object representing the successor of this state
            after the specified stack explodes.

            Args:
                A Stack which is in this state.

            Returns:
                A State object which is the result of stack exploding thin this
                State.
        """

        #a component remains on the board if and only if any one of its elements
        #remains on the board
        #pylint: disable=not-an-iterable
        remaining_components = {
                c: board.explosion_radii(c) for c in ExplosionComponent.get() 
                if any(b.pos in c for b in self.black)
            }

        white_to_explode = {stack.pos}
        exploded = set()
        while white_to_explode:

            exploder = white_to_explode.pop()
            exploded.add(exploder)

            #look at white tokens in the explosion radius radius
            radius = set(board.explosion_radius(exploder))
            for w in self.white:
                if w.pos in radius and w.pos not in exploded:
                    white_to_explode.add(w.pos)

            #look at components
            for c in list(remaining_components.keys()):
                
                #the exploder will blow up this component
                if exploder in remaining_components[c]:
                    
                    #set all tokens in component to exploded
                    exploded.update(c)

                    #check for any other white tokens in this radius
                    for w in self.white:
                        if w.pos in remaining_components[c] and w.pos not in exploded:
                            white_to_explode.add(w.pos)

                    #remove the component
                    del remaining_components[c]

        #remove any exploded goals, white stacks and black stacks
        new_goals = frozenset(g for g in self.goals if g.isdisjoint(exploded))
        new_black = frozenset(b for b in self.black if b.pos not in exploded)
        new_white = frozenset(w for w in self.white if w.pos not in exploded)
        
        return State(new_white, new_black, new_goals)

    def change_state_move(self, stack, new_pos, num_tokens):
        """ Generates the State object which is the result of stack moving 
            num_tokens to new_pos in this State.

            Args:
                stack: A Stack in this State
                new_pos: a valid new position for stack considering the current State
                num_tokens: a valid number of tokens to move from stack

            Returns:
                The State object which is the successor of this state after 
                executing the move described above.
        """

        new_white = self.white.difference([stack])

        new_height = num_tokens
        for w in self.white:
            if w.pos == new_pos:
                new_white = new_white.difference([w])
                new_height += w.height

        new_white |= {Stack(new_pos, new_height)}

        if stack.height > num_tokens:
            new_white |= {Stack(stack.pos, stack.height - num_tokens)}
        
        return State(new_white, self.black, self.goals)

    def possible_moves(self, stack):
        """ Generates all moves possible for stack in the current State.

            Args:
                stack: the stack for which to generate move

            Yields:
                tuples of the form (pos, n) where pos is a 2-tuple which 
                represents the position to move stack to and n is the number of
                tokens to move.
        """
        wpx, wpy = stack.pos
        h = stack.height
        
        # tests whether a generated position e is a valid move from s
        valid = lambda s, e: board.is_valid_position(e) and (s != e) and all(e != b.pos for b in self.black)

        moves = []
        for n in range(1, h + 1):
            for x in range(wpx - h, wpx + h + 1):
                if valid(stack.pos, (x, wpy)):
                    moves.append(((x, wpy), n))
            for y in range(wpy - h, wpy + h + 1):
                if valid(stack.pos, (wpx, y)):
                    moves.append(((wpx, y), n))
        return moves

    @staticmethod
    def create_from_json(json_fp):
        """ Creates a State object from a json file. Also initializes the 
            singleton ExplosionComponent
        
            Args:
                json_fp: file pointer object for a json file of State data
            
            Returns:
                A State object
        """
        black = []
        white = []
        for c, stacks in json.load(json_fp).items():

            for height, x, y in stacks:

                if c == J_BLACK_NAME:
                    black.append(Stack(pos=(x, y), height=height))
                else:
                    white.append(Stack(pos=(x, y), height=height))
        
        ExplosionComponent.create(b.pos for b in black)
        
        #check if we have enough tokens to send one to each component
        if ExplosionComponent.num_components() > sum(w.height for w in white): 
            goals = ExplosionComponent.component_radii_intersections()
        
        #if we do not set the intersections between components as the goal
        else:
            goals = ExplosionComponent.component_radii()

        return State(frozenset(white), frozenset(black), goals)

if __name__ == "__main__":
    pass
