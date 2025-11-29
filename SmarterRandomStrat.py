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
        self.cardinals = { "NORTH": (1, 0),
                "SOUTH": (1, 2),
                "EAST": (2, 1),
                "WEST": (0, 1),
                "NORTHEAST": (2, 0),
                "SOUTHEAST": (2, 2),
                "SOUTHWEST": (0, 2),
                "NORTHWEST": (0, 0),
                "HERE": (1,1) }

    def receive_info(self, messages):
        '''Receive messages sent by teammates in the last round.'''
        self.inbox = messages

    def send_info(self):
        '''Send messages.'''
        to_return = self.outbox
        self.outbox = []
        return to_return

    def valid_move(self, vision, moves):
        '''Check if a move is valid from the moves available.'''
        while (len(moves) > 0):
            move = random.choice(moves)
            coords = self.cardinals[move]
            if ("#" not in vision[coords[0]][coords[1]]):
                return move
            else:
                moves.remove(move)

        return 'PASS'

    def one_step(self, x, y, vision, food):
        
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
                return self.valid_move(vision, ["NORTH", "NORTHEAST", "EAST", "WEST", "NORTHWEST"])
            else:
                return self.valid_move(vision, ["SOUTH", "SOUTHEAST", "EAST", "WEST", "SOUTHWEST"])

        # Otherwise move randomly
        while True:
            return self.valid_move(vision, ["NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST"])
