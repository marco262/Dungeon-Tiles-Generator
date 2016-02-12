"""
Steps to create the map
Load all images into a list
Create rotations of each room tile (no reflections needed)
Define grid (m x n)
Define borders of grid (Top border is closed, left border is open, etc)
Starting with the top row, randomly pick a tile to place in each location, checking to make sure it fits with all
    previously placed tiles.
If any tile cannot fit at all, scrap the whole maze and start again.
"""

from PIL import Image
import random

# Define the sides of a tile
TOP, RIGHT, BOTTOM, LEFT = range(4)

GRID_WIDTH = 5
GRID_HEIGHT = 5

# Define the different states a side can be in.
# Undefined means a tile hasn't yet been placed in that spot
# Hallway means an open space in the middle with a wall on each side
# LEFT_WALL means an open side with a wall only on the counter-clockwise side. e.g. top of the Room Corner tile
# RIGHT_WALL means an open side with a wall only on the clockwise side. e.g. left edge of the Room Corner tile
# All sides will pair up with like sides. Except the walls, which will pair up with each other only
UNDEFINED, CLOSED, HALLWAY, LEFT_WALL, RIGHT_WALL, OPEN = range(6)

# All edges of the grid must be defined with a type of side
# To allow any tile against an edge, that edge should be UNDEFINED
TOP_EDGE = CLOSED
RIGHT_EDGE = CLOSED
BOTTOM_EDGE = CLOSED
LEFT_EDGE = CLOSED

class Tile(object):

    filepath = ""
    image = None
    sides = ()
    rotation = 0

    def __init__(self, filepath, sides, image=None, rotation=0):
        self.filepath = filepath
        self.sides = sides
        if image is None:
            self.image = Image.open(filepath)
        else:
            self.image = image
        self.rotation = rotation

    def rotate_copy(self, rotation):
        """
        Returns a rotated copy of this tile
        :param rotation: 90, 180, or 270
        :return: Tile() object
        """
        if rotation not in (90, 180, 270):
            raise NotImplementedError
        if rotation == 90:
            new_sides = self.sides[3:] + self.sides[:3]
        if rotation == 180:
            new_sides = self.sides[2:] + self.sides[:2]
        else:
            new_sides = self.sides[1:] + self.sides[:1]
        return Tile(self.filepath, new_sides, self.image.rotate(rotation),
                    rotation=self.rotation + rotation)

    def get_image(self):
        return self.image

    def show(self):
        self.image.show()

    def get_size(self):
        return self.image.size

    def __str__(self):
        num = self.filepath.split('/')[-1][:2]
        return num + {0: 'A', 90: 'B', 180: 'C', 270: 'D'}.get(self.rotation)

    def __repr__(self):
        return "Tile(filepath={!r}, sides={!r}, rotation={!r})".format(self.filepath, self.sides, self.rotation)

    def get_side(self, side):
        """
        Returns the type of side (e.g. CLOSED, HALLWAY) based on the side given (e.g. TOP, RIGHT)
        :param side: TOP, RIGHT, BOTTOM, or LEFT
        :type side: int
        :return: int
        """
        return self.sides[side]

    def get_opposite_side(self, side):
        return self.sides[(side + 2) % len(self.sides)]


def main():
    tiles_list = build_tiles()
    grid = build_grid()
    for y, row in enumerate(grid):
        for x, space in enumerate(row):
            print "Grid pos:", y, x
            tile = pick_tile_for_space(grid, x, y, tiles_list)
            print "Chosen tile:", tile
            grid[y][x] = tile

    print_grid(grid)
    bg = build_final_image(grid)
    bg.show()

def build_final_image(grid):
    """
    Creates an image representing the grid of tiles, laid out appropriately
    :param grid: Grid of Tile() objects
    :return: Image file
    """
    tile_0 = grid[0][0]
    tile_x, tile_y = tile_0.get_size()
    bg = Image.new("RGB", size=(tile_x * GRID_WIDTH, tile_y * GRID_HEIGHT))

    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            bg.paste(tile.get_image(), (tile_x * x, tile_y * y))
    return bg

def print_grid(grid):
    for row in grid:
        print "###",
        for tile in row:
            if tile is not None:
                print tile, "|",
            else:
                print "No", "|",
        print


def print_tiles(tiles_list):
    print "Tiles:", map(str, tiles_list)

def pick_tile_for_space(grid, x, y, tiles_list):
    """
    :param grid:
    :param x:
    :param y:
    :param tiles_list:
    :return:
    """
    # Randomize list of tiles, and then iterate through them to find a match
    rand_tiles = random.sample(tiles_list, len(tiles_list))
    # print_tiles(rand_tiles)
    print_grid(grid)
    for tile in rand_tiles:
        if check_if_tile_fits(grid, x, y, tile):
            # print tile
            return tile
    raise Exception("No fitting tile found")

