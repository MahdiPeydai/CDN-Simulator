import asyncio
import time

from app.main import SERVERS
from app.node import ServerNode


def sort_enable_by_duration_estimation(edges: dict[str, float]) -> list[tuple[ServerNode, float]]:
     return sorted(
        (
            (SERVERS[name], edges[name])
            for name in edges
            if name in SERVERS and SERVERS[name].is_up
        ),
        key=lambda server: server.latency + (edges[server.name] / 100) * 10,
    )


def calculate_network_latency_by_km(distance_km: float) -> float:
    return (distance_km / 100) * 10


async def time_sleep_ms(time_ms: float):
    await asyncio.sleep(time_ms / 1000)