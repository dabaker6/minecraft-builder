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

Check:
```bash
python -c "import core; print(core.__file__)"
```
should 

[build-system] — tells the installer how to build your project into an installable package. hatchling is a common, simple build backend (uv uses it by default). Without a [build-system], there's nothing to install.
[tool.hatch.build.targets.wheel] packages = [...] — explicitly lists which directories are your packages. This is the line that says "core, api, and mcp_server are the things to install." Adjust to your actual top-level package folders.
each package directory must have an ```__init__.py```