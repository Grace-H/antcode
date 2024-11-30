# Ant Resource Collection Game
#
# To make ants and run game:
# 1. Create a subclass of AntStrategy that will direct an ant's actions during 
#    the game: Copy StarterStrat.py, rename it, and finish the methods.
# 2. Import your AntStrategy subclass below (see comment A)
# 3. Put your ants on a teams by adding them to the appropriate tuples (B)
# 4. Run this file. Ants will have 200 moves to try to score the most points
#    by dropping food at their team's anthill

from concurrent.futures import wait, ProcessPoolExecutor, ThreadPoolExecutor, TimeoutError
import os
import random
import time
import traceback

# A. Import student strategies here
from HorizontalStrat import HorizontalStrat
from VerticalStrat import VerticalStrat
from RandomStrat import RandomStrat
from SmarterRandomStrat import SmarterRandomStrat
from StraightHomeStrat import StraightHomeStrat
from GridBuilderStrat import GridBuilderStrat
from ScoutStrat import ScoutStrat
from StarterStrat import StarterStrat
    
# B. Register strategy class names in team1/team2 tuples below, 1-4 ants per team
team1 = (RandomStrat, SmarterRandomStrat, StraightHomeStrat, ScoutStrat)
team2 = (GridBuilderStrat,  StarterStrat, HorizontalStrat, VerticalStrat)
DEBUG = False # Change this to True to get more detailed errors from ant strategies

# --- Begin Game ---

# Configuration variables for randomly generated maps
NUM_OBSTACLES = 10 # Number of obstacles
AMOUNT_FOOD = random.randrange(20, 25) # Number of food piles

# Matrix constants
EMPTY = '.'
WALL = '#'
NORTH_HILL = '@'
SOUTH_HILL = 'X'
NORTH_SYMS = ["A", "B", "C", "D"]
SOUTH_SYMS = ["E", "F", "G", "H"]

class Cell:
    '''Cell in the game matrix.

    Attributes:
        wall: boolean, whether this is a wall
        anthill: str | None, anthill if this cell has an anthill
        food: int, number of food in this cell
        ant: Ant | None, ant in this cell
    '''
    def __init__(self, wall=False, anthill=None, food=0):
        self.wall = wall
        self.anthill = anthill
        self.food = food
        self.ant = None

    def is_empty(self):
        '''Has absolutely nothing in it'''
        return not self.wall and not self.anthill and not self.ant and self.food == 0

    def print_cell(self):
        if self.ant:
            return self.ant.get_symbol()
        elif self.anthill:
            return self.anthill
        elif self.food > 0:
            return str(self.food)
        elif self.wall:
            return WALL
        else:
            return EMPTY

    def __repr__(self):
        return self.print_cell()

class Ant:
    def __init__(self, strategy, x, y, team, symbol):
        self.strategy = strategy
        self.x = x
        self.y = y
        self.team = team
        self.symbol = symbol
        self.food = False
        self.alive = True
    
    def die(self):
        self.alive = False

    def act(self, vision):
        return self.strategy.one_step(self.x, self.y, vision, self.food)
    
    def send(self, messages):
        self.strategy.receive_info(messages)
    
    def recv(self):
        return self.strategy.send_info()

    def get_symbol(self):
        return self.symbol if not self.food else self.symbol.lower()

    def __repr__(self):
        return self.symbol

def is_open_cell(matrix, x, y):
    """Check if a cell in matrix is in bounds and not a wall."""
    return x > 0 and x < len(matrix) and y > 0 and y < len(matrix[0]) and not matrix[x][y].wall
    
def initialize_ants(team1_strats, team1_locs, team2_strats, team2_locs, rows, cols):
    """Instantiate ant classes for each team.
    
    Populate ants list and dictionary of Ant->matrixSymbol mappings. Takes two 
    lists for each team: AntStrategy class names and inital (x, y) positions
    """
    # Team 1
    for Strat, sym in zip(team1_strats, NORTH_SYMS):
        try:
            ant_strat = Strat(rows, cols, NORTH_HILL)
        except Exception as e:
            print("Ant initialization failed for Team 1 AntStrategy: " + str(Strat))
            if DEBUG:
                print(traceback.format_exc())
            continue
        ants.append(Ant(ant_strat, team1_locs[sym][0], team1_locs[sym][1], 0, sym))

    # Team 2
    for Strat, sym in zip(team2_strats, SOUTH_SYMS):
        try:
            ant_strat = Strat(rows, cols, SOUTH_HILL)
        except Exception as e:
            print("Ant initialization failed for Team 2 AntStrategy: " + str(Strat))
            if DEBUG:
                print(traceback.format_exc())
            continue
        ants.append(Ant(ant_strat, team2_locs[sym][0], team2_locs[sym][1], 1, sym))

