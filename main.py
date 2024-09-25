# Ant Resource Collection Game
#
# To make ants and run game:
# 1. Create a subclass of AntStrategy that will direct an ant's actions during 
#    the game: Copy StarterStrat.py, rename it, and finish the methods.
# 2. Import your AntStrategy subclass below (see comment A)
# 3. Put your ants on a teams by adding them to the appropriate tuples (B)
# 4. Run this file. Ants will have 200 moves to try to score the most points
#    by dropping food at their team's anthill

from concurrent.futures import wait, ProcessPoolExecutor, ThreadPoolExecutor, TimeoutError
import os
import random
import time
import traceback

# A. Import student strategies here
from HorizontalStrat import HorizontalStrat
from VerticalStrat import VerticalStrat
from RandomStrat import RandomStrat
from SmarterRandomStrat import SmarterRandomStrat
from StraightHomeStrat import StraightHomeStrat
from GridBuilderStrat import GridBuilderStrat
from ScoutStrat import ScoutStrat
from StarterStrat import StarterStrat
    
# B. Register strategy class names in team1/team2 tuples below, 1-4 ants per team
team1 = (StraightHomeStrat, StraightHomeStrat, StraightHomeStrat, StraightHomeStrat)
team2 = (GridBuilderStrat,  GridBuilderStrat, GridBuilderStrat, GridBuilderStrat)
DEBUG = False # Change this to True to get more detailed errors from ant strategies

# --- Begin Game ---

# Configuration variables for randomly generated maps
numObstacles = 10 # Number of obstacles
amountFood = random.randrange(20, 25) # Number of food piles

# Matrix constants
EMPTY = '.'
WALL = '#'
NORTH_HILL = '@'
SOUTH_HILL = 'X'

class Cell:
    '''Cell in the game matrix.

    Attributes:
        wall: boolean, whether this is a wall
        anthill: str | None, anthill if this cell has an anthill
        food: int, number of food in this cell
        ant: Ant | None, ant in this cell
    '''
    def __init__(self, wall=False, anthill=None, food=0):
        self.wall = wall
        self.anthill = anthill
        self.food = food
        self.ant = None

    def is_empty(self):
        '''Has absolutely nothing in it'''
        return not self.wall and not self.anthill and not self.ant and self.food == 0

    def print_cell(self):
        if self.ant:
            return self.ant.get_symbol()
        elif self.anthill:
            return self.anthill
        elif self.food > 0:
            return str(self.food)
        elif self.wall:
            return WALL
        else:
            return EMPTY

    def __repr__(self):
        return self.print_cell()

class Ant:
    def __init__(self, strategy, x, y, team, symbol):
        self.strategy = strategy
        self.x = x
        self.y = y
        self.team = team
        self.symbol = symbol
        self.food = False
        self.alive = True
    
    def die(self):
        self.alive = False

    def act(self, vision):
        return self.strategy.oneStep(self.x, self.y, vision, self.food)
    
    def send(self, messages):
        self.strategy.receiveInfo(messages)
    
    def recv(self):
        return self.strategy.sendInfo()

    def get_symbol(self):
        return self.symbol if not self.food else self.symbol.lower()

    def __repr__(self):
        return a.symbol

def isOpenCell(matrix, x, y):
    """Check if a cell in matrix is in bounds and not a wall."""
    return x > 0 and x < len(matrix) and y > 0 and y < len(matrix[0]) and not matrix[x][y].wall
    
def initializeAnts(team1Strats, team1Locs, team2Strats, team2Locs, rows, cols):
    """Instantiate ant classes for each team.
    
    Populate ants list and dictionary of Ant->matrixSymbol mappings. Takes two 
    lists for each team: AntStrategy class names and inital (x, y) positions
    """
    # Team 1
    for Strat, sym in zip(team1Strats, ["A", "B", "C", "D"]):
        try:
            antStrat = Strat(rows, cols, NORTH_HILL)
        except Exception as e:
            print("Ant initialization failed for Team 1 AntStrategy: " + str(Strat))
            if DEBUG:
                print(traceback.format_exc())
            continue
        ants.append(Ant(antStrat, team1Locs[sym][0], team1Locs[sym][1], 0, sym))

    # Team 2
    for Strat, sym in zip(team2Strats, ["E", "F", "G", "H"]):
        try:
            antStrat = Strat(rows, cols, SOUTH_HILL)
        except Exception as e:
            print("Ant initialization failed for Team 2 AntStrategy: " + str(Strat))
            if DEBUG:
                print(traceback.format_exc())
            continue
        ants.append(Ant(antStrat, team2Locs[sym][0], team2Locs[sym][1], 1, sym))

