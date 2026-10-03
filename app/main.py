from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
import asyncio

from app.domain.node import ServerNode, ClientNode
from app.services.health_checker import HealthChecker
from app.middlewares.cdn_simulator import CdnSimulatorMiddleware
from app.services.invalidation import InvalidationService
from app.topology import create_topology
from app.api.routes import router
from app.services.cdn_service import CDNService
from app.services.content_fetcher import ContentFetcher
from app.services.server_selector import ServerSelector

# mutable servers and clients
SERVERS: dict[str, ServerNode] = {}
CLIENTS: dict[str, ClientNode] = {}

@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    # creating topology
    SERVERS.clear()
    CLIENTS.clear()

    servers, clients = create_topology()

    SERVERS.update(servers)
    CLIENTS.update(clients)

    # creating health checker
    health_checker = HealthChecker(list(SERVERS.values()))

    # creating services
    server_selector = ServerSelector(SERVERS)
    content_fetcher = ContentFetcher(server_selector)
    invalidation_service = InvalidationService(SERVERS)
    cdn_service = CDNService(content_fetcher=content_fetcher,
                             server_selector=server_selector,
                             invalidation_service=invalidation_service)

    # set cdn_service as app state
    fastapi.state.cdn_service = cdn_service

    # running health checker
    health_check_task = asyncio.create_task(health_checker.run())

    try:
        yield
    finally:
        # closing health checker
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

def register_middlewares(fastapi: FastAPI):
    fastapi.add_middleware(CdnSimulatorMiddleware, clients=CLIENTS)


def register_routes(fastapi: FastAPI):
    fastapi.include_router(router)


register_middlewares(fastapi_app)
register_routes(fastapi_app)