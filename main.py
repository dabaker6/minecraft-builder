from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

from factories.build_factory import BuildFactory
from buildservices.base import BuildService
from shapebuilders.custom import BUILDERS
from shapebuilders.schemas import BuildBatch, BuildResult, MapResult, UndoResult, BuildBusyError

import uuid

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = BuildFactory.create_shape_builder()
    yield
    app.state.service.close()

app = FastAPI(lifespan=lifespan, title="BuildBot API", description="API for Minecraft Classic BuildBot", version="0.1.0")

def get_service(request: Request) -> BuildService:
    return request.app.state.service

ServiceDep = Annotated[BuildService, Depends(get_service)]

@app.exception_handler(BuildBusyError)
async def build_busy_handler(request: Request, exc: BuildBusyError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(IndexError)
async def no_undo_history_handler(request: Request, exc: IndexError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.post("/build")
def build(body: BuildBatch, service: ServiceDep):
    """
    Build one or more shapes in the Minecraft world.

    Multiple shapes can be sent in one request. These shapes are placed in the order given, as a single build. The world uses
    (x, y, z) coordinates where y is height (up). Coordinates must be within the build zone. 
    
    The size of the map can be obtained through the map tool.
    
    If a build looks wrong, call the undo tool to revert it.
    """
    guid=uuid.uuid4()

    all_blocks = []
    shapes = []
    
    for shape in body.shapes:        
        blocks = BUILDERS[shape.type](shape)
        all_blocks.extend(blocks)
        shapes.append(shape.type)

    kept, dropped = service.build(all_blocks, guid)

    return BuildResult(
        type=shapes,
        queued=len(all_blocks), 
        kept=kept, 
        dropped=dropped,
        build_id=guid
        ) 

@app.post("/undo")
def undo(service: ServiceDep) -> UndoResult:
    '''
    Undo the last build.

    When a build is requested all shapes for that build are placed on an undo stack. 
    If no builds are present an http 400 bad request is returned
    '''
    return service.undo()    

@app.get("/map")
def map(service: ServiceDep) -> MapResult:
    '''
    Returns the size of the map.
    '''
    return service.map_size

if __name__ == "__main__":
    import uvicorn    
    uvicorn.run(app, host="127.0.0.1", port=8000)
    