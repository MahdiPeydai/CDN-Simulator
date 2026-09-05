import asyncio
from typing import Optional, Any

from app.helpers.cdn_helpers import time_sleep_ms, sort_enable_by_duration_estimation, calculate_network_latency_by_km


class Node:
    def __init__(self, name: str):
        self._name = name
        self._edges: dict[str, float] = {}

    @property
    def name(self):
        return self._name

    @property
    def edges(self):
        return self._edges

    def set_edge(self, node_name, distance: float):
        self._edges[node_name] = distance


class ServerNode(Node):
    def __init__(self, name: str, database: dict, latency: int = 0, is_up: bool = True):
        super().__init__(name)
        self._database: dict = database
        self._latency = latency
        self._is_up = is_up
        self._healthy = True
        self._failure_count = 0
        self._process_latency = 10

    @property
    def database(self):
        return self._database

    @property
    def latency(self):
        return self._latency

    def set_latency(self, latency: float):
        self._latency = latency

    @property
    def is_up(self):
        return self._is_up

    @property
    def healthy(self):
        return self._healthy

    async def get_data(self, data_key: str, requester_node: Optional[str] = None) -> Optional[dict]:
        await time_sleep_ms(self._process_latency)
        data = self._database.get(data_key, None)
        if data:
            return data

        result = await self.get_from_other_nodes(data_key, requester_node)

        if result is not None:
            self._database[data_key] = result
        return result

    async def get_from_other_nodes(self, data_key: str, requester_node: Optional[str] = None) -> Optional[dict]:
        from app.main import SERVERS

        edges = self.edges.copy()
        if requester_node:
            edges.pop(requester_node, None)

        sorted_enable_servers = sort_enable_by_duration_estimation(edges, SERVERS)

        tasks: dict[asyncio.Task, str] = {
            asyncio.create_task(server[0].get_data(data_key, requester_node=self.name)): server[0].name
            for server in sorted_enable_servers
        }

        while tasks:
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in done:
                server_name = tasks[task]
                result = task.result()

                if result is not None:
                    await time_sleep_ms(calculate_network_latency_by_km(distance_km=self.edges[server_name]))
                    return result

            tasks = {task: tasks[task] for task in pending}

        return None

    async def invalidate_data(self, data_key: str, requester_node: Optional[str] = None):
        self._database.pop(data_key, None)
        await self.push_data_invalidation(data_key, requester_node)

    async def push_data_invalidation(self, data_key: str, requester_node: Optional[str] = None):
        from app.main import SERVERS

        edges = self.edges.copy()
        if requester_node:
            edges.pop(requester_node, None)

        tasks = [
            asyncio.create_task(SERVERS[node_name].invalidate_data(data_key, requester_node=self.name))
            for node_name in edges.keys()
        ]

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def update_data(self, data_key: str, data: Any | None = None):
        try:
            self._database[data_key] = data
            await self.push_data_invalidation(data_key)
            return data
        except:
            return None

    def add_failure(self):
        self._failure_count += 1

        if self._failure_count >= 5:
            self._is_up = False

    def flash_failure(self):
        self._failure_count = 0

    def mark_up(self):
        self._is_up = True

    def mark_down(self):
        self._is_up = False


class ClientNode(Node):
    pass
