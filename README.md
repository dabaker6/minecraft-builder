# Vectors

NORTH = (0, 0, -1)
SOUTH = (0, 0,  1)
EAST  = (1, 0,  0)
WEST  = (-1, 0, 0)

To implement:
- sphere
- error handling to give better feedback to LLM
- TraceIds
- MCP
- add valid bid check

Importable package

# Setup
```bash
uv add fastapi uvicorn [standard]
uv add fastmcp
```
Pyclassic isn't on uv so need 
```bash
uv add "git+https://github.com/pyclassic/pyclassic.git" 
```

run:
```bash
python -c "import core; print(core.__file__)"
```
If none then add to pyproject.toml:
```ini
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["api", "core", "mcp_server"]
```
run
```bash
uv pip install -e .
```

Check:
```bash
python -c "import core; print(core.__file__)"
```
should 

[build-system] — tells the installer how to build your project into an installable package. hatchling is a common, simple build backend (uv uses it by default). Without a [build-system], there's nothing to install.
[tool.hatch.build.targets.wheel] packages = [...] — explicitly lists which directories are your packages. This is the line that says "core, api, and mcp_server are the things to install." Adjust to your actual top-level package folders.
each package directory must have an ```__init__.py```

# Known limitations
- Undo, if disconnects the undo stack becomes inconsistent, so on reconnect the undo stack is cleared
- Fire and forget. Was built as an API first, so a quick response was required. This means that the response to build and undo is received almost as and HTTP 200 OK response rather than a confirmation. Future work could change this to ensure the response to the LLM is accurate of what was built.
- Liveness checks are limited to sending a message to the server.

# MCGalaxy

- Get to console
```bash
docker exec -it mcgalaxy screen -U -D -r
```
- use / commands e.g.
```bash
/players # list players
/kick <player name>