def generateGameConfig():
    """Prompt user for game configuration options, including saved map file

    Returns: dict[str, boolean or str], with the following keys:
        'fast_forward': boolean, continue to end without stopping
        'load_map': boolean, use saved map
        'save_file': str, filename if load_map is True
    """
    config = {
            'fast_forward': False,
            'load_map': False,
            'save_file': None,
    }

    fast_forward = input("Run to the end without pausing? (yes/<enter>) ")
    if fast_forward.upper() == "YES":
        config['fast_forward'] = True

    load_map = input("Use saved map? (yes/<enter>) ")
    if load_map.upper() == "YES":
        config['load_map'] = True

    if config['load_map']:
        filepath = input("Enter path to save file: ")
        if os.path.exists(filepath):
           config['save_file'] = filepath
        else:
            print("File not found, using new map: " + filepath)
            config['load_map'] = False

    return config

def loadSaveFile(filename):
    """Load saved game data from a file.

    Trusts that map is valid format, with walls, 8 ants, and 2 anthills.

    Returns:
        Dict[str, int or str] of game data with following keys:
            'map': List[str], game matrix
            'team1Starting': (int, int) x,y tuple representing starting positions
            'team2Starting': (int, int) "

    Raises: ValueError if file is incorrect format
    """
    with open(filename, 'r') as file:
        lines = file.readlines()

    file_data = {}
    try:
        file_data['map'] = []
        file_data['team1Starting'] = {}
        file_data['team2Starting'] = {}
        for y, string in enumerate(lines):
            line = []
            for x, c in enumerate(string.strip()):
                if c in "ABCD":
                    file_data['team1Starting'][c] = (x, y)
                elif c in "EFGH":
                    file_data['team2Starting'][c] = (x, y)
                line.append(c)
            file_data['map'].append(line)
    except:
        raise ValueError("Error loading save file: incorrect format")

    return file_data

def placeObstacles(matrix, numObstacles):
    """Place several vertical and horizontal barriers randomly in matrix."""
    rows = len(matrix[0])
    cols = len(matrix)
    while numObstacles > 0: # place obstacles (including mirror image)
        pickX = random.randrange(2, (cols - 3)) # don't place on left or right sides
        pickY = random.randrange(3, (rows - 4)) # don't place in top two or bottom two rows
        if matrix[pickX][pickY].is_empty():
            direction = random.randrange(0, 1) # 0 is horizontal, 1 is vertical
            numberOfSquare = random.randrange(1, 5) # length of obstacle
            if direction == 0: # horizontal obstacle
                for x in range(numberOfSquare):
                    if pickX < cols/2: # left half of screen
                        matrix[pickX+x][pickY].wall = True
                        matrix[cols-pickX-1-x][rows-pickY-1].wall = True
                    else: # right half of screen
                        matrix[pickX-x][pickY].wall = True
                        matrix[cols-pickX-1+x][rows-pickY-1].wall = True
            else: # direction == 1, vertical obstacle
                for y in range(numberOfSquare):
                    if pickY < rows/2: # top half of screen
                        matrix[pickX][pickY+y].wall = True
                        matrix[cols-pickX-1][rows-pickY-1-y].wall = True
                    else: # bottom half of screen
                        matrix[pickX][pickY-y].wall = True
                        matrix[cols-pickX-1][rows-pickY-1+y].wall = True
            numObstacles -= 1

