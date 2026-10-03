# CDN Simulator

A small FastAPI-based CDN simulator built as an interview assignment. It models clients, edge servers, geographic latency, cache fill, cache invalidation, server selection, failures, and health checks entirely in memory.

## What it demonstrates

- **Latency-aware edge selection**: a client is routed to available edge servers using simulated network distance plus measured server latency.
- **Cache miss forwarding**: an edge that misses can fetch the value through connected server nodes and cache the result locally.
- **Cache invalidation**: writes are accepted by the selected edge and invalidation is propagated through the server graph.
- **Failure handling**: failed requests increment a per-node failure counter and can temporarily remove a node from routing.
- **Health checking**: a lightweight background health checker reconciles server routing state.
- **Deterministic topology**: the server/client graph is defined in `app/topology.py`, making scenarios easy to inspect and test.

## Topology

Server links use distance in kilometers:

```text
B --500-- A --800-- C
          |
         200
          |
          D --300-- E
```

Client connectivity:

```text
Client 0 -> B (200 km), D (100 km), E (150 km)
Client 1 -> C (50 km), D (700 km)
```

The simulator uses **10 ms per 100 km** as the network-latency rule, plus a server's measured processing latency.

## API

### Scope

> **The CDN functionality only applies to URLs under `/data/*`.**

Requests such as `/docs`, `/openapi.json`, `/health`, and other application endpoints **bypass the CDN middleware** and are handled normally by FastAPI.

For example:

- `GET /data/example` → handled by the CDN simulator
- `GET /docs` → handled directly by FastAPI
- `GET /openapi.json` → handled directly by FastAPI
- `GET /health` → handled directly by FastAPI
Every request must include an `X-Client-Node` header (`0` or `1`).

### Read data

```bash
curl -H 'X-Client-Node: 0' http://localhost:8000/data/example
```

Successful response:

```json
{"result": "value", "success": true}
```

### Write/update data

```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-Client-Node: 1' \
  -d '"new-value"' \
  http://localhost:8000/data/example
```

A successful write stores the value on the selected edge and invalidates stale copies on the rest of the connected server graph.

### Simulation timing

Successful API responses include:

```text
X-Simulation-Duration: <seconds>
```

This reports the wall-clock duration of the simulated request.

## Run locally

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:fastapi_app
```

Then open the interactive API documentation at `http://localhost:8000/docs`.

## Run with Docker

```bash
docker build -t cdn-simulator .
docker run --rm -p 8000:8000 cdn-simulator
```

## Tests

```bash
pytest -q
```

The tests cover routing by proximity/latency, down/busy nodes, cache fills, invalidation, API header validation, falsy cached values, required request bodies, and end-to-end FastAPI behavior.

## Design choices and scope

This is a simple **in-memory simulator** by design, not a production CDN. No external database, distributed cache, real DNS, or real network calls are required. Distances and latency are deterministic so the behavior can be exercised in automated tests.

The server graph is small and currently has no arbitrary cyclic topology beyond bidirectional links. For a general graph, invalidation/fetch traversal should use a request-scoped `visited` set or request ID to guarantee cycle safety. Similarly, production systems would use persistent/distributed state, structured observability, explicit timeouts/circuit breakers, and a real health-probe mechanism.

## Project Structure

The project is organized by responsibility to keep the CDN simulation logic separate from HTTP handling, domain models, and simulation utilities.

```text
app/
├── api/
│   └── routes.py              # HTTP endpoints
│
├── domain/
│   ├── cache.py               # In-memory cache
│   └── node.py                # Server and client node models
│
├── middlewares/
│   └── cdn_simulator.py       # Client resolution and request simulation
│
├── services/
│   ├── cdn_service.py         # Main CDN operation
│   ├── content_fetcher.py     # Content lookup and graph traversal
│   ├── health_checker.py      # Simulated server health checks
│   ├── invalidation.py        # Content invalidation
│   └── server_selector.py     # Server selection and ordering
│
├── simulation/
│   └── latency.py             # Network latency simulation
│
├── topology.py                # Builds the simulated network topology
└── main.py                    # Application setup
```

### Responsibilities

* **API** handles HTTP requests and converts service results into HTTP responses.
* **Middleware** resolves the client node and adds simulation-related response information.
* **CDN Service** coordinates CDN operations such as fetching and updating data.
* **Content Fetcher** handles content lookup and traverses the server graph when data is not available locally.
* **Server Selector** selects and orders available servers based on simulated latency.
* **Invalidation Service** removes stale content data from other servers after an update.
* **Domain models** represent servers, clients, and their local caches.
* **Simulation** contains latency-related simulation utilities.
* **Topology** defines the predefined servers, clients, and network connections.
* **Main** initializes the application and wires the components together.

```
