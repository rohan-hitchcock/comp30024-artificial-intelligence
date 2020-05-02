import argparse
import subprocess
import numpy as np
from tdleaf import tdleaf_update 
from evaluation import reward, dpartial_reward
import os

parser = argparse.ArgumentParser(description="For training a player.")

parser.add_argument("num_iterations", type=int, help="The number of iterations to run the program for.")
parser.add_argument("opponent", type=str, help="The name of the opponent player.")

temp_discount = 0.7
learning_rate = 0.7

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

    state_files = os.listdir("./pretty_fly_for_an_AI/ml_logging")
    pred_states = np.empty((len(state_files), 64), dtype=np.int8)
    for i, state_file in enumerate(sorted(state_files)):
        pred_states[i] = np.load(state_file)

    pred_states = pred_states

    new_weights = tdleaf_update(weights, pred_states, reward, dpartial_reward, temp_discount, learning_rate)

    #delete all files in the logging folder
    os.system("rm ./pretty_fly_for_an_AI/ml_logging/*")
    
    as_white = not as_white



