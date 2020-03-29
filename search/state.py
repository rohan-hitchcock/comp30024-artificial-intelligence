import itertools
from math import ceil
from search.board import Board

BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

BOARD_LENGTH = 8

EXPL_RAD = 1


class State:

    def __init__(self):
        """ Initialises an empty state """
        self.white = dict()
        self.black = dict()
        self.goals = list()

    def __str__(self):
        return str(self.white)

    def __repr__(self):
        return f"{type(self).__name__}.{type(self).create_from_dict.__name__}({str(self)}, {str(self.black)}, {str(self.goals)})"

    def __hash__(self):
        return hash(tuple(self.white.items()) + tuple(self.black.items()) + tuple(str(self.goals)))

    def __eq__(self, other):
        return self.white == other.white and self.black == other.black and self.goals == other.goals

    def get_state(self):
        return self.white.copy()


    """ I put this here so I could use it below, obviously if it all works we'd clean it up/ merge the classes"""
    def components(self):
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
        ungrouped_stacks = set(itertools.chain(self.black, self.white))

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


    def change_state(self, pos1, pos2, h):
        new_state_dict = self.white.copy()

        """ if its the move which stays still, check if that position is a goal position, if it is
            remove all black and white tokens that would be caught in the components at that position"""
        if pos1 == pos2:
            for g in self.goals:
                if pos1 in g:
                    new_black = self.black.copy()
                    new_goals = self.goals.copy()
                    components = self.components()
                    for c in components:
                        if pos1 in c:
                            for b in self.black:
                                if b in c:
                                    new_black.pop(b)
                            for w in self.white:
                                if w in c and w != pos1:
                                    new_state_dict.pop(w)
                    new_goals.remove(g)
                    new_state_dict.pop(pos1)
                    return State.create_from_dict(new_state_dict, new_black, new_goals)


        if self.white[pos1] == h:
            new_state_dict.pop(pos1)
        else:
            new_state_dict[pos1] -= h

        if pos2 in new_state_dict:
            new_state_dict[pos2] += h
        else:
            new_state_dict[pos2] = h

        return State.create_from_dict(new_state_dict, self.black, self.goals)

    @staticmethod
    def create_from_dict(white, black, goals):
        """ Creates a board object from a json file"""
        s = State()

        s.white = white.copy()
        s.black = black.copy()
        s.goals = goals.copy()
        return s

    def estimate_cost(self):
        cost_estimate = 0
        """ added guard to stop going down paths that wont result in goal, didnt use inf because A* registers
                that as something else """
        sum = 0
        for n in self.white.values():
            sum += n
        if sum < len(self.goals):
            return 10000000000
        for g in self.goals:
            cost_estimate += min(stack_l1_norm_cost(s, h, g) for s, h in self.white.items()) + 1
        return cost_estimate


def stack_l1_norm_cost(p, h, goals):
    # TODO: is this the best place for this function?
    return min(sum(ceil(abs(x - y) / h) for x, y in zip(p, g)) for g in goals)


if __name__ == "__main__":
    pass
