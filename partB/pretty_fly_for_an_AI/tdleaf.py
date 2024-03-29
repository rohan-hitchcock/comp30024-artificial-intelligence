import numpy as np

def tdleaf_update(weights, pred_states, reward, dpartial_reward, temporal_discount, learning_rate):
    """ Updates a weight vector according to the TD-Leaf(lambda) algorithm.
    
        Args:
            weights: an array of weights to update
            pred_states: an array of states. The state pred_states[i] is the 
            best state predicted by minimax on turn i of a game.
            reward: a callable reward(s, w) where w is a weight vector and s 
            is a state.
            dpartial_reward: a callable dpartial_reward(s, w, i) which returns 
            the value of the partial derivative of reward(s, w) w.r.t the ith 
            coordinate of w.
            temporal_discount: a value in [0, 1] which determines how relavent
            past moves are to the current result (->1 =more relevent). This is
            the parameter lambda
            learning_rate: parameterises the step size of weights.
            
        Returns:
            An updated weight vector as a numpy array.        
    """

    # Has to zip new prev states too
    tds = np.array(
        [reward(s1, weights) - reward(s0, weights)
        for s0, s1 in zip(pred_states, pred_states[1:])

    ])

    discounted_tds = np.array(
        [sum(tds[m] * temporal_discount ** (m - i) for m in range(i, len(tds)))
        for i in range(len(tds))    
    ])

    # Same here
    derivs = np.array([
        [dpartial_reward(s, weights, i) for s in pred_states[:-1]]
        for i in range(len(weights))
    ])

    return weights + learning_rate * np.dot(derivs, discounted_tds)

if __name__ == "__main__":  
    pass
