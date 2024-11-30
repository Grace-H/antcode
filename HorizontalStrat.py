from AntStrategy import AntStrategy

class HorizontalStrat(AntStrategy):
    '''Move east and west within grid boundaries'''

    def __init__(self, max_x, max_y, anthill):
        super().__init__(max_x, max_y, anthill)
        self.direction = "WEST"

    def receive_info(self, messages):
        '''Receive messages sent by teammates in the last round.
        Called by game'''
        pass

    def send_info(self):
        '''Send messages. Called by game to get queued messages'''
        return []
    
    def one_step(self, x, y, vision, food):
        '''Return next move'''
        if self.direction == "EAST":
            if x < self.max_x:
                return self.direction
            else:
                self.direction = "WEST"
                return self.direction
        elif self.direction == "WEST":
            if x > 0:
                return self.direction
            else:
                self.direction = "EAST"
                return self.direction
