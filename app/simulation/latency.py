import asyncio


def calculate_network_latency_by_km(distance_km: float) -> float:
    return (distance_km / 100) * 10


async def sleep_ms(time_ms: float):
    await asyncio.sleep(time_ms / 1000)