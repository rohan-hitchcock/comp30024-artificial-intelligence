import itertools

# the side length of the board
BOARD_LENGTH = 8

# the radius of an explosion of the board
EXPLOSION_RADIUS = 1


def positions():
    """ Iterates over every valid board position

        Yields:
            valid board positions.
    """
    yield from itertools.product(range(BOARD_LENGTH), repeat=2)


def is_valid_position(p):
    """ Checks that the provided position is a valid board position

        Args:
            pos: the position to be checked
        Returns:
            A boolean representing if the position is valid or not
    """
    return all(0 <= x < BOARD_LENGTH for x in p)


def in_explosion_radius(p1, p2):
    """ Checks whether two positions are in the same explosion radius

        Args:
            p1, p2: valid board positions

        Returns:
            True if p1 and p2 are in each-others explosion radius and false
            otherwise
    """
    return all(abs(x - y) <= EXPLOSION_RADIUS for x, y in zip(p1, p2))


def explosion_radius(pos):
    """ Returns an iterable of positions which are in the explosion radius of
        an explosion centered on pos.

        Args:
            pos: A valid board position, the center of the explosion.

        Yields:
            Valid board positions in the explosion radius of pos
    """
    x, y = pos
    possible = itertools.product(
        range(x - EXPLOSION_RADIUS, x + EXPLOSION_RADIUS + 1),
        range(y - EXPLOSION_RADIUS, y + EXPLOSION_RADIUS + 1))

    return (p for p in possible if is_valid_position(p))


def explosion_radii(ps):
    """ Finds the explosion radii of an iterable of positions ps

        Args:
            ps: An iterable of valid board positions

        Returns:
            A frozenset of valid board positions in the collective explosion radius of
             all elements of ps
    """
    r = set()
    for p in ps:
        r.update(explosion_radius(p))
    return frozenset(r)
