from fastmcp import FastMCP
from core.factories.build_factory import BuildFactory

mcp = FastMCP("Minecraft Buildbot")

service = BuildFactory.create_shape_builder()

@mcp.tool()
def build(shapes: List[ShapeSpec]) -> dict:
    """

    """
    return service.build(shapes)

@mcp.resource()
def block_ids() -> dict:
    """
    The available block Ids and their description
    """
    return service.palette.as_dict()