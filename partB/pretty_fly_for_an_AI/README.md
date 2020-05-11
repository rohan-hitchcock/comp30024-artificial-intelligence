# COMP30024 Artificial Intelligence PART B
## Explodibots Game Playing AI
##### Rohan Hitchcock (836598) and Patrick Randell (836026)

### Main Player
Our final player to be used for submission is simply the "Player" class found in "player.py". In that same file is
a similar variant "LearnerPlayer" which was used to train the final version. At the top, the weights are assigned to 
their respective classes.

### Other Players
In the "old_players.py" file are 3 players, a RandomPlayer, PlayerModerate, and PVSPlayer. These players were used to train 
our final player, or in the case of PVSPlayer, used as an experiment to determine its effective compared to our final strategy.

### Game Representation
In "state.py" are all the methods and objects used to represent the game, generate moves and modify the objects maintained throughout
a playthrough. Included are 2 expansion strategies used at different points in a game.

### Searching
"minimax.py" contains the various different implementations of the minimax algorithm with alpha-beta pruning adjusted for the different
Players we have created.

### Evaluation
The evaluation function used by our final player and learner are found in "evaluation.py". The main evaluation function is adjusted 
such that it could be updated by the TDLeaf machine learning algorithm.

### Machine Learning Algorithm
"tdleaf.py" contains our implementation of the TD-LEAF(Lambda) algorithm, used to train our Player and update its feature weights.
"learning_runner.py" is the module used to run the learner and update its weights.

