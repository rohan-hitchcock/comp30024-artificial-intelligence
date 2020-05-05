import argparse
import subprocess
import numpy as np
from tdleaf import tdleaf_update
from evaluation import reward, dpartial_reward
import os


def load_states_to_numpy(dirpth):
    state_files = os.listdir(dirpth)
    pred_states = np.empty((len(state_files), 64), dtype=np.int8)
    for i, state_file in enumerate(sorted(state_files, key=lambda s: int(s.split(".")[0]))):
        pred_states[i] = np.load(os.path.join(dirpth, state_file))
    return pred_states

def load_states_to_numpy_2(dirpth):
    state_files = os.listdir(dirpth)
    pred_states = []
    for i, state_file in enumerate(sorted(state_files, key=lambda s: int(s.split(".")[0]))):
        pred_states.append(np.load(os.path.join(dirpth, state_file)))
    return pred_states


TEMP_DISCOUNT = 0.7
LEARNING_RATE = 0.09

parser = argparse.ArgumentParser(description="For training a player.")

parser.add_argument("num_iterations", type=int, help="The number of iterations to run the program for.")
parser.add_argument("opponent", type=str, help="The name of the opponent player.")
parser.add_argument("--verbose", "-v", action="store_true", help="Show additonal output.")
parser.add_argument("--temp_discount", "-t", type=float, default=TEMP_DISCOUNT,
                    help="The temporal discount in TD-Leaf  (the value of lambda)")
parser.add_argument("--learning_rate", "-l", type=float, default=LEARNING_RATE, help="The learning rate of TD-Leaf")

args = parser.parse_args()

as_white = True

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

    subprocess.run(to_run)

    #new verbose stuff. alernatives that are a bit nicer use subprocess.catch_output or something rather than run
    # if result.stdout.decode('utf-8').__contains__('draw detected: game state occurred 4 times.'):
        #do something

    # if args.verbose:
    #     print(result.stdout.decode('utf-8'))
    #     print(result.stderr.decode('utf-8'))

    weights = np.load("./pretty_fly_for_an_AI/weights.npy")
    pred_states = load_states_to_numpy("./pretty_fly_for_an_AI/ml_logging")
    prev_states = load_states_to_numpy_2("./pretty_fly_for_an_AI/prevs")

    new_weights = tdleaf_update(weights, pred_states, reward, dpartial_reward, args.temp_discount, args.learning_rate, prev_states)

    np.save("./pretty_fly_for_an_AI/weights.npy", new_weights)

    if args.verbose:
        print(f"Updated weights: {new_weights}")

    # delete all files in the logging folder
    if (i + 1) != args.num_iterations:
        os.system("rm ./pretty_fly_for_an_AI/ml_logging/*")
        os.system("rm ./pretty_fly_for_an_AI/prevs/*")

    as_white = not as_white
    print(f"({i + 1}/{args.num_iterations}) complete.")
    if args.verbose:
        print()
