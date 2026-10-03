from __future__ import annotations

import asyncio
from typing import Any

from app.domain.node import ServerNode
from app.simulation.latency import (
    calculate_network_latency_by_km,
    sleep_ms,
)
from app.services.server_selector import ServerSelector


class ContentFetcher:
    def __init__(self, server_selector: ServerSelector):
        self._server_selector = server_selector

    async def fetch(
        self,
        server: ServerNode,
        data_key: str,
    ) -> Any | None:
        visited: set[str] = set()

        return await self._fetch(
            server,
            data_key,
            visited,
        )

    async def _fetch(
        self,
        server: ServerNode,
        data_key: str,
        visited: set[str],
    ) -> Any | None:
        if server.name in visited:
            return None

        current_visited = visited | {server.name}

        data = server.get_data(data_key)

        if data is not None:
            return data

        candidates = self._server_selector.select(server.edges)

        tasks: dict[asyncio.Task[Any | None], str] = {}

        for neighbor, distance_km in candidates:
            if neighbor.name in current_visited:
                continue

            task = asyncio.create_task(
                self._fetch_neighbor(
                    neighbor,
                    distance_km,
                    data_key,
                    current_visited,
                )
            )

            tasks[task] = neighbor.name

        try:
            while tasks:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in done:
                    tasks.pop(task, None)

                    try:
                        result = task.result()
                    except Exception:
                        continue

                    if result is not None:
                        for pending_task in pending:
                            pending_task.cancel()

                        if pending:
                            await asyncio.gather(
                                *pending,
                                return_exceptions=True,
                            )

                        server.update_data(data_key, result)

                        return result

                tasks = {
                    task: tasks[task]
                    for task in pending
                }

        finally:
            remaining = list(tasks)

            for task in remaining:
                if not task.done():
                    task.cancel()

            if remaining:
                await asyncio.gather(
                    *remaining,
                    return_exceptions=True,
                )

        return None

    async def _fetch_neighbor(
        self,
        server: ServerNode,
        distance_km: float,
        data_key: str,
        visited: set[str],
    ) -> Any | None:
        await sleep_ms(
            calculate_network_latency_by_km(distance_km)
        )

        return await self._fetch(
            server,
            data_key,
            visited,
        )