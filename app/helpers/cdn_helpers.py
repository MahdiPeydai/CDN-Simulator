import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.node import ServerNode


def sort_enable_by_duration_estimation(edges: dict[str, float], servers: dict[str, ServerNode] | None = None) -> list[tuple[ServerNode, float]]:
    if servers is None:
       from app.main import SERVERS as servers

    return sorted(
       (
           (servers[name], edges[name])
           for name in edges
           if name in servers and servers[name].is_up
       ),
       key=lambda server: server[0].latency + (edges[server[0].name] / 100) * 10,
    )


def calculate_network_latency_by_km(distance_km: float) -> float:
    return (distance_km / 100) * 10


async def time_sleep_ms(time_ms: float):
    await asyncio.sleep(time_ms / 1000)