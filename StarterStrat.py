from AntStrategy import AntStrategy
import random

class StarterStrat(AntStrategy):
    """An ant's strategy (brains) for moving during the game.
    
    See superclass documentation for more about this class's methods and
    attributes. This is a file you can copy to start making your own strategies.
    """
    
    def __init__(self, max_x, max_y, anthill):
        super().__init__(max_x, max_y, anthill) # Call constructor in superclass

    def receive_info(self, messages):
        """Receive messages sent by teammates in the last round."""
        pass

    def send_info(self):
        """Send messages to teammates at the end of a round."""
        return []
    
    def one_step(self, x, y, vision, food):
        '''Calculate and return a randomly chosen, but valid, next move.'''
        return "PASS"
