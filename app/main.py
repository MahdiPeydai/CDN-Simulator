from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
import asyncio

from app.helpers.health_checker import HealthChecker
from app.middlewares.cdn_simulator import CdnSimulatorMiddleware
from app.node import ClientNode, ServerNode
from app.node_registery import register_server_nodes, register_client_nodes
from app.router import router


SERVERS: dict[str, ServerNode] = {}
CLIENTS: dict[str, ClientNode] = {}

health_checker = HealthChecker([])

@asynccontextmanager
async def lifespan(app: FastAPI):
    SERVERS.clear()
    CLIENTS.clear()
    register_server_nodes(SERVERS)
    register_client_nodes(CLIENTS)
    health_checker.servers = list(SERVERS.values())

    health_check_task = asyncio.create_task(health_checker.run())
    try:
        yield
    finally:
        health_check_task.cancel()
        with suppress(asyncio.CancelledError):
            await health_check_task


fastapi_app = FastAPI(
    title="CDN Simulator",
    version="1.0.0",
    description=(
        "A small in-memory CDN simulation demonstrating edge selection, "
        "network latency, cache fill, invalidation, and node failure handling."
    ),
    lifespan=lifespan,
)
fastapi_app.add_middleware(CdnSimulatorMiddleware)
fastapi_app.include_router(router)


