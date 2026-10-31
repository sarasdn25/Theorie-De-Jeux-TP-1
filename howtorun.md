# How to run

`python code.py`

Starts the interactive menu: choose the game (keyboard, JSON file, random, or TP examples 1 to 5), then strict or weak dominance. In the examples option, the list of the 5 examples is shown and you pick one.

`python code.py --example 3`

Runs the chosen TP example directly (1 to 5), then asks for the mode.

`python code.py --example 3 --mode weak --order 2 1`

Runs Example 3 in weak mode with Player 2 examined first, with no questions asked. `--mode` accepts `strict` or `weak`.

`python code.py --test`
Runs the automatic tests on the TP examples and prints `[OK]` or `[ECHEC]` for each.

`python code.py game.json`
Loads a game from a JSON file, then asks for the mode.

If `python` does not work, use `python3`.