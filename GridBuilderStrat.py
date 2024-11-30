from AntStrategy import AntStrategy
import random

class GridBuilderStrat(AntStrategy):
    '''Build an internal version of arena through team communication.

    Based on internal grid, repeatedly go to closest food and return to hill.
    '''
    
    def __init__(self, max_x, max_y, anthill):
        super().__init__(max_x, max_y, anthill)
        self.outbox = [] # Queued messages to send
        
        # Initialize internal grid
        self.grid = [["." for y in range(max_y)] for x in range(max_x)]
        for i in range(max_x):
            self.grid[i][0] = "#"
            self.grid[i][max_y - 1] = "#"
        for i in range(max_y):
            self.grid[0][i] = "#"
            self.grid[max_x - 1][i] = "#"
        if anthill == "@":
            self.anthillXY = (int((max_x-1)/2), 1)
        else:                
            self.anthillXY = (max_x - (int((max_x - 1) / 2)) - 1, max_y - 2)
        self.grid[self.anthillXY[0]][self.anthillXY[1]] = anthill

        self.visited = [] # Past locations, used to prevent backtracking
        self.lastPlace = None # Tuple (x, y) where ant was last

    def receive_info(self, messages):
        '''Update internal grid with messages received from teammates.
        
        Messages on this team have the format: X Y AGENT'''
        for m in messages:
            x, y, agent = m.split()
            self.grid[int(x)][int(y)] = agent

    def send_info(self):
        '''Send and clear outbox list of messages from this round'''
        toReturn = self.outbox
        self.outbox = []
        return toReturn
    
    def one_step(self, x, y, vision, food):
        '''Report surroundings to teammates and calculate best move.
        
        If carrying food, move in direction closest to anthill. If not, move 
        towards nearest food pile. If no known food piles, move randomly.
        '''
        # Cardinal directions (x, y): indices in vision array for each
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
                    return move
        self.lastPlace = (x, y)

        # Survey surroundings, dropping/getting if there's an obvious move
        # Also compare directions to find best way to get to anthill
        minDistance = 100000
        move = (x, y, "HERE")
        for direct, coords in cardinals.items():
            for agent in vision[coords[0]][coords[1]]:
                newX = x + coords[0] - 1
                newY = y + coords[1] - 1
                self.grid[newX][newY] = agent
                self.outbox.append(str(newX) + " " + str(newY) + " " + agent)
                if not food and agent.isdigit():
                    return "GET " + direct
                if food and agent == self.anthill:
                    self.visited = []
                    return "DROP " + direct
                elif food:
                    if agent != "#" and (newX, newY) not in self.visited:
                        distance = abs(newX - self.anthillXY[0]) + abs(newY - self.anthillXY[1])
                        if distance < minDistance:
                            minDistance = distance
                            move = (newX, newY, direct)

        # If carrying food, move towards anthill using the direction just chosen
        if food:
            self.visited.append((move[0], move[1]))
            return move[2]

        # Otherwise, find closest food
        if not food:
            minCost = 1000000 # Manhattan distance to food and then to anthill
            minFood = None
            for xx in range(1, self.max_x - 1):
                for yy in range(1, self.max_y - 1):
                    if self.grid[xx][yy].isdigit() and self.grid[xx][yy] != "0":
                        cost = abs(xx - x) + abs(yy - y) + abs(xx - self.anthillXY[0]) + abs(yy - self.anthillXY[1])
                        if cost < minCost:
                            minCost = cost
                            minFood = (xx, yy)
            # Move towards closest food pile if one was found
            if minFood:
                minDistance = 1000000
                move = "HERE"
                for direct, coords in cardinals.items():
                    if direct != "HERE" and "#" not in vision[coords[0]][coords[1]]:
                        newX = x + coords[0] - 1
                        newY = y + coords[1] - 1
                        distance = abs(newY - minFood[1]) + abs(newX - minFood[0])
                        if distance < minDistance:
                            minDistance = distance
                            move = direct
                return move
            # If no known food piles are found, move randomly
            else:
                while True:
                    move = random.choice(["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST"])
                    coords = cardinals[move]
                    if "#" not in vision[coords[0]][coords[1]]:
                        return move
