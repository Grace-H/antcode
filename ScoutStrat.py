from AntStrategy import AntStrategy
import random

class ScoutStrat(AntStrategy):
    '''Explores the grid and reports to teammates.
    
    This ant doesn't score, but it moves in an X pattern around grid to report
    surroundings to teammates.
    '''
    def __init__(self, max_x, max_y, anthill):
        super().__init__(max_x, max_y, anthill)
        self.outbox = []
        self.direction = "WEST"
        
        # Build an internal map from what's been discovered
        self.grid = [["." for y in range(max_y)] for x in range(max_x)]
        for i in range(max_x):
            self.grid[i][0] = "#"
            self.grid[i][max_y - 1] = "#"
        for i in range(max_y):
            self.grid[0][i] = "#"
            self.grid[max_x - 1][i] = "#"
        self.grid[int((max_x-1)/2)][1] = "@"
        self.grid[max_x-(int((max_x-1)/2))-1][max_y - 2] = "X"
        
        self.lastPlace = None # Where ant was last, to check if ant's movement blocked
        
        # Variables for navigating to corners
        self.targets = [(1, 1), (max_x - 1, max_y - 1), (1, max_y - 1), (max_x - 1, 1)]
        self.currentTarget = 0
        self.visited = []

    def receiveInfo(self, messages):
        '''Use teammates' input to update internal map.
        '''
        for m in messages:
            x, y, agent = m.split()
            self.grid[int(x)][int(y)] = agent

    def sendInfo(self):
        '''Pass off messages created in the last round.'''
        toReturn = self.outbox
        self.outbox = []
        return toReturn
    
    def oneStep(self, x, y, vision, food):
        '''Move towards next target corner of the grid, forming an X pattern.'''
        
        # Dictionary of mappings between cardinal directions and (y, x) in vision

        cardinals = { "NORTH": (1, 0),
                "SOUTH": (1, 2),
                "EAST": (2, 1),
                "WEST": (0, 1),
                "NORTHEAST": (2, 0),
                "SOUTHEAST": (2, 2),
                "SOUTHWEST": (0, 2),
                "NORTHWEST": (0, 0) }
        
        # Movement was blocked due to conflict, move random
        if (x, y) == self.lastPlace:
            while True:
                move = random.choice(["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST"])
                coords = cardinals[move]
                if "#" not in vision[coords[0]][coords[1]]:
                    print(move)
                    return move
        self.lastPlace = (x, y)

        # If ant's reached current target, set target to next target
        if self.targets[self.currentTarget][0] == x and self.targets[self.currentTarget][0] == y:
            self.currentTarget = (self.currentTarget + 1) % 4
            self.visited = []

        self.visited.append((x,y))
        
        # Find best direction to move to get to target coordinates
        minDistance = 100000
        move = "HERE"
        for direct, coords in cardinals.items():
            for agent in vision[coords[0]][coords[1]]:
                newX = x + coords[0] - 1
                newY = y + coords[1] - 1
                self.grid[newX][newY] = agent
                self.outbox.append(str(newX) + " " + str(newY) + " " + agent)
                if agent != "#" and (newX, newY) not in self.visited:
                    distance = abs(newX - self.targets[self.currentTarget][0]) + abs(newY - self.targets[self.currentTarget][1])
                    if distance < minDistance:
                        minDistance = distance
                        move = direct
        return move
