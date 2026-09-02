#This is in custom shapes, should live there or here?????
from shapebuilders.shapes import Shapes

# Vectors to represent allignment
_VECTORS = {
    "north": (0, 0, -1),
    "south": (0, 0, 1),
    "east": (1, 0, 0),
    "west": (-1, 0, 0)
}

BUILDERS = {
    "triangle": lambda p: Shapes.triangle(p.size, _VECTORS[p.orientation], p.ox, p.oy, p.oz, p.bid)
}