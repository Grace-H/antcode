from AntStrategy import AntStrategy
import random

class SmarterRandomStrat(AntStrategy):
    '''If carrying food, limit directions chosen from to get closer to anthill.

    If not, moves randomly and grabs first food.
    '''
    def __init__(self, max_x, max_y, anthill):
        super().__init__(max_x, max_y, anthill)
        self.inbox = []
        self.outbox = []
        self.direction = "WEST"

    def receiveInfo(self, messages):
        '''Receive messages sent by teammates in the last round.'''
        self.inbox = messages

    def sendInfo(self):
        '''Send messages.'''
        toReturn = self.outbox
        self.outbox = []
        return toReturn
    
    def oneStep(self, x, y, vision, food):
        '''Calculate and return a randomly chosen, but valid, next move.'''
        cardinals = { "NORTH": (1, 0),
                "SOUTH": (1, 2),
                "EAST": (2, 1),
                "WEST": (0, 1),
                "NORTHEAST": (2, 0),
                "SOUTHEAST": (2, 2),
                "SOUTHWEST": (0, 2),
                "NORTHWEST": (0, 0),
                "HERE": (1,1) }

        self.outbox.append("message")

        # DROP if carrying food near anthill, GET if find food while not carrying
        for direct, coords in cardinals.items():
            for agent in vision[coords[0]][coords[1]]:
                if food and agent == self.anthill:
                    return "DROP " + direct
                if not food and agent.isdigit():
                    return "GET " + direct

        # Take ant towards hill if it's carrying food
        if food:
            if self.anthill == "@":
                return random.choice(["NORTH", "NORTHEAST", "EAST", "WEST", "NORTHWEST"])
            else:
                return random.choice(["SOUTH", "SOUTHEAST", "EAST", "WEST", "SOUTHWEST"])

        # Otherwise move randomly
        while True:
            move = random.choice(["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST"])
            coords = cardinals[move]
            if "#" not in vision[coords[0]][coords[1]]:
                return move
