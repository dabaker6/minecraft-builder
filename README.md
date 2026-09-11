# Minecraft Builder

An LLM-driven build system for a self-hosted Minecraft Classic (ClassiCube / MCGalaxy) server. Describe what you want in natural language — *"build a small house with a pointed roof"* — and an AI agent constructs it block-by-block in a live world, with per-component undo.

The project exposes the same build engine through **two interfaces**: a REST API (FastAPI) and an **MCP server** (FastMCP) that plugs into Claude Desktop, so a language model can build, inspect, and correct structures using well-described tools.

---

## What it does

- Connects a bot to a MCGalaxy (Minecraft Classic) server and places blocks programmatically over the Classic protocol.
- Turns high-level shape requests (cuboid, floor, pyramid, hollow, triangle, slope) into block placements, paced to respect the server's anti-grief limits.
- Enforces a build zone (out-of-bounds blocks are dropped and reported) and validates block IDs against a configurable palette.
- Supports **undo** via per-build snapshots, so an LLM can build incrementally and revert individual components.
- Survives real-world connection problems: idle kicks, mid-build network drops, and server outages, with automatic reconnection.
- Is driven either by HTTP requests or by an LLM through the Model Context Protocol.

---

## Architecture

The project is layered so that the **core domain knows nothing about transport or LLMs**. Each layer depends only inward:

```
            +-------------------+      +-------------------+
            |   FastAPI (HTTP)  |      |  MCP server       |
            |   entry point     |      |  (FastMCP)        |
            +---------+---------+      +---------+---------+
                      |                          |
                      +------------+-------------+
                                   |
                      +------------v-------------+
                      |     core (domain)        |
                      |  build service, geometry |
                      |  palette, undo, factories|
                      +------------+-------------+
                                   |
                      +------------v-------------+
                      |  pyclassic (Classic      |
                      |  protocol client)        |
                      +--------------------------+
```

- **`core/`** — the domain. The build service, shape geometry, block palette, undo service, and factories. Contains no HTTP or MCP code; it could be driven by any transport.
- **`api/`** — a FastAPI application exposing the build engine over HTTP.
- **`mcp_server/`** — a FastMCP server exposing the build engine as MCP tools and resources for an LLM.

Both entry points own a single build service instance (one bot connection). They are **alternative front doors, not meant to run against the same bot simultaneously** (one bot per username).

### Key design decisions

- **Transport-agnostic core.** The build service returns domain objects and raises domain exceptions; each transport adapts them to its own format (HTTP status codes, MCP responses). Swapping or adding a transport touches no domain code.
- **Backend abstraction.** The build service is defined behind an interface, anticipating a future RCON/Java backend. Shape geometry produces backend-neutral output; block IDs are strings so the same contract fits both Classic (numeric IDs) and Java (namespaced IDs).
- **Factory-based construction.** A factory selects the backend, loads the matching block palette, and injects dependencies — keeping construction concerns in one place and the service testable with fakes.
- **Configurable data, not code.** The block palette and the shape catalogue (LLM-facing documentation) load from JSON, so they can be extended or reworded without changing code.

---

## How it works

### Building

1. A request (HTTP or MCP tool call) arrives with an ordered list of shapes.
2. Each shape's geometry is expanded into a list of blocks.
3. Blocks outside the build zone are filtered out (and counted); unknown block IDs are rejected.
4. A **snapshot** of the affected region is read from the live map (for undo).
5. Blocks are queued and drained onto the server at a paced rate.
6. The build's snapshot is pushed onto the undo stack.

Each build is one undo entry, so building a house as separate calls (walls, roof, stairs) lets each part be undone independently.

### The live map & connection handling

The bot maintains a live copy of the world map via a background listener thread that receives the server's block-change broadcasts. This map is the source of truth for undo snapshots.

Connection resilience is handled through:

- **Lazy connection** — the bot connects on first use, so the server starts instantly (important for the MCP handshake timeout).
- **On-demand liveness checks & reconnect** — before each build, the connection is probed; if dead (idle kick, dropped network), it reconnects and reloads the map.
- **Atomic reconnect** — a failed connection attempt fully cleans up (no leaked threads) rather than leaving half-started state.
- **Undo invalidation on reconnect** — because the world may have changed during a disconnection, the undo stack is cleared on reconnect to avoid restoring stale state.

