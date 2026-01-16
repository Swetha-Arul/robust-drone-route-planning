from .grid import GridMap, Position

def add_cuboid_no_fly_zone(
    env: GridMap,
    min_corner: Position,
    max_corner: Position
):
    x1, y1, z1 = min_corner
    x2, y2, z2 = max_corner

    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                env.add_no_fly_zone((x, y, z))
