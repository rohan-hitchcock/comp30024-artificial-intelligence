from collections import defaultdict as dd

def get_labeled_print(components):
    """ Accepts a finite iterable of iterables of valid board positions. 
        Returns a dictionary suitible for printing where each position is labeled
        by the index of the iterable containing it in components"""

    print_dict = dd(str)
    for component_id, component in enumerate(components):
        for pos in component:
            if str(component_id) not in print_dict[pos]:
                print_dict[pos] += str(component_id)
    return print_dict
