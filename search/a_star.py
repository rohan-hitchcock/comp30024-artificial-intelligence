import heapq
from collections import defaultdict as dd


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


def expand_free(node):
    """ Expands a node to all four of its north, south, east, west neighbors.

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


def a_star(start, goals, cost_to_goal, expand_node):
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
    priority = {start: cost_to_goal(start, goals)}

    PriorityNode.__lt__ = lambda x, y: priority[x.node] < priority[y.node]

    while open_nodes:
        curr_node = heapq.heappop(open_nodes).node

        if curr_node in goals:
            return path_to(curr_node, prev_node)

        heap_changed = False
        for neighbor in expand_node(curr_node):

            if cost[neighbor] > cost[curr_node] + 1:

                if cost[neighbor] == float("inf"):
                    open_nodes.append(PriorityNode(neighbor))

                cost[neighbor] = 1 + cost[curr_node]
                priority[neighbor] = cost[neighbor] + cost_to_goal(neighbor, goals)
                prev_node[neighbor] = curr_node

                heap_changed = True

        if heap_changed:
            heapq.heapify(open_nodes)

    return None


if __name__ == "__main__":

    goals = {(1, 10), (11, 3)}

    start = (0, 0)

    for n in a_star(start, goals, l1_norm_cost, expand_free):
        print(n)
