import random
import time
import concurrent.futures
from ant1 import HorizontalStrat as AntStrat1
from ant2 import VerticalStrat as AntStrat2
from RandomStrat import RandomStrat
    
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

# Ant variables
team1 = (RandomStrat, RandomStrat, RandomStrat, RandomStrat) # Update these two tuples when changing
team2 = (RandomStrat, RandomStrat, RandomStrat, RandomStrat) # which ants are on which teams

ants = []
deadAnts = []

# Constants for rendering matrix
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
    """
    Instantiate ant classes for each team, populating ants list and dictionary
    of Ant->matrixKey mappings. Takes two lists for each team: class names and
    inital positions
    """
    # Team 1
    for Strat, (x, y), sym, num in zip(team1Strats, team1Locs, ["A", "B", "C", "D"], 
    [NORTHTEAM1, NORTHTEAM2, NORTHTEAM3, NORTHTEAM4]):
        ants.append(Ant(Strat(rows, cols, matrixSymbols[NORTHHILL]), x, y, 1, sym))
        antMatrixDict[ants[-1]] = num
        
    # Team 2
    for Strat, (x, y), sym, num in zip(team2Strats, team2Locs, ["E", "F", "G", "H"],
    [SOUTHTEAM1, SOUTHTEAM2, SOUTHTEAM3, SOUTHTEAM4]):
        ants.append(Ant(Strat(rows, cols, matrixSymbols[SOUTHHILL]), x, y, 1, sym))
        antMatrixDict[ants[-1]] = num

def placeObstacles(matrix, numObstacles):
    while numObstacles > 0:# place obstacles (including mirror image)
        pickX = random.randrange(2, (cols - 3))# don't place on left or right sides
        pickY = random.randrange(3, (rows - 4))# don't place in top two or bottom two rows
        if not matrix[pickX][pickY]:
            direction = random.randrange(0, 1) # 0 is horizontal, 1 is vertical
            numberOfSquare = random.randrange(1, 5) # length of obstacle
            if direction == 0: #horizontal obstacle
                for x in range(numberOfSquare):
                    if pickX < cols/2:#left half of screen
                        matrix[pickX+x][pickY] = [WALL]
                        matrix[cols-pickX-1-x][rows-pickY-1] = [WALL]
                    else:#right half of screen
                        matrix[pickX-x][pickY] = [WALL]
                        matrix[cols-pickX-1+x][rows-pickY-1] = [WALL]
            else: #direction == 1, vertical obstacle
                for y in range(numberOfSquare):
                    if pickY < rows/2:#top half of screen
                        matrix[pickX][pickY+y] = [WALL]
                        matrix[cols-pickX-1][rows-pickY-1-y] = [WALL]
                    else:#bottom half of screen
                        matrix[pickX][pickY-y] = [WALL]
                        matrix[cols-pickX-1][rows-pickY-1+y] = [WALL]
            numObstacles -= 1

def placeFood(matrix, amountFood):
    while amountFood > 0:# place food (including mirror image)
        pickX = random.randrange(1, cols - 1)
        pickY = random.randrange(2, rows - 3)# Don't place in top or bottom row
        if not matrix[pickX][pickY]:
            pile = random.randrange(1,9)
            matrix[pickX][pickY] = [pile]
            matrix[cols-pickX-1][rows-pickY-1] = [pile]
            amountFood -= 1
            
def placeAnts(matrix, ants):
    """Put appropriate code for each live ant at x,y location in matrix."""
    for a in ants:
        if a.alive:
            matrix[a.x][a.y].append(antMatrixDict[a])
        
def initializeMatrix(matrix, amountFood, numObstacles, ants):
    for i in range(cols):# Create initial array
        col = []
        for j in range(rows):
            col.append([])
        matrix.append(col)
    
    for i in range(rows):# Surround with walls
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
    """
    Print an ascii rendering of the map. If multiple items occupy the same
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
    """
    Return a 3x3 matrix representing the area surrounding x,y in the matrix.
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
    