def generate_game_config():
    """Prompt user for game configuration options, including saved map file

    Returns: dict[str, boolean or str], with the following keys:
        'fast_forward': boolean, continue to end without stopping
        'load_map': boolean, use saved map
        'save_file': str, filename if load_map is True
    """
    config = {
            'fast_forward': False,
            'load_map': False,
            'save_file': None,
    }

    fast_forward = input("Run to the end without pausing? (yes/<enter>) ")
    if fast_forward.upper() == "YES":
        config['fast_forward'] = True

    load_map = input("Use saved map? (yes/<enter>) ")
    if load_map.upper() == "YES":
        config['load_map'] = True

    if config['load_map']:
        filepath = input("Enter path to save file: ")
        if os.path.exists(filepath):
           config['save_file'] = filepath
        else:
            print("File not found, using new map: " + filepath)
            config['load_map'] = False

    return config

def load_save_file(filename):
    """Load saved game data from a file.

    Trusts that map is valid format, with walls, 8 ants, and 2 anthills.

    Returns:
        Dict[str, int or str] of game data with following keys:
            'map': List[str], game matrix
            'team1_starting': (int, int) x,y tuple representing starting positions
            'team2_starting': (int, int) "

    Raises: ValueError if file is incorrect format
    """
    with open(filename, 'r') as file:
        lines = file.readlines()

    file_data = {}
    try:
        file_data['map'] = []
        file_data['team1_starting'] = {}
        file_data['team2_starting'] = {}
        for y, string in enumerate(lines):
            line = []
            for x, c in enumerate(string.strip()):
                if c in NORTH_SYMS:
                    file_data['team1_starting'][c] = (x, y)
                elif c in SOUTH_SYMS:
                    file_data['team2_starting'][c] = (x, y)
                line.append(c)
            file_data['map'].append(line)
    except:
        raise ValueError("Error loading save file: incorrect format")

    return file_data

def place_obstacles(matrix, num_obstacles):
    """Place several vertical and horizontal barriers randomly in matrix."""
    rows = len(matrix[0])
    cols = len(matrix)
    remaining_obstacles = num_obstacles
    while remaining_obstacles > 0: # place obstacles (including mirror image)
        pick_x = random.randrange(2, (cols - 3)) # don't place on left or right sides
        pick_y = random.randrange(3, (rows - 4)) # don't place in top two or bottom two rows
        if matrix[pick_x][pick_y].is_empty():
            direction = random.randrange(0, 1) # 0 is horizontal, 1 is vertical
            length = random.randrange(1, 5) # length of obstacle
            if direction == 0: # horizontal obstacle
                for x in range(length):
                    if pick_x < cols/2: # left half of screen
                        matrix[pick_x][pick_y].wall = True
                        matrix[cols-pick_x-1-x][rows-pick_y-1].wall = True
                    else: # right half of screen
                        matrix[pick_x-x][pick_y].wall = True
                        matrix[cols-pick_x-1+x][rows-pick_y-1].wall = True
            else: # direction == 1, vertical obstacle
                for y in range(length):
                    if pick_y < rows/2: # top half of screen
                        matrix[pick_x][pick_y+y].wall = True
                        matrix[cols-pick_x-1][rows-pick_y-1-y].wall = True
                    else: # bottom half of screen
                        matrix[pick_x][pick_y-y].wall = True
                        matrix[cols-pick_x-1][rows-pick_y-1+y].wall = True
            remaining_obstacles -= 1

def place_food(matrix, amount_food):
    """Place ints representing food piles randomly in matrix."""
    rows = len(matrix[0])
    cols = len(matrix)
    remaining_food = amount_food
    while remaining_food > 0: # place food (including mirror image)
        pick_x = random.randrange(1, cols - 1)
        pick_y = random.randrange(2, rows - 3) # Don't place in top or bottom row
        if matrix[pick_x][pick_y].is_empty():
            pile = random.randrange(1,9)
            matrix[pick_x][pick_y].food = pile
            matrix[cols-pick_x-1][rows-pick_y-1].food = pile
            remaining_food -= 1
            
