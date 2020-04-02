from search import board

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
                    if board.in_explosion_radius(s, n) and (n not in component):
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
        assert ExplosionComponent is not None, "Not initialized."
        #pylint:disable=not-an-iterable
        return frozenset(board.explosion_radii(c) for c in ExplosionComponent._components)

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
