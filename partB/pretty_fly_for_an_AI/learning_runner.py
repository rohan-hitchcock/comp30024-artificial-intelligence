import argparse
import subprocess
import numpy as np
from tdleaf import tdleaf_update 
from evaluation import reward, dpartial_reward
import os

def load_states_to_numpy(dirpth):
    state_files = os.listdir(dirpth)
    pred_states = np.empty((len(state_files), 64), dtype=np.int8)
    for i, state_file in enumerate(sorted(state_files, key=lambda s : int(s.split(".")[0]))):
        pred_states[i] = np.load(os.path.join(dirpth, state_file))
    return pred_states


TEMP_DISCOUNT = 0.7
LEARNING_RATE = 0.07

parser = argparse.ArgumentParser(description="For training a player.")

parser.add_argument("num_iterations", type=int, help="The number of iterations to run the program for.")
parser.add_argument("opponent", type=str, help="The name of the opponent player.")
parser.add_argument("--verbose", "-v", action="store_true", help="Show additonal output.")
parser.add_argument("--temp_discount", "-t", type=float, default=TEMP_DISCOUNT, help="The temporal discount in TD-Leaf  (the value of lambda)")
parser.add_argument("--learning_rate", "-l", type=float, default=LEARNING_RATE, help="The learning rate of TD-Leaf")

args = parser.parse_args()

as_white = True

if args.verbose:
    stdouterr = None
else:
    stdouterr = subprocess.PIPE


for i in range(args.num_iterations):

    if args.verbose:
        color_str = "white" if as_white else "black"
        print(f"Playing as: {color_str}")

    if as_white:
        to_run = ["python3", "-m", "referee", "-v0",
                  "pretty_fly_for_an_AI:LearnerPlayer", 
                  "pretty_fly_for_an_AI:" + args.opponent]
    else:
        to_run = ["python3", "-m", "referee", "-v0",
                  "pretty_fly_for_an_AI:" + args.opponent, 
                  "pretty_fly_for_an_AI:LearnerPlayer"]
    
    
    subprocess.run(to_run, stderr=stdouterr, stdout=stdouterr)

    weights = np.load("./pretty_fly_for_an_AI/weights.npy")
    pred_states = load_states_to_numpy("./pretty_fly_for_an_AI/ml_logging")

    new_weights = tdleaf_update(weights, pred_states, reward, dpartial_reward, args.temp_discount, args.learning_rate)

    np.save("./pretty_fly_for_an_AI/weights.npy", new_weights)

    if args.verbose:
        print(f"Updated weights: {new_weights}")


    #delete all files in the logging folder
    os.system("rm ./pretty_fly_for_an_AI/ml_logging/*")
    
    as_white = not as_white
    print(f"({i + 1}/{args.num_iterations}) complete.")
    if args.verbose:
        print()


