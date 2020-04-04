import heapq
from collections import defaultdict as dd
import search.board as bd
import itertools


class PriorityNode:
    """ This class is used to encode priority information about a node (anything).
        It allows custom implementation of a 'comparable' interface (in Java
        terminology).

        Before use, PriorityNode.__lt__ must be assigned to a callable to define
        how comparison works.
    """

    def __init__(self, node):
        self.node = node

    def __eq__(self, other):
        self.node == other.node

    def __lt__(self, other):
        # Choose how this when the class is used!
        pass

    def __gt__(self, other):
        return not self < other

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other


def a_star_new(start, goals, cost_to_goal, expand_node, board, inposition):
    """ The world-famous A* algorithm. Note it is generic and does not assume
        anything about what a node is.

        Args:
            start: the state to start the search from
            goals: a set of goal states
            cost_to_goal: a callable of the form cost_to_goal(state, goals) which
            estimates the cost reaching any goal from state. Must return something
            which can be cast to a float.
            expand_node: a callable of the form expand_node(node) which returns
            an iterable of next-nodes from node.

        Returns:
            A sequence of states starting with `start' and ending with some
            state in `goals' (inclusive of both)
    """
    if not goals:
        return None
    if start not in board.white:
        for f in board.white:
            if f not in inposition:
                start = f
            if f in inposition and board.height_at(f) > 1:
                start = f
    open_nodes = [PriorityNode(start)]

    total_goals = goals.copy()
    for pos in board.stack_positions(color='w'):
        if pos != start:
            total_goals.append({pos})
    print("********* NEW TOKEN ***********")
    print("total goals are now:" + str(total_goals))

    prev_node = {start: None}
    cost = dd(lambda: float("inf"))
    cost[start] = 0
    priority = {start: cost_to_goal(start, start, goals, board, inposition)}

    PriorityNode.__lt__ = lambda x, y: priority[x.node] < priority[y.node]

    prev = start
    merged = None
    while open_nodes:
        curr_node = heapq.heappop(open_nodes).node
        print("***********" + str(curr_node) + "***********")
        # if curr_node in board.white and curr_node != start:
        #     board.merge_stacks(prev, curr_node)
        #     prev = curr_node

        for g in total_goals:
            if curr_node in g and g in goals:
                inposition.append(curr_node)
                if board.height_at(prev) > 1:
                    goals.remove(g)
                    total_goals.remove(g)
                else:
                    goals.remove(g)
                    total_goals.remove(g)
                update_priorities(priority, cost, cost_to_goal, board, goals, curr_node, inposition)
            elif curr_node in g and g not in goals:
                board.merge_stacks(prev, curr_node)
                merged = g

        if prev in inposition:
            board.move(prev, curr_node, board.height_at(prev) - 1)
        elif not merged:
            board.move(prev, curr_node, board.height_at(prev))

        if not goals:
            return path_to(curr_node, prev_node)

        print(board.height_at(curr_node))

        if merged:
            total_goals.remove(merged)
            update_priorities(priority, cost, cost_to_goal, board, goals, curr_node, inposition)
            merged = None

        heap_changed = False
        for o in expand_node(curr_node):
            print(o)
        update_priorities(priority, cost, cost_to_goal, board, goals, curr_node, inposition)
        for neighbor in expand_node(curr_node):

            if cost[neighbor] > cost[curr_node] + 1:

                if cost[neighbor] == float("inf"):
                    open_nodes.append(PriorityNode(neighbor))

                cost[neighbor] = 1 + cost[curr_node]
                priority[neighbor] = cost[neighbor] + cost_to_goal(curr_node, neighbor, goals, board, inposition)
                prev_node[neighbor] = curr_node

                heap_changed = True
        print(priority)
        if heap_changed:
            heapq.heapify(open_nodes)
        prev = curr_node
    return None


def update_priorities(priority, cost, cost_to_goal, board, goals, curr_node, inposition):
    for key in priority:
        priority[key] = cost[key] + cost_to_goal(curr_node, key, goals, board, inposition) + l1_norm_cost(curr_node,
                                                                                                          [key])


def find_paths_new(board):
    """ Finds paths for white stacks to destroy all black tokens."""
    goal_states = generate_goal_states(board)

    poss_paths = dict()
    inposition = list()
    whites = dict(board.white)

    for white_stack in whites:
        path_to_goal = a_star_new(white_stack, goal_states, cost_new, board.possible_moves_new, board, inposition)
        print(goal_states)
        if path_to_goal is not None:
            poss_paths[(white_stack, path_to_goal[-1])] = path_to_goal

    if goal_states:
        print(f"\nWARNING: {len(goal_states)} goal(s) not achieved.")
    return poss_paths


def generate_goal_states(board):
    """ Generates a list of disjoint sets of goal positions, given a board. This
        can be thought of as a formula in conjunctive normal form, that is at
        least one goal position from each set must be achieved to complete the
        goal.

        Args:
            A Board object.

        Returns:
            A list of sets of goal positions.
    """
    explosion_radii = [set(board.explosion_radius(c)) for c in board.components(color=bd.BLACK)]
    return intersecting_radii(explosion_radii)


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


def expand_free(node):
    """ Expands a node to all four of its north, south, east, west neighbors.
        Used for testing.

        Args:
            node: a 2-tuple to expand

        Returns:
            A list of four 2-tuples L1-distance 1 from node
    """
    x, y = node
    return [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]


def path_to(node, prev_node):
    """ Reconstructs the path to node.

        Args:
            node: the node the path is to
            prev_node: a dictionary of node predecessors, keyed by node.

        Returns:
            A sequence of nodes (as a list) ending in node
    """
    l = [node]
    while prev_node[node] is not None:
        l.append(prev_node[node])
        node = prev_node[node]
    l.reverse()
    return l


def l1_norm_cost(p, goals):
    """ Returns the minimum L1-norm distance of p to any point in goals.

        Args:
            p: a 2-tuple to calculate the distances from.
            goals: a finite iterable of goal nodes (2-tuples)
        Returns:
            The minimum distance of p to any point in goals
    """
    return min(sum(abs(x - y) for x, y in zip(p, g)) for g in goals)


def cost_new(self, p, goals, board, inposition):
    """ Returns the minimum L1-norm distance of p to any point in goals.

        Args:
            p: a 2-tuple to calculate the distances from.
            goals: a finite iterable of goal nodes (2-tuples)
        Returns:
            The minimum distance of p to any point in goals
    """
    new_goals = set()
    for g in goals:
        new_goals.update(g)
    for pos in board.stack_positions(color='w'):
        if pos != self and (pos not in inposition):
            new_goals.update({pos})
    return min(sum(abs(x - y) for x, y in zip(p, g)) for g in new_goals)


if __name__ == "__main__":

    goals = {(1, 10), (11, 3)}

    start = (0, 0)

    for n in a_star(start, goals, l1_norm_cost, expand_free):
        print(n)
