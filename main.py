# Ant Resource Collection Game
#
# To make ants and run game:
# 1. Create a subclass of AntStrategy that will direct an ant's actions during 
#    the game: Copy StarterStrat.py, rename it, and finish the methods.
# 2. Import your AntStrategy subclass below (see comment A)
# 3. Put your ants on a teams by adding them to the appropriate tuples (B)
# 4. Run this file. Ants will have 200 moves to try to score the most points
#    by dropping food at their team's anthill

import random
import time
from concurrent.futures import wait, ProcessPoolExecutor, ThreadPoolExecutor, TimeoutError

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

# --- Begin Game ---
ants = []

# Matrix variables  
rows = random.randrange(20,25) # Number of rows
cols = random.randrange(20,25) # Number of columns
matrix = []
numObstacles = 10 #Number of obstacles
amountFood = random.randrange(20, 25) # Amount of food
northHill = (int((cols-1)/2), 1) # Location of north hill
southHill = (cols-(int((cols-1)/2))-1, rows-2) # Location of south hill
team1Starting = [(3,1), (6,1), (cols-7,1), (cols-4,1)]
team2Starting = [(3,rows-2), (6,rows-2), (cols-7,rows-2), (cols-4,rows-2)]

# Matrix constants & ascii mappings
EMPTY = 0
WALL = 11
NORTHHILL = 13
SOUTHHILL = 14
NORTHTEAM1 = 15
NORTHTEAM2 = 16
NORTHTEAM3 = 17
NORTHTEAM4 = 18
SOUTHTEAM1 = 19
SOUTHTEAM2 = 20
SOUTHTEAM3 = 21
SOUTHTEAM4 = 22
antMatrixDict = {} # Mapping of Ants to {NORTH,SOUTH}TEAM{1,2} above
matrixSymbols = { EMPTY: '.', WALL: '#', NORTHHILL: '@', SOUTHHILL: 'X',
                NORTHTEAM1: 'A', NORTHTEAM2: 'B', NORTHTEAM3: 'C', NORTHTEAM4: 'D',
                SOUTHTEAM1: 'E', SOUTHTEAM2: 'F', SOUTHTEAM3: 'G', SOUTHTEAM4: 'H' }  

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

def isOpenCell(matrix, x, y):
    """Check if a cell in matrix is in bounds and not a wall."""
    return x > 0 and x < cols and y > 0 and y < rows and WALL not in matrix[x][y]
    
def initializeAnts(team1Strats, team1Locs, team2Strats, team2Locs):
    """Instantiate ant classes for each team.
    
    Populate ants list and dictionary of Ant->matrixSymbol mappings. Takes two 
    lists for each team: AntStrategy class names and inital (x, y) positions
    """
    # Team 1
    for Strat, (x, y), sym, num in zip(team1Strats, team1Locs, ["A", "B", "C", "D"], 
    [NORTHTEAM1, NORTHTEAM2, NORTHTEAM3, NORTHTEAM4]):
        try:
            antStrat = Strat(cols, rows, matrixSymbols[NORTHHILL])
        except Exception as e:
            print("Ant initialization failed for Team 1 AntStrategy: " + str(Strat))
            continue
        ants.append(Ant(antStrat, x, y, 1, sym))   
        antMatrixDict[ants[-1]] = num

    # Team 2
    for Strat, (x, y), sym, num in zip(team2Strats, team2Locs, ["E", "F", "G", "H"],
    [SOUTHTEAM1, SOUTHTEAM2, SOUTHTEAM3, SOUTHTEAM4]):
        try:
            antStrat = Strat(cols, rows, matrixSymbols[SOUTHHILL])
        except Exception as e:
            print("Ant initialization failed for Team 2 AntStrategy: " + str(Strat))
            continue
        ants.append(Ant(antStrat, x, y, 1, sym))
        antMatrixDict[ants[-1]] = num

def placeObstacles(matrix, numObstacles):
    """Place several vertical and horizontal barriers randomly in matrix."""
    while numObstacles > 0: # place obstacles (including mirror image)
        pickX = random.randrange(2, (cols - 3)) # don't place on left or right sides
        pickY = random.randrange(3, (rows - 4)) # don't place in top two or bottom two rows
        if not matrix[pickX][pickY]:
            direction = random.randrange(0, 1) # 0 is horizontal, 1 is vertical
            numberOfSquare = random.randrange(1, 5) # length of obstacle
            if direction == 0: # horizontal obstacle
                for x in range(numberOfSquare):
                    if pickX < cols/2: # left half of screen
                        matrix[pickX+x][pickY] = [WALL]
                        matrix[cols-pickX-1-x][rows-pickY-1] = [WALL]
                    else: # right half of screen
                        matrix[pickX-x][pickY] = [WALL]
                        matrix[cols-pickX-1+x][rows-pickY-1] = [WALL]
            else: # direction == 1, vertical obstacle
                for y in range(numberOfSquare):
                    if pickY < rows/2: # top half of screen
                        matrix[pickX][pickY+y] = [WALL]
                        matrix[cols-pickX-1][rows-pickY-1-y] = [WALL]
                    else: # bottom half of screen
                        matrix[pickX][pickY-y] = [WALL]
                        matrix[cols-pickX-1][rows-pickY-1+y] = [WALL]
            numObstacles -= 1

