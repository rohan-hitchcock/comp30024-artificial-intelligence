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

    def __str__(self):
        return str(self.white)

    def __repr__(self):
        return f"{type(self).__name__}.{type(self).create_from_dict.__name__}({str(self)})"

    def __hash__(self):
        return hash(tuple(self.white.items()))

    def __eq__(self, other):
        return self.white == other.white

    def get_state(self):
        return self.white.copy()

    def change_state(self, pos1, pos2, h):
        new_state_dict = self.white.copy()
        if self.white[pos1] == h:
            new_state_dict.pop(pos1)
        else:
            new_state_dict[pos1] -= h

        if pos2 in new_state_dict:
            new_state_dict[pos2] += h
        else:
            new_state_dict[pos2] = h
            
        return State.create_from_dict(new_state_dict)

    @staticmethod
    def create_from_dict(white):
        """ Creates a board object from a json file"""
        s = State()

        for c, height in white.items():
            s.white[c] = height
        return s

    def estimate_cost(self, goal_sets):
        cost_estimate = 0
        for g in goal_sets:
            cost_estimate += min(stack_l1_norm_cost(s, h, g) for s, h in self.white.items())
        return cost_estimate

def stack_l1_norm_cost(p, h, goals):
    #TODO: is this the best place for this function?
    return min(sum(ceil( abs(x - y) / h)  for x, y in zip(p, g)) for g in goals) 

if __name__ == "__main__":
    s1 = State()
    s2 = State.create_from_dict({(0, 1): 10})

    print(f"hash(s1) == {hash(s1)}")
    print(f"hash(str(s1)) == {hash(str(s1))}")
    print(f"hash(repr(s1)) == {hash(repr(s1))}")
    print()
    print(f"hash(s2) == {hash(s2)}")
    print(f"hash(str(s2)) == {hash(str(s2))}")
    print(f"hash(repr(s2)) == {hash(repr(s2))}")


    class Test:
        def __init__(self):
            pass

    s = Test()
    t = Test()
    print(hash(s))
    print(hash(t))