def check_if_tile_fits(grid, x, y, tile):
    """
    If a tile's sides match all sides of all adjacent tiles, return True
    :param grid:
    :param x:
    :param y:
    :param tile:
    :return:
    """
    return (check_side(tile, grid, x, y, TOP) and
            check_side(tile, grid, x, y, RIGHT) and
            check_side(tile, grid, x, y, BOTTOM) and
            check_side(tile, grid, x, y, LEFT)
            )

def get_adjacent_side(grid, x, y, side):
    """
    Gets the adjacent side type for the given tile on its given side
    E.g. The edge immediately to the left of the given tile may be a HALLWAY, CLOSED, or even UNDEFINED
    :param grid:
    :param x:
    :param y:
    :param side:
    :return:
    """
    if side == TOP:
        if y == 0:
            return TOP_EDGE
        other_tile = grid[y - 1][x]
    elif side == RIGHT:
        try:
            other_tile = grid[y][x + 1]
        except IndexError as e:
            return RIGHT_EDGE
    elif side == BOTTOM:
        try:
            other_tile = grid[y + 1][x]
        except IndexError as e:
            return BOTTOM_EDGE
    elif side == LEFT:
        if x == 0:
            return LEFT_EDGE
        other_tile = grid[y][x - 1]
    else:
        other_tile = None

    if other_tile is None:
        return UNDEFINED

    return other_tile.get_opposite_side(side)

def check_side(my_tile, grid, x, y, side):
    my_side = my_tile.get_side(side)
    other_side = get_adjacent_side(grid, x, y, side)
    # print "Checking {}: {} | {}".format(side, my_side, other_side)
    if other_side == UNDEFINED:
        return True
    if my_side in (CLOSED, HALLWAY, OPEN):
        return my_side == other_side
    return ((my_side == LEFT_WALL and other_side == RIGHT_WALL) or
            (my_side == RIGHT_WALL and other_side == LEFT_WALL)
            )

def build_tiles():
    """
    Builds the list of all possible tile configurations, rotating and copying tiles as needed
    Sides are defined in clockwise order: TOP, RIGHT, BOTTOM, LEFT
    :return: list of Tile() objects
    """
    tiles = [
        Tile("dungeon tiles/01 - Corridor .png", (HALLWAY, HALLWAY, HALLWAY, HALLWAY)),
        Tile("dungeon tiles/02 - Corridor End.png", (CLOSED, CLOSED, HALLWAY, CLOSED))
    ]
    # Create 3 copies of the tile, each rotated 90 degress from the previous
    for i in xrange(3):
        tiles.append(tiles[-1].rotate_copy(90))
    tiles.append(Tile("dungeon tiles/03 - Corridor I.png", (HALLWAY, CLOSED, HALLWAY, CLOSED)))
    tiles.append(tiles[-1].rotate_copy(90))
    tiles.append(Tile("dungeon tiles/04 - Corridor L.png", (CLOSED, HALLWAY, HALLWAY, CLOSED)))
    for i in xrange(3):
        tiles.append(tiles[-1].rotate_copy(90))
    tiles.append(Tile("dungeon tiles/05 - Corridor T.png", (HALLWAY, HALLWAY, HALLWAY, CLOSED)))
    for i in xrange(3):
        tiles.append(tiles[-1].rotate_copy(90))
    tiles.append(Tile("dungeon tiles/06 - Room Corner Inner.png", (LEFT_WALL, OPEN, OPEN, RIGHT_WALL)))
    for i in xrange(3):
        tiles.append(tiles[-1].rotate_copy(90))
    tiles.append(Tile("dungeon tiles/07 - Room Corner.png", (CLOSED, LEFT_WALL, RIGHT_WALL, CLOSED)))
    for i in xrange(3):
        tiles.append(tiles[-1].rotate_copy(90))
    tiles.append(Tile("dungeon tiles/08 - Room Doorway.png", (RIGHT_WALL, HALLWAY, LEFT_WALL, OPEN)))
    for i in xrange(3):
        tiles.append(tiles[-1].rotate_copy(90))
    tiles.append(Tile("dungeon tiles/09 - Room Wall.png", (LEFT_WALL, OPEN, RIGHT_WALL, CLOSED)))
    for i in xrange(3):
        tiles.append(tiles[-1].rotate_copy(90))
    tiles.append(Tile("dungeon tiles/10 - Solid Wall.png", (CLOSED, CLOSED, CLOSED, CLOSED)))
    tiles.append(Tile("dungeon tiles/11 - Solid Floor.png", (OPEN, OPEN, OPEN, OPEN)))
    return tiles

def build_grid():
    """
    Creates a list of lists, a 2D grid based on GRID_WIDTH and GRID_HEIGHT
    Default values in each space is None
    :return: List of lists of None
    """
    return [[None] * GRID_WIDTH for line in xrange(GRID_HEIGHT)]

if __name__ == "__main__":
    main()
