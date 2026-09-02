import uuid

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Union, Literal, Annotated

# -------- exceptions ------
class BuildBusyError(Exception):
    pass

# ------ geometry --------

class Orientation(str, Enum):
    north = "north"
    south = "south"
    east = "east"
    west = "west"

class Block(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["block"] = "block"
    x: int = Field(ge=0, description="X coordinate to place the block")
    y: int = Field(ge=0, description="Y coordinate to place the block")
    z: int = Field(ge=0, description="Z coordinate to place the block")
    bid: int | str = Field(description="Block type ID (e.g. 0=air, 1=stone, 2=grass etc...)")

class BlockInfo(BaseModel):
    id: str = Field(description="Block ID to pass as 'bid' when building")
    name: str = Field(description="Human readable block name")

# ------ requests --------

class CuboidBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["cuboid"]
    x1: int = Field(ge=0, description="First x coordinate, along with x2 provides the length of the cuboid in the x plane")
    y1: int = Field(ge=0, description="First y coordinate, along with y2 provides the length of the cuboid in the y plane")
    z1: int = Field(ge=0, description="First z coordinate, along with z2 provides the length of the cuboid in the z plane")
    x2: int = Field(ge=0, description="Second x coordinate, along with x1 provides the length of the cuboid in the x plane")
    y2: int = Field(ge=0, description="Second y coordinate, along with y1 provides the length of the cuboid in the y plane")
    z2: int = Field(ge=0, description="Second z coordinate, along with z1 provides the length of the cuboid in the z plane")
    bid: str = Field(description="Block type ID (e.g. 0=air, 1=stone, 2=grass etc...)")

class WallBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["wall"]
    length: int = Field(gt=0, description="Length of the wall in horizontal plane")
    height: int = Field(gt=0, description="Height of the wall in the vertical plane")
    orientation: Orientation = Field(description="Compass direction the shape faces: north (-z), south (+z), east (+x), west (-x)")
    ox: int = Field(ge=0, description="X coordinate for the origin of the wall")
    oy: int = Field(ge=0, description="Y coordinate for the origin of the wall")
    oz: int = Field(ge=0, description="Z coordinate for the origin of the wall")
    bid: str = Field(description="Block type ID (e.g. 0=air, 1=stone, 2=grass etc...)")

class EmptyCuboidBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["emptyCuboid"]
    xlength: int = Field(gt=0, description="Length of the empty cuboid in the x plane")
    zlength: int = Field(gt=0, description="length of the empty cuboid in the z plane")
    height: int = Field(gt=0, description="Total height in the y plane of the empty cuboid")
    ox: int = Field(ge=0, description="X coordinate for the origin of the empty cuboid")
    oy: int = Field(ge=0, description="Y coordinate for the origin of the empty cuboid")
    oz: int = Field(ge=0, description="Z coordinate for the origin of the empty cuboid")
    bid: str = Field(description="Block type ID (e.g. 0=air, 1=stone, 2=grass etc...)")

class FloorBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["floor"]
    x1: int = Field(ge=0, description="First x coordinate, along with x2 provides the length of the floor in the x plane")
    y: int = Field(ge=0, description="Y coordinate, sets the height the floor is placed at")
    z1: int = Field(ge=0, description="First z coordinate, along with z2 provides the length of the floor in the z plane")
    x2: int = Field(ge=0, description="Second x coordinate, along with x1 provides the length of the floor in the x plane")    
    z2: int = Field(ge=0, description="Second z coordinate, along with z1 provides the length of the floor in the z plane")
    bid: str = Field(description="Block type ID (e.g. 0=air, 1=stone, 2=grass etc...)")

class TriangleBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["triangle"]
    size: int = Field(ge=3, description="Length of the base of the triangle")
    orientation: Orientation = Field(description="Compass direction the shape faces: north (-z), south (+z), east (+x), west (-x)")
    ox: int = Field(ge=0, description="X coordinate for the origin of the triangle")
    oy: int = Field(ge=0, description="Y coordinate for the origin of the triangle")
    oz: int = Field(ge=0, description="Z coordinate for the origin of the triangle")
    bid: str = Field(description="Block type ID (e.g. 0=air, 1=stone, 2=grass etc...)")

class SlopeBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["slope"]
    length: int = Field(gt=0, description="Length of the slope in horizontal plane")
    height: int = Field(gt=0, description="Height of the slope in the vertical plane")
    orientation: Orientation = Field(description="Compass direction the shape faces: north (-z), south (+z), east (+x), west (-x)")
    ox: int = Field(ge=0, description="X coordinate for the origin of the slope")
    oy: int = Field(ge=0, description="Y coordinate for the origin of the slope")
    oz: int = Field(ge=0, description="Z coordinate for the origin of the slope")
    bid: str = Field(description="Block type ID (e.g. 0=air, 1=stone, 2=grass etc...)")

class PyramidBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["pyramid"]
    size: int = Field(ge=3)
    ox: int = Field(ge=0, description="X coordinate for the origin of the pyramid")
    oy: int = Field(ge=0, description="Y coordinate for the origin of the pyramid")
    oz: int = Field(ge=0, description="Z coordinate for the origin of the pyramid")
    bid: str = Field(description="Block type ID (e.g. 0=air, 1=stone, 2=grass etc...)")

# To implement
#class SphereBody(BaseModel):
#    model_config = ConfigDict(extra="forbid")
#    type: Literal["sphere"]
#    x: int
#    y: int
#    z: int
#    radius: int
#    bid: str

#Batch

ShapeSpec = Union [Block, CuboidBody, WallBody, EmptyCuboidBody, FloorBody, TriangleBody, SlopeBody, PyramidBody]

class BuildBatch(BaseModel):
    """
    Annotated [T. x], adds metadata x to type T, in this case adds the shape type text to the ShapeSpec type
    """
    shapes: list[Annotated[ShapeSpec, Field(discriminator="type")]]

# ------ responses --------
class BuildResult(BaseModel):
    type: list[str] = Field(description="THe shape types that were built, in order.")
    queued: int = Field(description="Total blocks queued accepted for placement.")
    dropped: int = Field(description="Blocks not placed due to being of of the map bounds.")
    kept: int = Field(description="Blocks placed after removing blocks outside of the map bounds.")
    build_id: uuid.UUID = Field(description="Unique ID for the build")
 
class UndoResult(BaseModel):
    build_id: uuid.UUID = Field(description="Unique ID for the build")
    blocks_restored: int = Field(description="Total blocks restored")
 
class MapResult(BaseModel):
    width: int = Field(description="Map size in the x plane")
    height: int = Field(description="Map size in the y plane")
    length: int = Field(description="Mapp size in the z plane")

class PaletteResult(BaseModel):
    source: str = Field(description="Which palette file is being used")
    count: int = Field(description="Number of available block types")
    blocks: list[BlockInfo] = Field(description="All block types available to build with as id/name pairs")