from AntStrategy import AntStrategy

class VerticalStrat(AntStrategy):
    '''Move up and down within grid boundaries'''

    def __init__(self, max_x, max_y, anthill):
        super().__init__(max_x, max_y, anthill)
        self.direction = "NORTH"

    def receive_info(self, messages):
        '''This ant ignores messages passed to it'''
        pass

    def send_info(self):
        '''This ant doesn't send any messages'''
        return []
    
    def one_step(self, x, y, vision):
        '''Return next move, changing direction when a boundary is reached'''
        if self.direction == "SOUTH":
            if x < self.max_y:
                return self.direction
            else:
                self.direction = "NORTH"
                return self.direction
        elif self.direction == "NORTH":
            if x > 0:
                return self.direction
            else:
                self.direction = "SOUTH"
                return self.direction
