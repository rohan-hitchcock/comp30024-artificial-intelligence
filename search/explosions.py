from search import board

class ExplosionComponent:
    """ This class is a Singleton which represents the components of a set of 
        Stacks. We define the components of a set of stacks to be the disjoint
        partition of the stacks such that for any component, if any stack in 
        the component explodes then any other stack in the component will 
        necessarily explode.
        
        It is reletively expensive to calculate all components, and componets
        of black tokens will only ever be removed from the board. Therefore 
        this singleton class means that repeated component calculations are 
        not done in the State class as tokens are removed from the board.
    """

    #When initialized, a frozenset of disjoint frozensets. The elements of each
    #set will explode if any other element explode, and will not explode if an
    #element of another set explodes
    _components = None

    @staticmethod
    def create(positions):
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
        """ Returns the number of components"""
        assert ExplosionComponent is not None, "Not initialized."
        return len(ExplosionComponent._components)
    
    @staticmethod
    def component_radii():
        """ Returns the explosion radii of each component.
        
            Returns:
                A frozenset of frozensets, which are the explosion radii
                of the componets"""
        assert ExplosionComponent is not None, "Not initialized."
        #pylint:disable=not-an-iterable
        return frozenset(board.explosion_radii(c) for c in ExplosionComponent._components)

    @staticmethod
    def component_radii_intersections():
        """ Finds the fewest number of disjoint sets such that a position
            from every explosion radius is contained in at least one set

            Returns:
                A frozenset of frozensets as described
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
    def get():
        """ Gets the instance """
        return ExplosionComponent._components
