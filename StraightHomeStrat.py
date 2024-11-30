from AntStrategy import AntStrategy
import random

class StraightHomeStrat(AntStrategy):
    '''When carrying food, find fastest move to anthill.'''
    
    def __init__(self, max_x, max_y, anthill):
        super().__init__(max_x, max_y, anthill)
        self.inbox = []
        self.outbox = []
        self.direction = "WEST"
        if anthill == "@":
            self.anthillXY = (int((max_x-1)/2), 1)
        else:
            self.anthillXY = (max_x-(int((max_x-1)/2))-1, max_y-2)
        self.visited = [] # When going to anthill, cells that have already been visited

    def receive_info(self, messages):
        '''
        Receive messages sent by teammates in the last round. Called by game.
        You may add to this method, but do not call it yourself.
        '''
        self.inbox = messages

    def send_info(self):
        '''
        Send messages. Called by game to get queued messages
        You may add to this method, but do not call it yourself.
        '''
        toReturn = self.outbox # lists are a reference type--does this need to be copy()?
        self.outbox = []
        return toReturn
    
    def one_step(self, x, y, vision, food):
        '''Calculate and return a randomly chosen, but valid, next move.'''
        # Dictionary of string directions to (x, y) indices in vision
        cardinals = { "NORTH": (1, 0),
                "SOUTH": (1, 2),
                "EAST": (2, 1),
                "WEST": (0, 1),
                "NORTHEAST": (2, 0),
                "SOUTHEAST": (2, 2),
                "SOUTHWEST": (0, 2),
                "NORTHWEST": (0, 0),
                "HERE": (1,1) }

        # Move towards anthill with food, GET if find food while not carrying
        minDistance = 100000
        move = (x, y, "HERE")
        for direct, coords in cardinals.items():
            for agent in vision[coords[0]][coords[1]]:
                if food:
                    if agent == self.anthill:
                        self.visited = []
                        return "DROP " + direct
                    else:
                        newX = x + coords[0] - 1
                        newY = y + coords[1] - 1
                        if agent != "#" and (newX, newY) not in self.visited:
                            distance = abs(newX - self.anthillXY[0]) + abs(newY - self.anthillXY[1])
                            if distance < minDistance:
                                minDistance = distance
                                move = (newX, newY, direct)
                if not food and agent.isdigit():
                    return "GET " + direct

        if food:
            self.visited.append((move[0], move[1]))
            return move[2]

        # Otherwise move randomly
        while True:
            move = random.choice(["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST"])
            coords = cardinals[move]
            if "#" not in vision[coords[0]][coords[1]]:
                return move