def place_ants(matrix, ants):
    """Put corresponding number for each live ant at x,y location in matrix."""
    for a in ants:
        if a.alive:
            matrix[a.x][a.y].ant = a
        
def initialize_matrix_from_saved(loaded_map):
    new_matrix = [[Cell() for col in loaded_map] for row in loaded_map[0]]
    for x, col in enumerate(loaded_map):
        for y, cell in enumerate(col):
            if cell == "#":
                new_matrix[y][x].wall = True
            elif cell.isdigit():
                new_matrix[y][x].food = int(cell)
            elif cell == "@":
                new_matrix[y][x].anthill = NORTH_HILL
            elif cell == "X":
                new_matrix[y][x].anthill = SOUTH_HILL
    return new_matrix
    
def initialize_matrix_random():
    rows = random.randrange(20,25) # Number of rows
    cols = random.randrange(20,25) # Number of columns
    north_hill = (int((cols-1)/2), 1) # Location of north hill
    south_hill = (cols-(int((cols-1)/2))-1, rows-2) # Location of south hill

    matrix = [[Cell() for i in range(rows)] for j in range(cols)]

    # Surround with walls
    for i in range(rows):
        matrix[0][i].wall = True
        matrix[cols-1][i].wall = True
    for i in range(cols):
        matrix[i][0].wall = True
        matrix[i][rows-1].wall = True

    # Place hills, obstacles, food
    matrix[north_hill[0]][north_hill[1]].anthill = NORTH_HILL
    matrix[south_hill[0]][south_hill[1]].anthill = SOUTH_HILL
    place_obstacles(matrix, NUM_OBSTACLES)
    place_food(matrix, AMOUNT_FOOD)

    return matrix

def construct_map(config):
    """Construct matrix and initialize ants"""
    if config['load_map']:
        try:
            file_data = load_save_file(config['save_file'])
        except ValueError as e:
            print(e)
            if DEBUG:
                print(traceback.format_exc())
            print("Randomly generating new map")
            config['load_map'] = False

    if config['load_map']:
        loaded_map = file_data['map']
        matrix = initialize_matrix_from_saved(loaded_map)
        team1_starting = file_data['team1_starting']
        team2_starting = file_data['team2_starting']
    else:
        matrix = initialize_matrix_random()
        cols = len(matrix)
        rows = len(matrix[0])
        team1_starting = {'A': (3,1), 'B': (6,1), 'C': (cols-7,1), 'D': (cols-4,1)}
        team2_starting = {'E': (3,rows-2), 'F': (6,rows-2), 'G': (cols-7,rows-2), 'H': (cols-4,rows-2)}

    initialize_ants(team1, team1_starting, team2, team2_starting, len(matrix), len(matrix[0]))
    place_ants(matrix, ants)
    return matrix

def matrix_to_str_list(matrix):
    out = []
    for row in range(len(matrix[0])):
        output = ""
        for col in range(len(matrix)):
            output += matrix[col][row].print_cell()
        out.append(output)
    return out

def print_map(matrix):
    """Print an ascii rendering of the map.

    If multiple items occupy the same
    cell, only print the last one (prioritizes things that move (ants))
    """
    for line in matrix_to_str_list(matrix):
        print(line)

def generate_vision(matrix, x, y):
    """Return a 3x3 matrix representing the area surrounding x,y in the matrix.
    
    Assumes x & y are inside the outer walls.
    """
    vision = []
    for j in range(x-1, x+2):
        row = []
        for i in range(y-1, y+2):
            row.append(matrix[j][i].print_cell())
        vision.append(row)
    return vision

def kill_ant(ant):
    ant.die()
    matrix[ant.x][ant.y].ant = None

# Thread/Process Mains
def get_move_main(ant, matrix):
    """Thread main for getting ant's next move.
    
    Returns an array of strings representing move. Performs basic input 
    validation by checking move's type and length. May raise ValueError.
    """
    move = ant.act(generate_vision(matrix, ant.x, ant.y))
    if type(move) == str:
        split_move = move.split()
        if len(split_move) < 1 or len(split_move) > 2:
            raise ValueError("Move too long or too short. Recieved: " + str(move))
        return split_move
    else:
        raise ValueError("Move should be of type string. Recieved: " + str(move))

