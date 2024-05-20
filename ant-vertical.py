max_x, max_y = [int(i) for i in input().split()]

 # Direction ant is currently traveling
direction = "NORTH"

# Game loop
while True:
    x, y = [int(i) for i in input().split()]

    if direction == "SOUTH":
        if y < max_y:
            print(direction)
        else:
            direction = "NORTH"
            print(direction)
    elif direction == "NORTH":
        if y > 0:
            print(direction)
        else:
            direction = "SOUTH"
            print(direction)
