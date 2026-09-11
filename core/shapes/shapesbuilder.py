# Vectors to represent allignment
from core.shapes.schemas import Block


_VECTORS = {
    "north": (0, 0, -1),
    "south": (0, 0, 1),
    "east": (1, 0, 0),
    "west": (-1, 0, 0)
}

BUILDERS = {
    "block": lambda p: [Block(x=x,y=y,z=z,bid=b) for (x,y,z,b) in Shapes.block(p.x, p.y, p.z, p.bid)],
    "cuboid": lambda p: [Block(x=x,y=y,z=z,bid=b) for (x,y,z,b) in Shapes.cuboid(p.x1, p.y1, p.z1, p.x2, p.y2, p.z2, p.bid)],
    "wall": lambda p: [Block(x=x,y=y,z=z,bid=b) for (x,y,z,b) in Shapes.wall(p.length, p.height, _VECTORS[p.orientation], p.ox, p.oy, p.oz, p.bid)],
    "emptyCuboid": lambda p: [Block(x=x,y=y,z=z,bid=b) for (x,y,z,b) in Shapes.emptyCuboid(p.xlength, p.zlength, p.height, p.ox, p.oy, p.oz, p.bid)],
    "floor": lambda p: [Block(x=x,y=y,z=z,bid=b) for (x,y,z,b) in Shapes.floor(p.x1, p.y, p.z1, p.x2, p.z2, p.bid)],
    "triangle": lambda p: [Block(x=x,y=y,z=z,bid=b) for (x,y,z,b) in Shapes.triangle(p.size, _VECTORS[p.orientation], p.ox, p.oy, p.oz, p.bid)],
    "slope": lambda p: [Block(x=x,y=y,z=z,bid=b) for (x,y,z,b) in Shapes.slope(p.length, p.height, _VECTORS[p.orientation], p.ox, p.oy, p.oz, p.bid)],    
    "pyramid": lambda p: [Block(x=x,y=y,z=z,bid=b) for (x,y,z,b) in Shapes.pyramid(p.size, p.ox, p.oy, p.oz, p.bid)]
}