def game_loop(matrix, ants, config):
    """Run game with initialized matrix and ants."""
    team1_points = 0
    team2_points = 0
    team1_ahead = 0
    team2_ahead = 0
    team1_messages = []
    team2_messages = []
    
    game_output = f"SIZE {len(matrix[0])} {len(matrix)}\n"
    
    pool = ThreadPoolExecutor() # Can impose limits on number of threads
    
    transform_xy = { "NORTH": lambda x, y: (x, y-1),
                    "SOUTH": lambda x, y: (x, y+1),
                    "EAST": lambda x, y: (x+1, y),
                    "WEST": lambda x, y: (x-1, y),
                    "NORTHEAST": lambda x, y: (x+1, y-1),
                    "SOUTHEAST": lambda x, y: (x+1, y+1),
                    "SOUTHWEST": lambda x, y: (x-1, y+1),
                    "NORTHWEST": lambda x, y: (x-1, y-1),
                    "HERE": lambda x, y: (x, y) }

    if not config['fast_forward']:
        print("Press enter to execute next round")

    print_map(matrix)
    for lap in range(200):
        if not config['fast_forward']:
            input()

        # Pass messages to ants and clear buffers
        for a in ants:
            try:
                a.send(team1_messages if a.team == 1 else team2_messages)
            except Exception as e:
                print("Error in " + str(a) + " when receiving messages: " + str(e))
                if DEBUG:
                    print(traceback.format_exc())
                kill_ant(a)
        team1_messages = []
        team2_messages = []

        # Prompt ants for next move
        moves = {}
        ants[:] = [a for a in ants if a.alive] # Remove the dead ants
        futures = [pool.submit(get_move_main, a, matrix) for a in ants]
        for a, future in zip(ants, futures):
            try:
                moves[a] = future.result(timeout=0.1)
            except TimeoutError:
                print("Timeout waiting for one_step in " + str(a))
                kill_ant(a)
            except Exception as e:
                print("Error in one_step in " + str(a) + ": " + str(e))
                if DEBUG:
                    print(traceback.format_exc())
                kill_ant(a)

        # Parse moves
        proposed_moves = {}
        proposed_gets = {}
        for a, move in moves.items():
            loc = (a.x, a.y)
            
            # Cardinal movement
            if move[0] in transform_xy and len(move) == 1:
                new_loc = transform_xy[move[0]](loc[0], loc[1])
                if is_open_cell(matrix, new_loc[0], new_loc[1]):
                    loc = new_loc

            elif move[0] == "GET":
                if len(move) != 2 or move[1] not in transform_xy:
                    print("Invalid GET in " + a.symbol + ": " + str(move))
                    kill_ant(a)
                    continue
                elif not a.food: # Can't carry more than one!
                    target_x, target_y = transform_xy[move[1]](a.x, a.y)
                    if is_open_cell(matrix, target_x, target_y):
                        if (target_x, target_y) in proposed_gets:
                            proposed_gets[(target_x, target_y)].append(a)
                        else:
                            proposed_gets[(target_x, target_y)] = [a]

            elif move[0] == "DROP":
                if len(move) != 2 or move[1] not in transform_xy:
                    print("Invalid DROP in " + a.symbol + ": " + str(move))
                    kill_ant(a)
                    continue
                elif a.food:
                    target_x, target_y = transform_xy[move[1]](a.x, a.y)
                    if is_open_cell(matrix, target_x, target_y):
                        a.food = False
                        cell = matrix[target_x][target_y]
                        if cell.anthill:
                            if cell.anthill == NORTH_HILL:
                                team1_points += 1
                            elif cell.anthill == SOUTH_HILL:
                                team2_points += 1

                        else:
                            cell.food += 1

            elif move[0] != "PASS":
                print("Invalid move from " + a.symbol + ": " + str(move))
                kill_ant(a)
                continue

            # Attempt to place this ant in next phase of simulation. Ants in conflict must go back
            if loc not in proposed_moves:
                proposed_moves[loc] = a
            else:
                conflict_ant = proposed_moves[loc]

                # Return this ant to original position, resolving any chains of conflicts
                proposed_moves[loc] = None # No one gets to be here
                current_ant = a
                while current_ant and (current_ant.x, current_ant.y) in proposed_moves and proposed_moves[(current_ant.x, current_ant.y)]:
                    next_current_ant = proposed_moves[(current_ant.x, current_ant.y)]
                    proposed_moves[(current_ant.x, current_ant.y)] = current_ant
                    current_ant = next_current_ant
                else:
                    if current_ant:
                        proposed_moves[(current_ant.x, current_ant.y)] = current_ant

                # Return conflicting ant to original position, resolving conflicts
                while conflict_ant and (conflict_ant.x, conflict_ant.y) in proposed_moves and proposed_moves[(conflict_ant.x, conflict_ant.y)]:
                    next_conflict_ant = proposed_moves[(conflict_ant.x, conflict_ant.y)]
                    proposed_moves[(conflict_ant.x, conflict_ant.y)] = conflict_ant
                    conflict_ant = next_conflict_ant
                else:
                    if conflict_ant:
                        proposed_moves[(conflict_ant.x, conflict_ant.y)] = conflict_ant

        # Resolve proposed gets
        for (target_x, target_y), aList in proposed_gets.items():
            if matrix[target_x][target_y].food > 0 and matrix[target_x][target_y].food >= len(aList): #here
                for a in aList:
                    a.food = True
                matrix[target_x][target_y].food -= len(aList)

        # Update arena & redraw screen
        for loc, a in proposed_moves.items():
            if a: # May be none if it was the site of a movement conflict
                matrix[a.x][a.y].ant = None
                a.x = loc[0]
                a.y = loc[1]

        place_ants(matrix, ants)
        print_map(matrix)
        print("Round:", lap, "Team 1:", str(team1_points), "Team 2:", str(team2_points))
        if team1_points > team2_points:
            team1_ahead += 1
        elif team2_points > team1_points:
            team2_ahead += 1
        
        # Add this round to an output string
        game_output += (
            f"==============================\n"
            f"ROUND {lap}\n"
            f"NORTH {team1_points}\n"
            f"SOUTH {team2_points}\n"
            f"=========================\n"
        )
        gameOutput += ''.join(f'{line}\n' for line in matrixToStrList(matrix))

        # Receive messages from ants from this round
        for a in ants:
            if a.alive:
                try:
                    msgs = a.recv()
                    if type(msgs) != list:
                        raise ValueError("Messages should be of type list.")
                except Exception as e:
                    print("Error in " + a.symbol + " when sending messages: " + str(e))
                    if DEBUG:
                        print(traceback.format_exc())
                    kill_ant(a)
                    continue

                if a.team == 1:
                    team1_messages += msgs
                elif a.team == 2:
                    team2_messages += msgs

        ants[:] = [a for a in ants if a.alive] # Remove the dead ants
        
    game_output += "==============================\n"

    pool.shutdown()
    print("\n==== Final score ====\nTeam 1: " + str(team1_points) + " Team 2 : " + str(team2_points))
    if team1_points > team2_points:
        print("Winner: Team 1")
        game_output += "WINNER NORTH\n"
    elif team2_points > team1_points:
        print("Winner: Team 2")
        game_output += "WINNER SOUTH\n"
    elif team1_ahead > team2_ahead:
        print("Winner: Team 1")
        game_output += "WINNER NORTH\n"
    elif team2_ahead > team1_ahead:
        print("Winner: Team 2")
        game_output += "WINNER SOUTH\n"
    else:
        print("Winner: Tie")
        game_output += "WINNER TIE\n"

    # Prompt user to save full game output
    save = input("Save game output? (yes/<enter>) ")
    if save.upper() == "YES":
        filename = input("Enter filename: ")
        with open(filename, "w+") as outfile:
            outfile.write(game_output)

def prompt_save_map(initial_matrix):
    """Prompt user to save map for a future game"""
    save = input("Save map? (yes/<enter>) ")
    if save.upper() == "YES":
        filename = input("Enter filename: ")
        with open(filename, "w+") as outfile:
            for line in initial_matrix:
                outfile.write(line + "\n")

# Ensure that only 'main' process/thread can execute this
if __name__ == '__main__':
    random.seed()
    ants = []
    config = generate_game_config()
    matrix = construct_map(config)
    initial_matrix = matrix_to_str_list(matrix)
    game_loop(matrix, ants, config)
    prompt_save_map(initial_matrix)
