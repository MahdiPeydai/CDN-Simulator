from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.helpers.dns_helpers import sort_enable_by_duration_estimation
from app.main import CLIENTS


class DnsSimulator(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # fetching client node from request header to simulate client request location
        client_node_id = request.headers.get("X-Client-Node", None)
        if client_node_id is None:
            return JSONResponse(status_code=400, content={"message": "X-Client-IP not provided"})

        client_node = CLIENTS.get(client_node_id, None)
        if not client_node:
            return JSONResponse(status_code=500, content={"message": "Client node not found"})

        client_edges = client_node.edges
        # dns logic to find fastest enable server
        sorted_enable_servers = sort_enable_by_duration_estimation(client_edges)

        request.state["sorted_enable_servers"] = sorted_enable_servers

        response = await call_next(request)


        return response
