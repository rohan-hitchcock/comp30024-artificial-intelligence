import itertools
import json

BLACK = 'b'
WHITE = 'w'

J_WHITE_NAME = "white"
J_BLACK_NAME = "black"

BOARD_LENGTH = 8

EXPL_RAD = 1


class State:
    length = BOARD_LENGTH
    expl_rad = EXPL_RAD

    def __init__(self):
        """ Initialises an empty state """
        self.white = dict()
        self.black = dict()
        self.goals = list()
        self.created_from = "# Start"

    def __str__(self):
        return str(self.white)

    def __repr__(self):
        return f"{type(self).__name__}.{type(self).create_from_dict.__name__}({str(self)}, {str(self.black)}, {str(self.goals)})"

    def __hash__(self):
        return hash(
            tuple(self.white.items()) +
            tuple(self.black.items()) +
            tuple(self.goals)
        )

    def __eq__(self, other):
        return self.white == other.white and self.black == other.black and self.goals == other.goals

    def __hash__(self):
        return hash(tuple(self.white.items()))

    def __eq__(self, other):
        return self.white == other.white

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
        return {p: self.as_string(p) for p in State.positions()}

    def components(self, color=None):
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
        ungrouped_stacks = set(self.stack_positions(color=color))

        components = []
        while ungrouped_stacks:
            to_visit = {ungrouped_stacks.pop()}
            component = set()
            while to_visit:

                s = to_visit.pop()
                for n in ungrouped_stacks:
                    if State.in_explosion_radius(s, n) and (n not in component):
                        to_visit.add(n)

                component.add(s)

            components.append(component)
            ungrouped_stacks -= component
        return components

    @staticmethod
    def move_string(pos1, pos2, h):
        x1, y1 = pos1
        x2, y2 = pos2
        return "MOVE {} from {} to {}.".format(h, (x1, y1), (x2, y2))

    @staticmethod
    def boom_string(pos1):
        x, y = pos1
        return "BOOM at {}.".format((x, y))

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
                    return State.create_from_dict(new_state_dict, new_black, new_goals, State.boom_string(pos1))

        if self.white[pos1] == h:
            new_state_dict.pop(pos1)
        else:
            new_state_dict[pos1] -= h

        if pos2 in new_state_dict:
            new_state_dict[pos2] += h
        else:
            new_state_dict[pos2] = h

        return State.create_from_dict(new_state_dict, self.black, self.goals, State.move_string(pos1, pos2, h))

    def possible_moves(self, wp):
        """ Generates all moves possible for a given white position wp.

            Args:
                wp: the coordinate of a white stack
                h: the height of wp

            Yields:
                positions on this board which are a valid move for a white
                stack at wp
        """
        wpx, wpy = wp
        h = self.white[wp]

        # tests whether a generated position e is a valid move from s
        valid = lambda s, e: State.is_valid_position(e) and (s != e) and (e not in self.black)

        moves = []
        for n in range(1, h + 1):
            for x in range(wpx - h, wpx + h + 1):
                if valid(wp, (x, wpy)):
                    moves.append(((x, wpy), n))
            for y in range(wpy - h, wpy + h + 1):
                if valid(wp, (wpx, y)):
                    moves.append(((wpx, y), n))

        moves.append(((wpx, wpy), h))

        return moves

    def generate_goal_states(self):
        """ Generates a list of disjoint sets of goal positions, given a board. This
            can be thought of as a formula in conjunctive normal form, that is at
            least one goal position from each set must be achieved to complete the
            goal.
            Args:
                A Board object.
            Returns:
                A list of sets of goal positions.
        """
        explosion_radii = [set(self.explosion_radius(c)) for c in self.components(color=BLACK)]
        sum = 0
        for h in self.white.values():
            sum += h
        if sum < len(explosion_radii):
            self.goals = State.intersecting_radii(explosion_radii)
        else:
            self.goals = explosion_radii

    @staticmethod
    def intersecting_radii(sets):
        """ Finds which sets of coordinates are not disjoint, and returns the
            intersection of those that are.
            Args:
                sets: A list of sets of explosion radii
            Returns:
                A list of disjoint sets, where each set contains the positions
                for which the corresponding group/(s) of stacks can be detonated from.
        """
        results = []
        while sets:
            first, rest = sets[0], sets[1:]
            merged = False
            sets = []
            for s in rest:
                if s and s.isdisjoint(first):
                    sets.append(s)
                else:
                    first &= s
                    merged = True
            if merged:
                sets.append(first)
            else:
                results.append(first)
        return results

    @staticmethod
    def create_from_dict(white, black, goals, move):
        s = State()

        s.white = white.copy()
        s.black = black.copy()
        s.goals = [frozenset(g) for g in goals]
        s.created_from = move
        return s

    @staticmethod
    def positions():
        """ Iterates over every valid board position

            Yields:
                valid board positions.
        """
        yield from itertools.product(range(State.length), repeat=2)

    @staticmethod
    def explosion_radius(ps):
        """ Iterates over the points inside an explosion centered on p

            Args:
                ps: An iterable of valid board positions

            Yields:
                Valid board positions in the explosion radius of ps
        """
        for p in ps:
            x, y = p
            yield from (
                p for p in itertools.product(
                range(x - EXPL_RAD, x + EXPL_RAD + 1),
                range(y - EXPL_RAD, y + EXPL_RAD + 1)
            ) if State.is_valid_position(p)
            )

    @staticmethod
    def in_explosion_radius(p1, p2):
        """ Checks whether two positions are in the same explosion radius

            Args:
                p1, p2: valid board positions

            Returns:
                True if p1 and p2 are in each-others explosion radius and false
                otherwise
        """
        return all(abs(x - y) <= State.expl_rad for x, y in zip(p1, p2))

    @staticmethod
    def is_valid_position(p):
        """ Checks that the provided position is a valid board position

            Args:
                pos: the position to be checked
            Returns:
                A boolean representing if the position is valid or not
        """
        return all(0 <= x < State.length for x in p)

    @staticmethod
    def create_from_json(json_fp):
        """ Creates a board object from a json file"""
        s = State()

        for c, stacks in json.load(json_fp).items():

            for height, x, y in stacks:

                if c == J_BLACK_NAME:
                    s.black[(x, y)] = height
                else:
                    s.white[(x, y)] = height
        return s


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
