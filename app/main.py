from contextlib import asynccontextmanager

from fastapi import FastAPI
import asyncio

from app.helpers.health_checker import HealthChecker
from app.middlewares.dns_simulator import DnsSimulator
from app.node import ClientNode, ServerNode
from app.node_registery import register_server_nodes, register_client_nodes
from app.router import router


SERVERS: dict[str, ServerNode] = {}
CLIENTS: dict[str, ClientNode] = {}

health_checker = HealthChecker([server for server in SERVERS.values()])

@asynccontextmanager
async def lifespan(app: FastAPI):
    register_server_nodes(SERVERS)
    register_client_nodes(CLIENTS)

    asyncio.create_task(health_checker.run())

    yield


fastapi_app = FastAPI(lifespan=lifespan)
fastapi_app.add_middleware(DnsSimulator)

fastapi_app.add_api_route("", router)