def gameLoop(matrix, ants):
    team1Points = 0
    team2Points = 0
    team1Messages = []
    team2Messages = []
    
    transformXY = { "NORTH": lambda x, y: (x, y-1),
                    "SOUTH": lambda x, y: (x, y+1),
                    "EAST": lambda x, y: (x+1, y),
                    "WEST": lambda x, y: (x-1, y),
                    "NORTHEAST": lambda x, y: (x+1, y-1),
                    "SOUTHEAST": lambda x, y: (x+1, y+1),
                    "SOUTHWEST": lambda x, y: (x-1, y+1),
                    "NORTHWEST": lambda x, y: (x-1, y-1) }
    while True:
        # Assume all ants are alive at beginning of the round
        
        #input() # Pause for me to hit enter!
        #time.sleep(1) # Comment this out for stress testing
        
        # Pass messages to ants and clear buffers
        for a in ants:
            try:
                if a.team == 1:
                    a.send(team1Messages)
                elif a.team == 2:
                    a.send(team2Messages)
            except:
                a.die()
                deadAnts.append(a)
    
        # Prompt ants for next move (serial for now)
        moves = dict((a, "PASS") for a in ants)
        for a in ants:
            if a.alive:
                try:
                    moves[a] = a.act(generateVision(matrix, a.x, a.y)).split()
                    print(moves[a])
                except:
                    a.die()
                    deadAnts.append(a)
                
        # Parse moves
        proposedMoves = {}
        proposedGets = {}
        for a, move in moves.items():
            loc = (a.x, a.y)
            
            if move[0] in transformXY and len(move) == 1: # Cardinal movement
                newLoc = transformXY[move[0]](loc[0], loc[1])
                if isOpenCell(matrix, newLoc[0], newLoc[1]):
                    loc = newLoc

            elif move[0] == "GET":
                if len(move) != 2 or move[1] not in transformXY:
                    a.die()
                    deadAnts.append(a)
                elif not a.food: # Can't carry more than one!
                    targetX, targetY = transformXY[move[1]](a.x, a.y)
                    if isOpenCell(matrix, targetX, targetY):
                        if (targetX, targetY) in proposedGets:
                            proposedGets[(targetX, targetY)].append(a)
                        else:
                            proposedGets[(targetX, targetY)] = [a]
                            
            elif move[0] == "DROP":
                if len(move) != 2 or move[1] not in transformXY:
                    a.die()
                    deadAnts.append(a)
                elif a.food:
                    targetX, targetY = transformXY[move[1]](a.x, a.y)
                    if isOpenCell(matrix, targetX, targetY):
                        for i, agent in enumerate(matrix[targetX][targetY]):
                            if agent == NORTHHILL:
                                team1Points += 1
                                a.food = False
                                break
                            elif agent == SOUTHHILL:
                                team2Points += 1
                                a.food = False
                                break
                            elif agent > 0 and agent < 10: # Food pile
                                matrix[targetX][targetY][i] += 1
                                a.food = False
                                break
                        else: # This else belongs to for, executes when loop exits normally
                            matrix[targetX][targetY] = [1] + matrix[targetX][targetY]
                            a.food = False
                            
            elif move[0] == "PASS":
                pass
            
            else:
                a.die()
                deadAnts.append(a)
            
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
                
                # Return conflicting ant to original position
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
            if a: # May be none because it was the site of a movement conflict
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
                    if a.team == 1:
                        team1Messages += a.recv()
                    elif a.team == 2:
                        team2Messages += a.recv()
                except:
                    a.die()
                    deadAnts.append(a)

        ants[:] = [a for a in ants if not a in deadAnts] # Remove the dead ants

#print("Press enter to execute next round")    
initializeAnts(team1, team1Starting, team2, team2Starting)
initializeMatrix(matrix, amountFood, numObstacles, ants)
printMap(matrix)
gameLoop(matrix, ants)ameLoop(matrix, ants)
