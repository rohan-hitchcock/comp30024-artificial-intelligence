import numpy as np

class StateLogger():

    def __init__(self):
        self.states = []

    def add(self, state):
        self.states.append(state.board)

    def save(self, path):
        np.save(path, np.array(self.states))