def placeFood(matrix, amountFood):
    """Place ints representing food piles randomly in matrix."""
    while amountFood > 0: # place food (including mirror image)
        pickX = random.randrange(1, cols - 1)
        pickY = random.randrange(2, rows - 3) # Don't place in top or bottom row
        if not matrix[pickX][pickY]:
            pile = random.randrange(1,9)
            matrix[pickX][pickY] = [pile]
            matrix[cols-pickX-1][rows-pickY-1] = [pile]
            amountFood -= 1
            
def placeAnts(matrix, ants):
    """Put corresponding number for each live ant at x,y location in matrix."""
    for a in ants:
        if a.alive:
            matrix[a.x][a.y].append(antMatrixDict[a])
        
def initializeMatrix(matrix, amountFood, numObstacles, ants):
    """Construct and populate a cols X rows list with outer walls, obstacles, food, and ants."""
    for i in range(cols): # Create initial array
        col = []
        for j in range(rows):
            col.append([])
        matrix.append(col)
    
    for i in range(rows): # Surround with walls
        matrix[0][i] = [WALL]
        matrix[cols-1][i] = [WALL]
    for i in range(cols):
        matrix[i][0] = [WALL]
        matrix[i][rows-1] = [WALL]
    matrix[northHill[0]][northHill[1]] = [NORTHHILL]
    matrix[southHill[0]][southHill[1]] = [SOUTHHILL]
    placeObstacles(matrix, numObstacles)
    placeFood(matrix, amountFood)
    placeAnts(matrix, ants)
    
def printMap(matrix):
    """Print an ascii rendering of the map.
    
    If multiple items occupy the same
    cell, only print the last one (prioritizes things that move (ants))
    """
    for row in range(rows):
        output = ""
        for col in range(cols):
            if not matrix[col][row]:
                output += matrixSymbols[EMPTY]
            elif matrix[col][row][-1] > 0 and matrix[col][row][-1] < 10:
                output += str(matrix[col][row][-1])
            elif matrix[col][row][-1] in matrixSymbols:
                output += matrixSymbols[matrix[col][row][-1]]
        print(output)
        
def generateVision(matrix, x, y):
    """Return a 3x3 matrix representing the area surrounding x,y in the matrix.
    
    Assumes x & y are inside the outer walls.
    """
    vision = []
    for j in range(x-1, x+2):
        row = []
        for i in range(y-1, y+2):
            if not matrix[j][i]:
                row.append([matrixSymbols[EMPTY]])
            else:
                cell = []
                for agent in matrix[j][i]:
                    if agent > 0 and agent < 10:
                        cell.append(str(agent))
                    elif agent in matrixSymbols:
                        cell.append(matrixSymbols[agent])
                row.append(cell)
        vision.append(row)
    return vision

def killAnt(ant):
    ant.die()
    matrix[ant.x][ant.y].remove(antMatrixDict[ant])

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

def gameLoop(matrix, ants):
    """Run game with initialized matrix and ants."""
    team1Points = 0
    team2Points = 0
    team1Messages = []
    team2Messages = []
    
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

    for _ in range(200):
        input() # Pause for me to hit enter!
        #time.sleep(1) # Comment this out for stress testing

        # Pass messages to ants and clear buffers
        for a in ants:
            try:
                a.send(team1Messages if a.team == 1 else team2Messages)
            except Exception as e:
                print("Error in " + a.symbol + " when receiving messages: " + str(e))
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
                print("Timeout waiting for oneStep in " + a.symbol)
                killAnt(a)
            except Exception as e:
                print("Error in oneStep in " + a.symbol + ": " + str(e))
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
                        for i, agent in enumerate(matrix[targetX][targetY]):
                            if agent == NORTHHILL:
                                team1Points += 1
                                break
                            elif agent == SOUTHHILL:
                                team2Points += 1
                                break
                            elif agent > 0 and agent < 10: # Food pile
                                matrix[targetX][targetY][i] += 1
                                break
                        else: # This else belongs to for, executes when loop exits normally
                            matrix[targetX][targetY] = [1] + matrix[targetX][targetY]

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
                for i, agent in enumerate(matrix[targetX][targetY]):
                    if (agent > 0 and agent < 10) and agent >= len(aList):
                        for a in aList:
                            a.food = True
                        matrix[targetX][targetY][i] -= len(aList)
                        if matrix[targetX][targetY][i] == 0:
                            matrix[targetX][targetY].remove(0)
                            break

        # Update arena & redraw screen
        for loc, a in proposedMoves.items():
            if a: # May be none if it was the site of a movement conflict
                matrix[a.x][a.y].remove(antMatrixDict[a])
                a.x = loc[0]
                a.y = loc[1]

        placeAnts(matrix, ants)
        printMap(matrix)
        print("Team 1:", str(team1Points), "Team 2:", str(team2Points))

        # Receive messages from ants from this round
        for a in ants:
            if a.alive:
                try:
                    msgs = a.recv()
                    if type(msgs) != list:
                        raise ValueError("Messages should be of type list.")
                except Exception as e:
                    print("Error in " + a.symbol + " when sending messages: " + str(e))
                    killAnt(a)
                    continue

                if a.team == 1:
                    team1Messages += msgs
                elif a.team == 2:
                    team2Messages += msgs

        ants[:] = [a for a in ants if a.alive] # Remove the dead ants

    pool.shutdown()
    print("\n==== Final score ====\nTeam 1: " + str(team1Points) + " Team 2 : " + str(team2Points))

# Ensure that only 'main' process/thread can execute this
if __name__ == '__main__':
    print("Press enter to execute next round")    
    initializeAnts(team1, team1Starting, team2, team2Starting)
    initializeMatrix(matrix, amountFood, numObstacles, ants)
    printMap(matrix)
    gameLoop(matrix, ants)
