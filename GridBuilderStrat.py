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
            self.anthill_xy = (int((max_x-1)/2), 1)
        else:                
            self.anthill_xy = (max_x - (int((max_x - 1) / 2)) - 1, max_y - 2)
        self.grid[self.anthill_xy[0]][self.anthill_xy[1]] = anthill

        self.visited = [] # Past locations to prevent backtracking when going to hill
        self.last_place = None # Tuple (x, y) where ant was last

    def receive_info(self, messages):
        '''Update internal grid with messages received from teammates.
        
        Messages on this team have the format: X Y AGENT'''
        for m in messages:
            x, y, agent = m.split()
            self.grid[int(x)][int(y)] = agent

    def send_info(self):
        '''Send and clear outbox list of messages from this round'''
        to_return = self.outbox
        self.outbox = []
        return to_return
    
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
        if (x, y) == self.last_place:
            while True:
                move = random.choice(["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST"])
                coords = cardinals[move]
                if "#" not in vision[coords[0]][coords[1]]:
                    return move
        self.last_place = (x, y)

        # Survey surroundings, dropping/getting if there's an obvious move
        # Also compare directions to find best way to get to anthill
        min_distance = 100000
        move = (x, y, "HERE")
        for direction, coords in cardinals.items():
            for agent in vision[coords[0]][coords[1]]:
                new_x = x + coords[0] - 1
                new_y = y + coords[1] - 1
                self.grid[new_x][new_y] = agent
                self.outbox.append(str(new_x) + " " + str(new_y) + " " + agent)
                if not food and agent.isdigit():
                    return "GET " + direction
                if food and agent == self.anthill:
                    self.visited = []
                    return "DROP " + direction
                elif food:
                    if agent != "#" and (new_x, new_y) not in self.visited:
                        distance = abs(new_x - self.anthill_xy[0]) + abs(new_y - self.anthill_xy[1])
                        if distance < min_distance:
                            min_distance = distance
                            move = (new_x, new_y, direction)

        # If carrying food, move towards anthill using the direction just chosen
        if food:
            self.visited.append((move[0], move[1]))
            return move[2]

        # Otherwise, find closest food
        if not food:
            min_cost = 1000000 # Manhattan distance to food and then to anthill
            min_food = None
            for xx in range(1, self.max_x - 1):
                for yy in range(1, self.max_y - 1):
                    if self.grid[xx][yy].isdigit() and self.grid[xx][yy] != "0":
                        cost = abs(xx - x) + abs(yy - y) + abs(xx - self.anthill_xy[0]) + abs(yy - self.anthill_xy[1])
                        if cost < min_cost:
                            min_cost = cost
                            min_food = (xx, yy)
            # Move towards closest food pile if one was found
            if min_food:
                min_distance = 1000000
                move = "HERE"
                for direction, coords in cardinals.items():
                    if direction != "HERE" and "#" not in vision[coords[0]][coords[1]]:
                        new_x = x + coords[0] - 1
                        new_y = y + coords[1] - 1
                        distance = abs(new_y - min_food[1]) + abs(new_x - min_food[0])
                        if distance < min_distance:
                            min_distance = distance
                            move = direction
                return move
            # If no known food piles are found, move randomly
            else:
                while True:
                    move = random.choice(["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST"])
                    coords = cardinals[move]
                    if "#" not in vision[coords[0]][coords[1]]:
                        return move
