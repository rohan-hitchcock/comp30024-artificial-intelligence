import heapq
from collections import defaultdict as dd
from math import ceil

import search.board as bd
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


def a_star(start, goals, cost_to_goal, expand_node, goal_reached):
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

    """ cost function now just takes state, state considers its own goals"""
    priority = {start: cost_to_goal(start)}

    PriorityNode.__lt__ = lambda x, y: priority[x.node] < priority[y.node]

    while open_nodes:

        curr_node = heapq.heappop(open_nodes).node

        """ same here, goal_reached checks the goals belonging to its own state """
        if goal_reached(curr_node):
            print(len(open_nodes))
            return path_to(curr_node, prev_node)

        heap_changed = False
        for neighbor in expand_node(curr_node):
            if cost[neighbor] > cost[curr_node] + 1:
                
                neighbor_to_goal_cost = cost_to_goal(neighbor)

                """
                if neighbor_to_goal_cost == 10000000000:
                    cost[neighbor] = 1 + cost[curr_node]
                    continue
                """


                if cost[neighbor] == float("inf"):
                    open_nodes.append(PriorityNode(neighbor))

                cost[neighbor] = 1 + cost[curr_node]
                priority[neighbor] = cost[neighbor] + neighbor_to_goal_cost
                prev_node[neighbor] = curr_node

                heap_changed = True

        if heap_changed:
            heapq.heapify(open_nodes)

    return None
#
#
# def find_paths(board):
#     """ Finds paths for white stacks to destroy all black tokens."""
#     goal_states = generate_goal_states(board)
#
#     poss_paths = dict()
#     for white_stack, goal in itertools.product(board.white, goal_states):
#
#         expander = lambda p: (e[0] for e in board.possible_moves(p, board.height_at(white_stack)))
#
#         path_to_goal = a_star(white_stack, goal, l1_norm_cost, expander, set.__contains__)
#
#         if path_to_goal is not None:
#             poss_paths[(white_stack, path_to_goal[-1])] = path_to_goal
#
#     paths = dict()
#     while goal_states and poss_paths:
#
#         print("\nGoals remaining:")
#         for g in goal_states:
#             print(g)
#
#         white_stack, goal = min(poss_paths, key=lambda k: len(poss_paths.get(k)))
#
#         for i, goal_set in enumerate(goal_states):
#             if goal in goal_set:
#                 break
#
#         achieved_goal = goal_states[i]
#         goal_states = goal_states[:i] + goal_states[i + 1:]
#
#         print(f"sending {white_stack} to {goal}")
#         paths[white_stack] = poss_paths[(white_stack, goal)]
#
#         for ws, g in list(poss_paths.keys()):
#             if ws == white_stack or g in achieved_goal:
#                 del poss_paths[(ws, g)]
#
#         break
#
#     if goal_states:
#         print(f"\nWARNING: {len(goal_states)} goal(s) not achieved.")
#     return paths


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
    return min(sum(abs(x - y)) for x, y in zip(p, g) for g in goals)


# def stack_l1_norm_cost(p, h, goals):
#     return min(sum(ceil(abs(x - y) / h) for x, y in zip(p, g)) for g in goals)
#
#
# def estimate_cost(white_stacks, goal_sets):
#     cost_estimate = 0
#     for g in goal_sets:
#         cost_estimate += min(stack_l1_norm_cost(s, h, g) for s, h in white_stacks.values())
#     return cost_estimate


def all_goals_reached(state):
    for g in state.goals:
        if not any(pos in g for pos in state.white):
            return False
    return True


# TODO: rename function
def whole_board_search(board):
    goals = generate_goal_states(board)
    start = State.create_from_dict(board.white, board.black, goals)

    print(f"goals: {goals}")

    cost_heuristic = State.estimate_cost
    expander = board.generate_states
    goal_reached = all_goals_reached

    return a_star(start, goals, cost_heuristic, expander, goal_reached)


if __name__ == "__main__":
    pass