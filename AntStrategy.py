class AntStrategy:
    '''An ant's strategy for moving during the game.
    
    Based on ant's state provided from the main game, calculates next moves and
    passes messages to teammate ants. Your strategy class should be a subclass 
    of this one. See the samples for examples of how to do this. You shouldn't 
    need to modify this class.
    
    Attributes:
        max_x: Number of columns in the game matrix
        max_y: Number of rows in the game matrix
        anthill: character, either 'X' or '@', of ant's anthill in the matrix
    '''

    def __init__(self, max_x, max_y, anthill):
        '''Initialize the strategy instance.
        
        Call from subclass. You will be able to access each of the attributes 
        from the subclass.
        '''
        self.max_x = max_x
        self.max_y = max_y
        self.anthill = anthill
    
    def receiveInfo(self, messages):
        '''Receive messages sent by teammates in the last round.
        
        Called by game at the beginning of a round to deliver messages sent by 
        all ants on the same team during the last round (including yourself). 
        Parse, store, and handle incoming messages here.
        
        Args:
            messages: List of messages sent by teammates in last round
        '''
        raise NotImplementedError()

    def sendInfo(self):
        '''Send messages to your teammates. 
        
        Called once by game at the end of each round. Messages will be passed to
        teammates at the beginning of the next round.
        
        Returns:
            List of messages to pass to teammates
        '''
        raise NotImplementedError()
    
    def oneStep(self, x, y, vision, food):
        '''Calculate and return the next move for this ant.
        
        Args:
            x: Ant's current column in the matrix
            y: Ant's current row in the matrix
            vision: Ant's immediate surroundings one unit in all directions with
                    the ant at the center. 3x3 matrix where each index is a list
                    of characters representing the objects at that location.
                    First dimension is x, second dimension is y: vision[x][y]
            food: boolean for if the Ant is currently carrying food

        Returns:
            All-caps string indicating the ant's next move. Options include:
                - Moving: provide a cardinal direction
                - Get food: GET followed by a direction
                - Drop food: DROP followed by a direction
            
            Cardinal directions: NORTH, NORTHEAST, EAST, SOUTHEAST, SOUTH, 
            SOUTHWEST, WEST, NORTHWEST, HERE
        '''
        raise NotImplementedError()
