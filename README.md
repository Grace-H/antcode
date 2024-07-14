# Anthill Resouce Collection Game
Players code the behavior of ants that compete in teams bring food back to their anthill.

## Introduction
Premise: Each team has 1-4 ants, which are placed on a grid. At the end of 200 rounds, whichever team has dropped the most food at their anthill wins. Ants have the ability to move, get food, drop food, and pass messages to their teammates.

### The Map
The map is randomly generated each round,
with between 20 and 24 rows and columns.
It's printed to the console using the following symbols:

| Symbol         | Meaning       |
| :------------- | :------------- |
| #              | Wall           |
| 1-9            | Food pile      |
| .              | Empty          |
| A-D, @         | North team ants & anthill |
| E-H, X         | South team ants & anthill |

### Ant Commands
Ants have four moves they can make on their turn:
1. PASS: Do nothing.
2. [direction]: Issue one of the cardinal directions (see below) to attempt moving in that direction. The top of the map is north.
3. DROP [direction]: If carrying food, it will be dropped at the coordinates in the direction given.
4. GET [direction]: If there is food in the direction given, pick up the food. Ants can carry one food at a time.

All ants move simutaneously. If the actions of two or more ants conflict (possible with moving or GET), these ants' actions won't be executed. Raising an exception, taking too long, or returning an invalid command will result in your ant being eliminated. The game will print a hint of what went wrong.

The supported cardinal directions are as follows:
|                |                 |                |
| :-------------: | :-------------: | :-------------: |
| NORTHWEST       | NORTH           | NORTHEAST       |
| WEST            | HERE            | EAST            |
| SOUTHWEST       | SOUTH           | SOUTHEAST       |

## Creating Ants
### Setup
Each ant's movement is controlled by a subclass of `AntStrategy`,
which is defined in `AntStrategy.py`.
In a new file, create a subclass and finish the methods.
All of your work will be in this new subclass alone, which is what you'll share with your teammates and turn in (you shouldn't need to change anything in `AntStrategy.py`).
`StarterStrat.py` is provided as a starter file that you can copy and work from.
Several `AntStrategy` implementations, varying from terrible to decent, are provided for inspiration and to help you understand how the game works.

### `AntStrategy` Details
Each `AntStrategy` has three methods for you to complete, which will be called in the following order each round by the main game:
1. `receiveInfo()`: The game will pass a list of messages sent by your teammates in the last round. Parse & handle these messages. What messages are sent and their format is up to your team!
2. `oneStep()`: Using the state information about your ant passed in as arguments, decide and return the next move for your ant.
3. `sendInfo()`: Return any messages you want to send this round.

This class is fully documented, so see `AntStrategy.py` for more details about these methods and how the game interacts with the class.

## Running the Simulation
First, add an import to the list of `AntStrategy` subclass imports in `main.py` to import your class.
Then, find the two tuples called `team1` and `team2`.
Change the contents of these so that they're the names of the 1-4 AntStrategy classes you want on each team.
If using CodeHS, click Run! If using something else, execute `main.py` (on the commandline: `$ python3 main.py`).

### Saving and Loading a Map from a File
To test your ants under the same conditions
(map and/or random seed),
you can save and load the game state from a file.
At the end of a game,
you will be asked if you would like to save the map and random seed to a file and prompted for a filename if so.
To load either the map or seed at the beginning of a game,
answer "yes" when prompted.
Always enter *relative* paths to the files you are saving from or loading
(if it's in the same folder as `main.py`, it's just the name of the file).

### Debugging Mode
By default, only short error messages are printed out when an exception occurs in an AntStrategy.
To see the full traceback,
set the `DEBUG` variable in `main.py` to `True`.
This will show you the type of exception, the sequence of function calls, and the exact line in your AntStrategy that caused the error.
