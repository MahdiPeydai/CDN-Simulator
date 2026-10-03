import time

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.domain.node import ClientNode


class CdnSimulatorMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
            clients: dict[str, ClientNode],
    ):
        super().__init__(app)
        self._clients = clients


    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/data/"):
            return await call_next(request)

        start = time.monotonic()

        client_node_id = request.headers.get("X-Client-Node")
        if client_node_id is None:
            return JSONResponse(status_code=400, content={"message": "X-Client-IP not provided"})

        client_node = self._clients.get(client_node_id, None)

        if not client_node:
            return JSONResponse(status_code=400, content={"message": "Client node not found"})

        request.state.client_node = client_node

        response = await call_next(request)

        duration = time.monotonic() - start
        response.headers["X-Simulation-Duration"] = str(duration)

        return response
