# Antcode Resouce Collection Game
Players code the behavior of ants that compete in teams to bring food back to their anthill.

## Introduction
Each team has 1-4 ants, which are placed on a grid. At the end of 200 rounds, whichever team has dropped the most food at their anthill wins. Ants have the ability to move, get food, drop food, and pass messages to their teammates.

### The Map
The map is randomly generated each round with 20-24 rows and columns.
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
1. `receive_info(messages)`: The game will pass a list of messages sent by your teammates in the last round. Parse & handle these messages. What messages are sent and their format is up to your team!
2. `one_step()`: Using the state information about your ant passed in as arguments, decide on and return the next move for your ant.
3. `send_info()`: Return any messages you want to send this round.

This class is fully documented, so see `AntStrategy.py` for more details about these methods and how the game interacts with the class.

## Running the Simulation
First, add an import to the list of `AntStrategy` subclass imports in `main.py` to import your class.
Then, find the two tuples called `team1` and `team2`.
Change the contents of these so that they're the names of the 1-5 AntStrategy classes you want on each team.
If using CodeHS, click Run! If using something else, execute `main.py` (on the commandline: `$ python3 main.py`).

### Saving and Loading a Map from a File
To test your ants under the same conditions,
you can save and load the game state from a file.
At the end of a game,
you will be asked if you would like to save the map to a file and prompted for a filename if so.
To load the map at the beginning of a game,
answer "yes" when prompted.
Always enter *relative* paths to the files you are saving from or loading
(if it's in the same folder as `main.py`, it's just the name of the file).

## Additional Information
### Ant Vision
One of the pieces of state information passed to the `one_step()` method is the ant's `vision`.
This is a 3x3 list representing the locations in the map immediately under and around the ant with the ant at the center (`vision[1][1]`).
Each index will have one of symbols in the key above, indicating what is around the ant in the map.
(0,0) is northwest of the ant.
Ants can "see" one unit in all directions.

### Message Passing
Each round, your ant will have the ability to receive messages sent by your team in the prior round and send messages.
Your team will need to decide what information you want to communicate and how to format your messages.
Suppose your team wants to share whether they're carrying food at the end of each round.
You might choose the message format `"ANT1 FOOD " + str(food)`.
`GridBuilderStrat` and `ScoutStrat` send messages about what they've discovered on the map in the format `str(x) + " " + str(y) + " " + item`.
Each of these examples is a string, but the messages don't have to be strings.
`SmarterRandomStrat` isn't very creative and just sends the word `"message"` to its teammates.
If you try to run GridBuilderStrat and SmarterRandomStrat together, you will see an error because they try to parse each others' messages incorrectly!

At the beginning of each round, the game will call `receive_info` on your ant. It will pass a `list` of messages from your teammates.
Parse each message according to the your team's format and update your ant's state if needed.
For example, `GridBuilderStrat` uses the messages to fill in its internal map of the playing field and even has some basic checks to avoid causing an exception if a message is the wrong format.
```python3
def receive_info(self, messages):
    for m in messages:
        words = m.split()
        if len(words) != 3:
            print("Message incorrectly formatted: " + m);
            continue
        x, y, agent = words
        self.grid[int(x)][int(y)] = agent
```

Then, the game will call the `one_step` method.
Do not call `send_info` yourself from `one_step`; it's called by the game after `one_step`.
Since you may want to share information learned during `one_step` with your teammates, one solution is to create an instance variable for outgoing messages, e.g. `self.outbox = []`.

In `send_info`, your ant can return a `list` of messages.
Here's an example where an ant shares if it's carrying food. Note that this method still returns a list even though there's only one message.
```python3
def send_info(self):
    '''Send whether or not I'm carrying food'''
    return ["ANT1 FOOD " + str(self.food)]
```

`GridBuilderStrat` returns the contents of its outbox and resets it to an empty list.
```python3
def send_info(self):
    '''Send and clear outbox list of messages from this round'''
    to_return = self.outbox
    self.outbox = []
    return to_return
```

### Debugging Mode
By default, only short error messages are printed out when an exception occurs in an AntStrategy.
To see the full traceback,
set the `DEBUG` variable in `main.py` to `True`.
This will show you the type of exception, the sequence of function calls, and the exact line in your AntStrategy that caused the error.

### Ties
If both teams of ants finish with the same total food dropped on each anthill, the winner is the team that held the lead in more rounds. For instance, if the North team has more food dropped on the anthill for 100 rounds, and the South team has more food dropped on the anthill for 40 rounds, the North team wins the match.

If both teams lead for the same number of rounds, the game is a true tie.