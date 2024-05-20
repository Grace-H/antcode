max_x, max_y = [int(i) for i in input().split()]

 # Direction ant is currently traveling
direction = "WEST"

# Game loop
while True:
    x, y = [int(i) for i in input().split()]

    if direction == "EAST":
        if x < max_x:
            print(direction)
        else:
            direction = "WEST"
            print(direction)
    elif direction == "WEST":
        if x > 0:
            print(direction)
        else:
            direction = "EAST"
            print(direction)