class Shapes:

    @staticmethod
    def block(x: int, y: int, z: int, bid: int) -> list[tuple]:
        """
        Creates a single block shape at the specified coordinates (x, y, z) with the given block type ID (bid).
        """
        coords = []
        coords.append((x, y, z, bid))
        return coords
    
    @staticmethod
    def cuboid(x1, y1, z1, x2, y2, z2, bid) -> list[tuple]:
        """
        Creates a cuboid shape with the specified dimensions.
        The cuboid is built from the first coordinate (x1, y1, z1) to the second coordinate (x2, y2, z2).        
        """
        ax, ay, az = min(x1, x2), min(y1, y2), min(z1, z2)
        bx, by, bz = max(x1, x2), max(y1, y2), max(z1, z2)

        coords = []

        for x in range(ax, bx + 1):
            for y in range(ay, by + 1):
                for z in range(az, bz + 1):
                    coords.append((x, y, z, bid))
        return coords

    @staticmethod
    def wall(length, height, orientation, ox, oy, oz, bid) -> list[tuple]:
        """
        Creates a wall shape with the specified dimensions and orientation.
        NORTH = (0, 0, -1)
        SOUTH = (0, 0,  1)
        EAST  = (1, 0,  0)
        WEST  = (-1, 0, 0)

        e.g. for North wall, orientation = (0, 0, -1) 
        dx = 0, dy = 0, dz = -1        
        the wall will extend in a negative x direction from the origin ox, oy, oz. The wall will be built upwards in the y direction to the specified height.
        """
        dx, _, dz = orientation # Unpack the orientation tuple into dx, dy, dz
        
        coords = []
        
        for y in range(0, height): # steps up y
            for l in range(0, length): # width of the slope
                x = ox + (l * dx)
                z = oz + (l * dz)
                coords.append((x, oy + y, z, bid))
        return coords 

    @staticmethod
    def emptyCuboid(xlength, zlength, height, ox, oy, oz, bid) -> list[tuple]:
        """
        Creates an empty cuboid shape with the specified dimensions.
        The empty cuboid is hollow, with walls of 1 block thickness. The origin (ox, oy, oz) is one of the corners of the cuboid. 
        The cuboid is built upwards in the y direction, to the specified height. The xlength and zlength specify the length of the cuboid in the x and z planes respectively.
        """
        coords = Shapes.wall(xlength,height,_VECTORS["east"],ox,oy,oz,bid) + \
        Shapes.wall(xlength,height,_VECTORS["east"],ox,oy,oz+zlength-1,bid) + \
        Shapes.wall(zlength-2,height,_VECTORS["south"],ox,oy,oz+1,bid) + \
        Shapes.wall(zlength-2,height,_VECTORS["south"],ox+xlength-1,oy,oz+1,bid)

        return coords

    @staticmethod
    def pyramid(size, ox, oy, oz, bid) -> list[tuple]:
        """
        Creates a pyramid shape with the specified dimensions.
        Size is the length of the base of the pyramid. The pyramid starts at the origin (ox, oy, oz) and this is one of the corners of the base. 
        The pyramid is built upwards in the y direction, with each level being a smaller square than the one below it.
        If the pyramid has an odd size, the top level will be a single block. If the pyramid has an even size, the top level will be a 2x2 square.
        """
        coords = []
        for y in range(0, size // 2):
            levelsize = size - (y * 2)
            coords.extend(Shapes.emptyCuboid(levelsize, levelsize, 1, ox+y, oy+y, oz+y, bid))

        if size % 2 != 0:
            mid = size // 2 
            coords.extend(Shapes.block(x=ox+mid, y=oy+mid, z=ox+mid, bid=bid))
        
        return coords
    
    @staticmethod
    def floor(x1, y, z1, x2, z2, bid) -> list[tuple]:
        """
        Creates a floor shape with the specified dimensions.
        The floor is built from the first coordinate (x1, y, z1) to the second coordinate (x2, y, z2).
        The floor is a flat surface with a thickness of 1 block. The y coordinate specifies the height at which the floor is placed.
        """
        return Shapes.cuboid(x1, y, z1, x2, y, z2, bid )

    @staticmethod
    def triangle(size, orientation, ox, oy, oz, bid) -> list[tuple]:        
        """
        Creates a triangular shape with the specified dimensions and orientation.
        NORTH = (0, 0, -1)
        SOUTH = (0, 0,  1)
        EAST  = (1, 0,  0)
        WEST  = (-1, 0, 0)

        e.g. for north triangle, orientation = (0, 0, -1)
        dx = 0, dy = 0, dz = -1        
        """            
        coords = []        

        dx, _, dz = orientation # Unpack the orientation tuple into dx, dy, dz

        for i in range(0, -(-size//2)):  # Ceiling division, calculates number of levels
            for j in range(0, size - (i * 2)):
                x = ox + (dx * i) + (dx * j)
                z = oz + (dz * i) + (dz * j)
                coords.append((x, oy + i, z, bid))        
        return coords    

    @staticmethod    
    def slope(length, height, orientation, ox, oy, oz, bid) -> list[tuple]:
        """
        Creates a sloped shape with the specified dimensions and orientation.
        NORTH = (0, 0, -1)
        SOUTH = (0, 0,  1)
        EAST  = (1, 0,  0)
        WEST  = (-1, 0, 0)

        e.g. for North slope, orientation = (0, 0, -1)
        dx = 0, dy = 0, dz = -1
        px = 1, pz = 0 (perpendicular direction for the slope), therefore the slope will go in the x direction as it goes up in y and z.
        """
        dx, _, dz = orientation # Unpack the orientation tuple into dx, dy, dz
        px, pz = -dz, dx  # Perpendicular direction for the slope

        coords = []
        
        for i in range(0, height): # steps up y
            for j in range(0, length): # width of the slope
                x = ox + (i * dx) + (j * px)
                z = oz + (i * dz) + (j * pz)
                coords.append((x, oy + i, z, bid))
        return coords