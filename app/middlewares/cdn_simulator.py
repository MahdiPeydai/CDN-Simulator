import time

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.helpers.cdn_helpers import sort_enable_by_duration_estimation


class CdnSimulatorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/data/"):
            return await call_next(request)

        start = time.monotonic()
        from app.main import CLIENTS, SERVERS

        # fetching client node from request header to simulate client request location
        client_node_id = request.headers.get("X-Client-Node", None)
        if client_node_id is None:
            return JSONResponse(status_code=400, content={"message": "X-Client-IP not provided"})

        client_node = CLIENTS.get(client_node_id, None)
        if not client_node:
            return JSONResponse(status_code=400, content={"message": "Client node not found"})

        client_edges = client_node.edges
        # dns logic to find fastest enable server
        sorted_enable_servers = sort_enable_by_duration_estimation(client_edges, SERVERS)

        request.state.sorted_enable_servers = sorted_enable_servers

        response = await call_next(request)
        duration = time.monotonic() - start
        response.headers["X-Simulation-Duration"] = str(duration)

        return response
