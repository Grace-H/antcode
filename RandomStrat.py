from AntStrategy import AntStrategy
import random

class RandomStrat(AntStrategy):
    '''
    Chooses a random, valid move.
    
    Left to its own devices, it will *eventually* score.
    '''

    def __init__(self, max_x, max_y, anthill):
        super().__init__(max_x, max_y, anthill)
        self.direction = "WEST"

    def receiveInfo(self, messages):
        '''This ant doesn't use message passing.'''
        pass

    def sendInfo(self):
        '''Send messages. Returns empty list since ant never sends messages.'''
        return []
    
    def oneStep(self, x, y, vision, food):
        '''Calculate and return a randomly chosen, but valid, next move.'''
        # Mapping of cardinal words to (x, y) indices in vision
        cardinals = { "NORTH": (1, 0),
                "SOUTH": (1, 2),
                "EAST": (2, 1),
                "WEST": (0, 1),
                "NORTHEAST": (2, 0),
                "SOUTHEAST": (2, 2),
                "SOUTHWEST": (0, 2),
                "NORTHWEST": (0, 0),
                "HERE": (1,1) }

        # Keep choosing a move until a valid one is chosen
        while True:
            move = random.choice(["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST", "GET", "DROP"])
            if move == "GET":
                if not food:
                    direction = random.choice(["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST", "HERE"])
                    coords = cardinals[direction]
                    for agent in vision[coords[0]][coords[1]]:
                        if agent.isdigit():
                            print(type(agent))
                            return move + " " + direction
            elif move == "DROP":
                if food:
                    direction = random.choice(["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST", "HERE"])
                    coords = cardinals[direction]
                    if self.anthill in vision[coords[0]][coords[1]]:
                        return move + " " + direction
            else:
                coords = cardinals[move]
                if "#" not in vision[coords[0]][coords[1]]:
                    return move