def placeFood(matrix, amountFood):
    """Place ints representing food piles randomly in matrix."""
    rows = len(matrix[0])
    cols = len(matrix)
    while amountFood > 0: # place food (including mirror image)
        pickX = random.randrange(1, cols - 1)
        pickY = random.randrange(2, rows - 3) # Don't place in top or bottom row
        if matrix[pickX][pickY].is_empty():
            pile = random.randrange(1,9)
            matrix[pickX][pickY].food = pile
            matrix[cols-pickX-1][rows-pickY-1].food = pile
            amountFood -= 1
            
def placeAnts(matrix, ants):
    """Put corresponding number for each live ant at x,y location in matrix."""
    for a in ants:
        if a.alive:
            matrix[a.x][a.y].ant = a
        
def initializeMatrixFromSaved(loaded_map):
    new_matrix = [[Cell() for col in loaded_map] for row in loaded_map[0]]
    for x, col in enumerate(loaded_map):
        for y, cell in enumerate(col):
            if cell == "#":
                new_matrix[y][x].wall = True
            elif cell.isdigit():
                new_matrix[y][x].food = int(cell)
            elif cell == "@":
                new_matrix[y][x].anthill = NORTH_HILL
            elif cell == "X":
                new_matrix[y][x].anthill = SOUTH_HILL
    return new_matrix
    
def initializeMatrixRandom():
    rows = random.randrange(20,25) # Number of rows
    cols = random.randrange(20,25) # Number of columns
    northHill = (int((cols-1)/2), 1) # Location of north hill
    southHill = (cols-(int((cols-1)/2))-1, rows-2) # Location of south hill

    matrix = [[Cell() for i in range(rows)] for j in range(cols)]

    # Surround with walls
    for i in range(rows):
        matrix[0][i].wall = True
        matrix[cols-1][i].wall = True
    for i in range(cols):
        matrix[i][0].wall = True
        matrix[i][rows-1].wall = True

    # Place hills, obstacles, food
    matrix[northHill[0]][northHill[1]].anthill = NORTH_HILL
    matrix[southHill[0]][southHill[1]].anthill = SOUTH_HILL
    placeObstacles(matrix, numObstacles)
    placeFood(matrix, amountFood)

    return matrix

def constructMap(config):
    """Construct matrix and initialize ants"""
    if config['load_map']:
        try:
            file_data = loadSaveFile(config['save_file'])
        except ValueError as e:
            print(e)
            if DEBUG:
                print(traceback.format_exc())
            print("Randomly generating new map")
            config['load_map'] = False
            return initializeMatrix(amountFood, numObstacles, ants, config)

        loaded_map = file_data['map']
        matrix = initializeMatrixFromSaved(loaded_map)
        team1Starting = file_data['team1Starting']
        team2Starting = file_data['team2Starting']
    else:
        matrix = initializeMatrixRandom()
        cols = len(matrix)
        rows = len(matrix[0])
        team1Starting = {'A': (3,1), 'B': (6,1), 'C': (cols-7,1), 'D': (cols-4,1)}
        team2Starting = {'E': (3,rows-2), 'F': (6,rows-2), 'G': (cols-7,rows-2), 'H': (cols-4,rows-2)}

    initializeAnts(team1, team1Starting, team2, team2Starting, len(matrix), len(matrix[0]))
    placeAnts(matrix, ants)
    return matrix

def matrixToStrList(matrix):
    out = []
    for row in range(len(matrix[0])):
        output = ""
        for col in range(len(matrix)):
            output += matrix[col][row].print_cell()
        out.append(output)
    return out

def printMap(matrix):
    """Print an ascii rendering of the map.

    If multiple items occupy the same
    cell, only print the last one (prioritizes things that move (ants))
    """
    for line in matrixToStrList(matrix):
        print(line)

def generateVision(matrix, x, y):
    """Return a 3x3 matrix representing the area surrounding x,y in the matrix.
    
    Assumes x & y are inside the outer walls.
    """
    vision = []
    for j in range(x-1, x+2):
        row = []
        for i in range(y-1, y+2):
            row.append(matrix[j][i].print_cell())
        vision.append(row)
    return vision

def killAnt(ant):
    ant.die()
    matrix[ant.x][ant.y].ant = None

