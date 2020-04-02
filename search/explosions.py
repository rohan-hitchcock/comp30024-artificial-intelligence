import itertools

EXPL_RAD = 1

BOARD_LENGTH = 8

class ExplosionComponent:
    #TODO: explain this class

    _components = None

    @staticmethod
    def create(positions):
        #TODO: fix docstring
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
        
        assert ExplosionComponent._components is None, "Already initialized."

        ungrouped = set(positions)

        components = []
        while ungrouped:
            to_visit = {ungrouped.pop()}
            component = set()
            while to_visit:

                s = to_visit.pop()
                for n in ungrouped:
                    if in_explosion_radius(s, n) and (n not in component):
                        to_visit.add(n)

                component.add(s)

            components.append(frozenset(component))
            ungrouped -= component

        ExplosionComponent._components = frozenset(components)

    @staticmethod
    def num_components():
        assert ExplosionComponent is not None, "Not initialized."
        return len(ExplosionComponent._components)
    
    @staticmethod
    def component_radii():
        return frozenset(explosion_radii(c) for c in ExplosionComponent._components)

    @staticmethod
    def component_radii_intersections():
        #TODO fix docstring
        """ Finds which sets of coordinates are not disjoint, and returns the
            intersection of those that are.
            Args:
                sets: A list of sets of explosion radii
            Returns:
                A list of disjoint sets, where each set contains the positions
                for which the corresponding group/(s) of stacks can be detonated from.
        """
        assert ExplosionComponent is not None, "Not initialized."
        
        sets = list(ExplosionComponent.component_radii())

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
        return frozenset(results)

    @staticmethod
    def components_containing(pos):
        assert ExplosionComponent is not None, "Not initialized."
        #pylint: disable=not-an-iterable
        return [c for c in ExplosionComponent._components if pos in c]
        
    @staticmethod
    def get():
        return ExplosionComponent._components

#*******************************************************************************

def explosion_radii(ps):
    #TODO: fix docstring
    """ Iterates over the points inside an explosion centered on p

        Args:
            ps: An iterable of valid board positions

        Yields:
            Valid board positions in the explosion radius of ps
    """
    r = set()
    for p in ps:
        r.update(explosion_radius(p))
    return frozenset(r)

def explosion_radius(pos):
    x, y = pos

    possible = itertools.product(
        range(x - EXPL_RAD, x + EXPL_RAD + 1),
        range(y - EXPL_RAD, y + EXPL_RAD + 1)
    )

    return (p for p in possible if is_valid_position(p))

def in_explosion_radius(p1, p2):
        """ Checks whether two positions are in the same explosion radius

            Args:
                p1, p2: valid board positions

            Returns:
                True if p1 and p2 are in each-others explosion radius and false
                otherwise
        """
        return all(abs(x - y) <= EXPL_RAD for x, y in zip(p1, p2))

def is_valid_position(p):
        """ Checks that the provided position is a valid board position

            Args:
                pos: the position to be checked
            Returns:
                A boolean representing if the position is valid or not
        """
        return all(0 <= x < BOARD_LENGTH for x in p)
