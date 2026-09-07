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