# Thread/Process Mains
def getMoveMain(ant, matrix):
    """Thread main for getting ant's next move.
    
    Returns an array of strings representing move. Performs basic input 
    validation by checking move's type and length. May raise ValueError.
    """
    move = ant.act(generateVision(matrix, ant.x, ant.y))
    if type(move) == str:
        split_move = move.split()
        if len(split_move) < 1 or len(split_move) > 2:
            raise ValueError("Move too long or too short. Recieved: " + str(move))
        return split_move
    else:
        raise ValueError("Move should be of type string. Recieved: " + str(move))

def gameLoop(matrix, ants, config):
    """Run game with initialized matrix and ants."""
    team1Points = 0
    team2Points = 0
    team1Messages = []
    team2Messages = []
    
    gameOutput = f"SIZE {len(matrix[0])} {len(matrix)}\n"
    
    pool = ThreadPoolExecutor() # Can impose limits on number of threads
    
    transformXY = { "NORTH": lambda x, y: (x, y-1),
                    "SOUTH": lambda x, y: (x, y+1),
                    "EAST": lambda x, y: (x+1, y),
                    "WEST": lambda x, y: (x-1, y),
                    "NORTHEAST": lambda x, y: (x+1, y-1),
                    "SOUTHEAST": lambda x, y: (x+1, y+1),
                    "SOUTHWEST": lambda x, y: (x-1, y+1),
                    "NORTHWEST": lambda x, y: (x-1, y-1),
                    "HERE": lambda x, y: (x, y) }

    if not config['fast_forward']:
        print("Press enter to execute next round")

    printMap(matrix)
    for lap in range(200):
        if not config['fast_forward']:
            input()

        # Pass messages to ants and clear buffers
        for a in ants:
            try:
                a.send(team1Messages if a.team == 1 else team2Messages)
            except Exception as e:
                print("Error in " + str(a) + " when receiving messages: " + str(e))
                if DEBUG:
                    print(traceback.format_exc())
                killAnt(a)
        team1Messages = []
        team2Messages = []

        # Prompt ants for next move
        moves = {}
        ants[:] = [a for a in ants if a.alive] # Remove the dead ants
        futures = [pool.submit(getMoveMain, a, matrix) for a in ants]
        for a, future in zip(ants, futures):
            try:
                moves[a] = future.result(timeout=0.1)
            except TimeoutError:
                print("Timeout waiting for oneStep in " + str(a))
                killAnt(a)
            except Exception as e:
                print("Error in oneStep in " + str(a) + ": " + str(e))
                if DEBUG:
                    print(traceback.format_exc())
                killAnt(a)

        # Parse moves
        proposedMoves = {}
        proposedGets = {}
        for a, move in moves.items():
            loc = (a.x, a.y)
            
            # Cardinal movement
            if move[0] in transformXY and len(move) == 1:
                newLoc = transformXY[move[0]](loc[0], loc[1])
                if isOpenCell(matrix, newLoc[0], newLoc[1]):
                    loc = newLoc

            elif move[0] == "GET":
                if len(move) != 2 or move[1] not in transformXY:
                    print("Invalid GET in " + a.symbol + ": " + str(move))
                    killAnt(a)
                    continue
                elif not a.food: # Can't carry more than one!
                    targetX, targetY = transformXY[move[1]](a.x, a.y)
                    if isOpenCell(matrix, targetX, targetY):
                        if (targetX, targetY) in proposedGets:
                            proposedGets[(targetX, targetY)].append(a)
                        else:
                            proposedGets[(targetX, targetY)] = [a]

            elif move[0] == "DROP":
                if len(move) != 2 or move[1] not in transformXY:
                    print("Invalid DROP in " + a.symbol + ": " + str(move))
                    killAnt(a)
                    continue
                elif a.food:
                    targetX, targetY = transformXY[move[1]](a.x, a.y)
                    if isOpenCell(matrix, targetX, targetY):
                        a.food = False
                        cell = matrix[targetX][targetY]
                        if cell.anthill:
                            if cell.anthill == NORTH_HILL:
                                team1Points += 1
                            elif cell.anthill == SOUTH_HILL:
                                team2Points += 2

                        else:
                            cell.food += 1

            elif move[0] != "PASS":
                print("Invalid move from " + a.symbol + ": " + str(move))
                killAnt(a)
                continue

            # Attempt to place this ant in next phase of simulation. Ants in conflict must go back
            if loc not in proposedMoves:
                proposedMoves[loc] = a
            else:
                conflictAnt = proposedMoves[loc]

                # Return this ant to original position, resolving any chains of conflicts
                proposedMoves[loc] = None # No one gets to be here
                currentAnt = a
                while currentAnt and (currentAnt.x, currentAnt.y) in proposedMoves and proposedMoves[(currentAnt.x, currentAnt.y)]:
                    nextCurrentAnt = proposedMoves[(currentAnt.x, currentAnt.y)]
                    proposedMoves[(currentAnt.x, currentAnt.y)] = currentAnt
                    currentAnt = nextCurrentAnt
                else:
                    if currentAnt:
                        proposedMoves[(currentAnt.x, currentAnt.y)] = currentAnt

                # Return conflicting ant to original position, resolving conflicts
                while conflictAnt and (conflictAnt.x, conflictAnt.y) in proposedMoves and proposedMoves[(conflictAnt.x, conflictAnt.y)]:
                    nextConflictAnt = proposedMoves[(conflictAnt.x, conflictAnt.y)]
                    proposedMoves[(conflictAnt.x, conflictAnt.y)] = conflictAnt
                    conflictAnt = nextConflictAnt
                else:
                    if conflictAnt:
                        proposedMoves[(conflictAnt.x, conflictAnt.y)] = conflictAnt

        # Resolve proposed gets
        for (targetX, targetY), aList in proposedGets.items():
            if matrix[targetX][targetY].food > 0 and matrix[targetX][targetY].food >= len(aList): #here
                for a in aList:
                    a.food = True
                matrix[targetX][targetY].food -= len(aList)

        # Update arena & redraw screen
        for loc, a in proposedMoves.items():
            if a: # May be none if it was the site of a movement conflict
                matrix[a.x][a.y].ant = None
                a.x = loc[0]
                a.y = loc[1]

        placeAnts(matrix, ants)
        printMap(matrix)
        print("Round:", lap, "Team 1:", str(team1Points), "Team 2:", str(team2Points))
        
        # Add this round to an output list
        gameOutput += (
            f"==============================\n"
            f"ROUND {lap}\n"
            f"NORTH {team1Points}\n"
            f"SOUTH {team2Points}\n"
            f"=============================\n"
            f"{''.join(f'{line}\n' for line in matrixToStrList(matrix))}"
            f"=============================\n"
        )


        # Receive messages from ants from this round
        for a in ants:
            if a.alive:
                try:
                    msgs = a.recv()
                    if type(msgs) != list:
                        raise ValueError("Messages should be of type list.")
                except Exception as e:
                    print("Error in " + a.symbol + " when sending messages: " + str(e))
                    if DEBUG:
                        print(traceback.format_exc())
                    killAnt(a)
                    continue

                if a.team == 1:
                    team1Messages += msgs
                elif a.team == 2:
                    team2Messages += msgs

        ants[:] = [a for a in ants if a.alive] # Remove the dead ants
        
    gameOutput += "==============================\n"

    pool.shutdown()
    print("\n==== Final score ====\nTeam 1: " + str(team1Points) + " Team 2 : " + str(team2Points))
    
    # Prompt user to save full game output
    save = input("Save game output? (yes/<enter>) ")
    if save.upper() == "YES":
        filename = input("Enter filename: ")
        with open(filename, "w+") as outfile:
            outfile.write(gameOutput)

def promptSaveMap(initialMatrix):
    """Prompt user to save map for a future game"""
    save = input("Save map? (yes/<enter>) ")
    if save.upper() == "YES":
        filename = input("Enter filename: ")
        with open(filename, "w+") as outfile:
            for line in initialMatrix:
                outfile.write(line + "\n")

# Ensure that only 'main' process/thread can execute this
if __name__ == '__main__':
    ants = []
    config = generateGameConfig()
    matrix = constructMap(config)
    initialMatrix = matrixToStrList(matrix)
    gameLoop(matrix, ants, config)
    promptSaveMap(initialMatrix)
