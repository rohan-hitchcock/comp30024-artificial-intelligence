import heapq
from collections import defaultdict as dd
from math import ceil

import itertools
from search.state import State


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


def a_star(start, cost_to_goal, expand_node, goal_reached):
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
    open_nodes = [PriorityNode(start)]

    prev_node = {start: None}
    cost = dd(lambda: float("inf"))
    cost[start] = 0

    priority = {start: cost_to_goal(start)}

    PriorityNode.__lt__ = lambda x, y: priority[x.node] < priority[y.node]

    while open_nodes:

        curr_node = heapq.heappop(open_nodes).node

        if goal_reached(curr_node):
            print(len(open_nodes))
            return path_to(curr_node, prev_node)

        heap_changed = False
        for neighbor in expand_node(curr_node):
            if cost[neighbor] > cost[curr_node] + 1:

                neighbor_to_goal_cost = cost_to_goal(neighbor)

                if neighbor_to_goal_cost == 10000000000:
                    cost[neighbor] = 1 + cost[curr_node]
                    continue

                if cost[neighbor] == float("inf"):
                    open_nodes.append(PriorityNode(neighbor))

                cost[neighbor] = 1 + cost[curr_node]
                priority[neighbor] = cost[neighbor] + neighbor_to_goal_cost
                prev_node[neighbor] = curr_node

                heap_changed = True

        if heap_changed:
            heapq.heapify(open_nodes)

    return None


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


def all_goals_reached(state):
    """ The goal test; checks whether a state has white stacks in all of it's goal groups.
        Args:
            state: The State object were testing

        Returns:
            Whether the test is passed or not
    """
    for g in state.goals:

        if not any(pos in g for pos in state.white):
            return False
    return True


def estimate_cost(state):
    """ The cost heuristic; uses the collective minimum l1 norm distance as an estimate, but
        also considers the number of remaining goal groups, and attempts to prune branches
        that will likely not reach a solution.
        Args:
            state: The State object were estimating a cost for

        Returns:
            The cost estimate as an integer.
    """
    cost_estimate = 0
    sum = 0

    for n in state.white.values():
        sum += n
    if sum < len(state.goals):
        state.generate_goal_states()
        if sum < len(state.goals):
            return 10000000000
    for g in state.goals:
        cost_estimate += min(stack_l1_norm_cost(s, h, g) for s, h in state.white.items()) + 1

    return cost_estimate


def generate_states(state):
    """ Creates a list of State objects reachable from the given state
        Args:
            state: The State object were generating states from.

        Returns:
            A list of State objects
    """
    states = []
    for c in state.white.keys():
        for t, h in state.possible_moves(c):
            temp = state.change_state(c, t, h)
            if temp != state:
                states.append(temp)
    return states


def stack_l1_norm_cost(p, h, goals):
    """ Returns the minimum cost from position p to any position in the set of coordinates goals,
        with the possibility of moving h squares at a time.
        Args:
            p: the position moving from
            h: the height of the stack at that position
            goals: a set of positions

        Returns:
            The minimum distance to a position in goals from p, moving h steps at a time.
    """
    return min(sum(ceil(abs(x - y) / h) for x, y in zip(p, g)) for g in goals)


def whole_board_search(board):
    """ Uses A* to generate the sequence of States (if they exist) the board must
        go through in order to remove all black stacks
        Args:
            board: The initial State of the board.

        Returns:
            A list of States, one move apart, resulting in all black stacks being removed



    """
    board.generate_goal_states()

    print(f"goals: {board.goals}")

    cost_heuristic = estimate_cost
    expander = generate_states
    goal_reached = all_goals_reached

    return a_star(board, cost_heuristic, expander, goal_reached)


if __name__ == "__main__":
    pass
