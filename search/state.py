import itertools
import json
from collections import namedtuple

from search.explosions import ExplosionComponent, explosion_radius, explosion_radii, is_valid_position

BOARD_LENGTH = 8

BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

Stack = namedtuple("Stack", ["pos", "height"])

class State:

    def __init__(self, white, black, goals, move):
        """ Initializes a state.

            Args:
                white: a frozenset of Stack objects representing white tokens
                black: a frozenset of Stack objects representing black tokens
                goals: a frozenset of frozensets of goal positions
                move: the move taken to get ot this state.
        """
        self.white = white
        self.black = black
        self.goals = goals
        self.prev_move = move

    def __str__(self):
        #TODO fix this
        #return f"w: {set(self.white)}\nb: {set(self.black)}\ng: {set(self.goals)}\n"
        return f"w: {set(self.white)}\nm: {self.prev_move}"

    def __repr__(self):
        return f"{type(self).__name__}.{type(self).create_from_dict.__name__}({str(self)}, {str(self.black)}, {str(self.goals)})"

    def __hash__(self):
        return hash((self.white, self.black, self.goals))
        
    def __eq__(self, other):
        return self.white == other.white and self.black == other.black and self.goals == other.goals

    def stack_positions(self, color=None):
        """ An iterator over every board position containing a stack.

            Args:
                color: (optional) set to BLACK or WHITE to only get positions
                of the selected color

            Yields:
                Board positions p for which self.height_at(p, color) is not 0
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
        
        for b in self.black:
            if p == b.pos:
                return BLACK + str(b.height)

        for w in self.white:
            if p == w.pos:
                return WHITE + str(w.height)
        return "" 
    
    def get_print_dict(self):
        """ Returns a dictionary of this board suitible for printing"""
        return {p: self.as_string(p) for p in State.positions()}

    def generate_next_states(self):
        """ Creates a list of State objects reachable from the
            current state

            Returns:
                A list of State objects
        """
        states = []

        for white_stack in self.white:

            #check if a boom move is sensible
            if any((white_stack.pos in g) for g in self.goals):
                states.append(self.change_state_boom(white_stack))
            
            for pos, num_tokens in self.possible_moves(white_stack):
                states.append(self.change_state_move(white_stack, pos, num_tokens))
        return states

    def change_state_boom(self, stack):

        #a component remains on the board if and only if any one of its elements
        #remains on the board
        #pylint: disable=not-an-iterable
        remaining_components = {
                c: explosion_radii(c) for c in ExplosionComponent.get() 
                if any(b.pos in c for b in self.black)
            }

        white_to_explode = {stack.pos}
        exploded = set()
        
        while white_to_explode:

            exploder = white_to_explode.pop()
            exploded.add(exploder)

            #look at white tokens in the explosion radius radius
            radius = set(explosion_radius(exploder))
            for w in self.white:
                if w.pos in radius and w.pos not in exploded:
                    white_to_explode.add(w.pos)

            #look at components
            for c in list(remaining_components.keys()):
                
                #the exploder will blow up this component
                if exploder in remaining_components[c]:
                    
                    #set all tokens in radius to exploded
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
        
        #TODO: is this format for move ok?
        return State(new_white, new_black, new_goals, stack.pos)

    def change_state_move(self, stack, new_pos, num_tokens):

        new_white = self.white.difference([stack])

        new_height = num_tokens
        for w in self.white:
            if w.pos == new_pos:
                new_white = new_white.difference([w])
                new_height += w.height

        new_white |= {Stack(new_pos, new_height)}

        if stack.height > num_tokens:
            new_white |= {Stack(stack.pos, stack.height - num_tokens)}
        

        return State(new_white, self.black, self.goals, (stack.pos, new_pos, num_tokens))

    def possible_moves(self, stack):
        """ Generates all moves possible for a given white position wp.

            Args:
                wp: the coordinate of a white stack
                h: the height of wp

            Yields:
                positions on this board which are a valid move for a white
                stack at wp
        """
        wpx, wpy = stack.pos
        h = stack.height
        
        # tests whether a generated position e is a valid move from s
        valid = lambda s, e: is_valid_position(e) and (s != e) and all(e != b.pos for b in self.black)

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
    def positions():
        """ Iterates over every valid board position

            Yields:
                valid board positions.
        """
        yield from itertools.product(range(BOARD_LENGTH), repeat=2)

    @staticmethod
    def create_from_json(json_fp):
        """ Creates a board object from a json file"""
        black = []
        white = []
        for c, stacks in json.load(json_fp).items():

            for height, x, y in stacks:

                if c == J_BLACK_NAME:
                    black.append(Stack(pos=(x, y), height=height))
                else:
                    white.append(Stack(pos=(x, y), height=height))
        
        
        ExplosionComponent.create(b.pos for b in black)
        
        if ExplosionComponent.num_components() > len(white):
            goals = ExplosionComponent.component_radii_intersections()
        else:
            goals = ExplosionComponent.component_radii()

        return State(frozenset(white), frozenset(black), goals, None)


if __name__ == "__main__":
    import sys
    import util
    with open(sys.argv[1]) as fp:
        s = State.create_from_json(fp)

    util.print_board(s.get_print_dict())
