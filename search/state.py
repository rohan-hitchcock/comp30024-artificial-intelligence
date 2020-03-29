from math import ceil

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
        return f"{type(self).__name__}.{type(self).create_from_dict.__name__}({str(self)})"

    def get_state(self):
        return self.white.copy()

    def change_state(self, pos1, pos2, h):
        new_state_dict = self.white.copy()

        if pos1 == pos2:
            for g in self.goals:
                if pos1 in g:
                    new_black = self.black.copy()
                    new_goals = self.goals.copy()
                    for b in self.black:
                        if b in g:
                            new_black.pop(b)
                new_goals.pop(g)
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
        for g in self.goals:
            cost_estimate += min(stack_l1_norm_cost(s, h, g) for s, h in self.white.values())
        return cost_estimate


def stack_l1_norm_cost(p, h, goals):
    # TODO: is this the best place for this function?
    return min(sum(ceil(abs(x - y) / h) for x, y in zip(p, g)) for g in goals)


if __name__ == "__main__":
    pass
