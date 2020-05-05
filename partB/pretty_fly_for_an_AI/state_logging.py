import numpy as np
import itertools

class StateLogger():

    def __init__(self):
        self.counter = itertools.count()
        self.counter2 = itertools.count()

    def add(self, state):

        outfile = "./pretty_fly_for_an_AI/ml_logging/" + str(next(self.counter)) +".npy"
        np.save(outfile, state)

    # A new counter was needed
    def record_prev(self, states):
        outfile = "./pretty_fly_for_an_AI/prevs/" + str(next(self.counter2)) + ".npy"
        np.save(outfile, states)

