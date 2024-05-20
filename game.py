#!/usr/bin/env python3.11

import sys, pygame, math, random
from subprocess import Popen, PIPE

# World building/game appearence
pygame.init()
screen_size = screen_width, screen_height = 600, 400
screen = pygame.display.set_mode(screen_size)
background = 198, 146, 87

# Game state constants
grid_size = grid_width, grid_height = 30, 20 # Ideally a factor of screen dimensions
unit_size = unit_width, unit_height = screen_width // grid_width, screen_height // grid_height
directions = { "EAST": [1, 0], "WEST": [-1, 0], "NORTH": [0, -1], "SOUTH": [0, 1] }

# Ant state
ant = pygame.image.load("img/ant.png")
ant_rect = ant.get_rect()
ant_rect.move(random.randint(0, grid_width) * unit_width, random.randint(0, grid_height) * unit_height)

ant_file = "ant-horizontal.py"
try:
    ant_proc = Popen(["python3", ant_file], stdin=PIPE, stdout=PIPE, text=True)
    ant_proc.stdin.write(str(grid_width) + " " + str(grid_height) + "\n")
    ant_proc.stdin.flush()
except Exception as e:
    print(e)
    sys.exit(status=1)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.quit: sys.exit()

    # Prompt for ant move
    move = "PASS"
    try:
        ant_proc.stdin.write(str(ant_rect.topleft[0] // unit_width) + 
                             " " + str(ant_rect.topleft[1] // unit_height) + "\n")
        ant_proc.stdin.flush()
        move = ant_proc.stdout.readline().strip()
    except Exception as e:
        print(e)
        break

    # Move more smoothly by moving one pixel at a time
    if move in directions:
        for i in range(max(abs(directions[move][0]) * unit_width, abs(directions[move][1]) * unit_height)):
            ant_rect = ant_rect.move(directions[move])
            screen.fill(background)
            screen.blit(ant, ant_rect)
            pygame.display.flip()

# Clean up
ant_proc.kill()