---

## The MCP server

The MCP server exposes the build engine to an LLM (e.g. via Claude Desktop) using hand-written FastMCP tools and resources:

- **Tools** (actions): `build`, `undo` — invoked by the LLM to change the world.
- **Resources** (read-only reference): the block palette and the shape catalogue — the LLM reads these to choose blocks and understand available shapes.

Instructions reach the LLM through three layers:
- **Tool input schemas** (Pydantic field descriptions) — precise, validation-backed parameter specs.
- **Tool docstrings** — concise build strategy (build in stages, check results, coordinate system).
- **The shape catalogue resource** — a JSON-backed, editable reference the LLM consults on demand.

---

## Tech stack

- **Python 3.14** (managed with [uv](https://docs.astral.sh/uv/))
- **FastAPI** — HTTP interface
- **FastMCP** — Model Context Protocol server
- **Pydantic** — request/response schemas and validation (discriminated unions for heterogeneous shapes)
- **pyclassic** — Minecraft Classic protocol client
- **MCGalaxy** — the Minecraft Classic server (run in Docker)

---

## Getting started

### Prerequisites

- Python 3.14+ and [uv](https://docs.astral.sh/uv/)
- A running MCGalaxy server (see [Server setup](#server-setup))

### Install

```bash
git clone <REPO_URL>
cd <REPO_NAME>
uv sync
```

This creates the virtual environment and installs the project (including its own packages, editable) so imports resolve from any launch context.

Also see [setup](setup.md) for further instructions

### Configure

Edit `config.py` (or the relevant config module) to set:

- `SERVER_IP` / `SERVER_PORT` — your MCGalaxy server address
- `USERNAME` — the bot's username (must be below the server's admin-verification rank)
- `BLOCK_PALETTE` / palette paths — which block palette to load
- shape catalogue path

### Run the HTTP API

```bash
uv run uvicorn api.main:app --host <HOST> --port 8000
```

Interactive docs at `http://<HOST>:8000/docs`.

### Run the MCP server

Add to your Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "minecraft-builder": {
      "command": "<ABSOLUTE_PATH>\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "PYTHONPATH": "<ABSOLUTE_PATH_TO_REPO>"
      }
    }
  }
}
```

Pointing directly at the venv's Python avoids per-launch environment resolution, keeping startup within the MCP handshake timeout. Fully restart Claude Desktop after config changes, and start a new conversation to pick up updated tool definitions.

---

## Server setup

The Minecraft Classic server runs as a Docker container. Example `docker-compose.yml`:

```yaml
services:
  mcgalaxy:
    container_name: mcgalaxy
    image: rdebath/mcgalaxy:latest
    volumes:
      - ./mcgalaxy/data:/home/user
    ports:
      - "<HOST_IP>:25566:25565"   # host:container — MCGalaxy listens on 25565
    restart: unless-stopped
```

Notes:
- The bind-mounted data directory must be owned by the container's user (UID 1000): `sudo chown -R 1000:1000 ./mcgalaxy/data`.
- Set `verify-names = false` in `server.properties` for a LAN server so the bot (and players) can connect without account verification.
- Keep the build bot's rank below the admin-verification threshold, or it will be unable to build.

---

## Project status & limitations

- Single-backend (Classic/MCGalaxy); the interface anticipates an RCON/Java backend, not yet implemented.
- One bot per server; the HTTP API and MCP server are alternative entry points, not concurrent.
- A build interrupted by a mid-drain disconnection completes partially and is not undoable (the interrupted snapshot is cleared on reconnect).
- Undo history is bounded and is cleared on reconnection.
- Fire and forget. Was built as an API first, so a quick response was required. This means that the response to build and undo is received as an HTTP 200 OK response rather than a confirmation. Future work could change this to ensure the response to the LLM is accurate of what was built.

---

## Acknowledgements

- [pyclassic](https://github.com/pyclassic/pyclassic) — Minecraft Classic protocol client
- [MCGalaxy](https://github.com/UnknownShadow200/MCGalaxy) — Minecraft Classic server software
- [FastMCP](https://gofastmcp.com) — MCP server framework

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Author

[David Baker](https://david-baker.co.uk)
