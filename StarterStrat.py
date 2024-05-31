from AntStrategy import AntStrategy
import random

class StarterStrat(AntStrategy):
    """An ant's strategy (brains) for moving during the game.
    
    See superclass documentation for more about this class's methods and attributes
    """
    
    def __init__(self, max_x, max_y, anthill):
        super().__init__(max_x, max_y, anthill) # Call constructor in superclass

    def receiveInfo(self, messages):
        """Receive messages sent by teammates in the last round."""
        pass

    def sendInfo(self):
        """Send messages to teammates at the end of a round."""
        return []
    
    def oneStep(self, x, y, vision, food):
        '''Calculate and return a randomly chosen, but valid, next move.'''
        return "PASS"
