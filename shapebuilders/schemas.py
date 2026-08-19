from pydantic import BaseModel, Field
from enum import Enum
from typing import Union, Literal, Annotated

# ------ geometry --------

class Orientation(str, Enum):
    north = "north"
    south = "south"
    east = "east"
    west = "west"

class Block(BaseModel):
    type: Literal["block"]
    x: int
    y: int
    z: int
    bid: int

# ------ requests --------

class CuboidBody(BaseModel):
    type: Literal["cuboid"]
    x1: int
    y1: int
    z1: int
    x2: int
    y2: int
    z2: int
    bid: int

class WallBody(BaseModel):
    type: Literal["wall"]
    length: int
    height: int
    orientation: Orientation
    ox: int
    oy: int
    oz: int
    bid: int

class EmptyCuboidBody(BaseModel):
    type: Literal["emptyCuboid"]
    xlength: int
    zlength: int
    height: int    
    ox: int
    oy: int
    oz: int
    bid: int

class FloorBody(BaseModel):
    type: Literal["floor"]
    x1: int
    y: int
    z1: int
    x2: int
    z2: int
    bid: int

class TriangleBody(BaseModel):
    type: Literal["triangle"]
    size: int
    orientation: Orientation
    ox: int
    oy: int
    oz: int
    bid: int

class SlopeBody(BaseModel):
    type: Literal["slope"]
    length: int
    height: int
    orientation: Orientation
    ox: int
    oy: int
    oz: int
    bid: int

class PyramidBody(BaseModel):
    type: Literal["pyramid"]
    size: int
    ox: int
    oy: int
    oz: int
    bid: int

# To implement
class SphereBody(BaseModel):
    type: Literal["sphere"]
    x: int
    y: int
    z: int
    radius: int
    bid: int

#Batch

ShapeSpec = Union [Block, CuboidBody, WallBody, EmptyCuboidBody, FloorBody, TriangleBody, SlopeBody, SphereBody, PyramidBody ]

class BuildBatch(BaseModel):
    """
    Annotated [T. x], adds metadata x to type T, in this case adds the type text to the ShapeSpec type
    """
    shapes: list[Annotated[ShapeSpec, Field(discriminator="type")]]

# ------ responses --------
class QueueResult(BaseModel):
    queued: int
    dropped: int
    pending: int
 
class ExecuteResult(BaseModel):
    executing: int
 
class StatusResult(BaseModel):
    pending: int