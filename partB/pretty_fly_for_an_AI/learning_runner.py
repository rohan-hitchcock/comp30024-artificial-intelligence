import argparse
import subprocess
import numpy as np
from tdleaf import tdleaf_update


parser = argparse.ArgumentParser(description="For training a player.")

parser.add_argument("num_iterations", type=int, help="The number of iterations to run the program for.")
parser.add_argument("opponent", type=str, help="The name of the opponent player.")

args = parser.parse_args()
as_white = True
for _ in range(args.num_iterations):

    if as_white:
        to_run = ["python3", "-m", "referee", "-v0",
                  "pretty_fly_for_an_AI:LearnerPlayer", 
                  "pretty_fly_for_an_AI:" + args.opponent]
    else:
        to_run = ["python3", "-m", "referee", "-v0",
                  "pretty_fly_for_an_AI:" + args.opponent, 
                  "pretty_fly_for_an_AI:LearnerPlayer"]
    
    
    subprocess.run(to_run)

    weights = np.load("./pretty_fly_for_an_AI/weights.npy")
    pred_states = np.load("./pretty_fly_for_an_AI/pred_states.npy")

    new_weights = tdleaf_update(weights, pred_states, ...)

    
    as_white = not as_white



