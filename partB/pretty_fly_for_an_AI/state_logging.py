import numpy as np
import itertools

class StateLogger():

    def __init__(self):
        self.counter = itertools.count()

    def add(self, state):

        outfile = "./pretty_fly_for_an_AI/ml_logging/" + str(next(self.counter)) +".npy"
        np.save(outfile, state)

