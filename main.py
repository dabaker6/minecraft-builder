from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, Request

from factories.build_factory import BuildFactory
from buildservices.base import BuildService
from shapebuilders.schemas import BuildBatch, StatusResult

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = BuildFactory.create_shape_builder()
    yield
    app.state.service.close()

app = FastAPI(lifespan=lifespan, title="BuildBot API", description="API for Minecraft Classic BuildBot", version="0.1.0")

def get_service(request: Request) -> BuildService:
    return request.app.state.service

ServiceDep = Annotated[BuildService, Depends(get_service)]

@app.get("/status", response_model=StatusResult)
def get_status(service: ServiceDep):
    return {"pending": service.pending}

@app.post("/build")
def build(body: BuildBatch, service: ServiceDep):
    results = []

    for shape in body.shapes:

        service.add_shape(shape)
    return service.execute()


# - add kept check
# - add forbid

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)