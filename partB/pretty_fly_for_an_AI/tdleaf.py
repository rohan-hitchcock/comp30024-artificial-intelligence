import numpy as np
import os

def tdleaf_update(weights, pred_states, reward, dpartial_reward, temporal_discount, learning_rate, prev_states):
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

    tds = np.array(
        [reward(s1, weights, p1) - reward(s0, weights, p0)
        for s0, s1, p0, p1 in zip(pred_states, pred_states[1:], prev_states, prev_states[1:])

    ])

    discounted_tds = np.array(
        [sum(tds[m] * temporal_discount ** (m - i) for m in range(i, len(tds)))
        for i in range(len(tds))    
    ])

    derivs = np.array([
        [dpartial_reward(s, weights, i, p) for s, p in zip(pred_states[:-1], prev_states[:-1])]
        for i in range(len(weights))
    ])

    return weights + learning_rate * np.dot(derivs, discounted_tds)

def tdleaf_update_simple(weights, pred_states, reward, dpartial_reward, temporal_discount, learning_rate):
    """ Same as tdleaf_update but written in a more readable way"""


    tds = np.array(
        [reward(s1, weights) - reward(s0, weights) 
        for s0, s1 in zip(pred_states, pred_states[1:])
    ])

    new_weights = weights.copy()

    for j in range(len(new_weights)):

        adjust = 0

        for i in range(len(pred_states) - 1):
            

            temp_diff = 0
            for m in range(i, len(tds)):
                temp_diff += tds[m] * temporal_discount ** (m - i)

            adjust += temp_diff * dpartial_reward(pred_states[i], weights, j)
        
        new_weights[j] += learning_rate * adjust

    return new_weights

def load_states_to_numpy(dirpth):


    state_files = os.listdir(dirpth)
    pred_states = np.empty((len(state_files), 64), dtype=np.int8)
    for i, state_file in enumerate(sorted(state_files, key=lambda s : int(s.split(".")[0]))):
        pred_states[i] = np.load(os.path.join(dirpth, state_file))


    return pred_states

if __name__ == "__main__":  
    import state as st
    from evaluation import reward, dpartial_reward

    EPS = 1e-11

    temp_dis = 0.7
    learn_r = 0.7

    iters = 100

    weights = np.load("./weights.npy")

    pred_states = load_states_to_numpy("./ml_logging/")

    
    new_weights_simple = tdleaf_update_simple(weights, pred_states, reward, dpartial_reward, temp_dis, learn_r)
    
    new_weights = tdleaf_update(weights, pred_states, reward, dpartial_reward, temp_dis, learn_r)
    
    print(np.allclose(new_weights_simple, new_weights))

    print(new_weights)
    print(new_weights_simple)

