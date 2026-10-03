from app.domain.cache import Cache


class Node:
    def __init__(self, name: str):
        self.name = name
        self._edges: dict[str, float] = {}

    @property
    def edges(self) -> dict[str, float]:
        return self._edges

    def add_edge(self, node_name: str, latency: float):
        self._edges[node_name] = latency

    def remove_edge(self, node_name: str):
        self._edges.pop(node_name, None)


class ServerNode(Node):
    def __init__(self, name: str):
        super().__init__(name)

        self._cache = Cache()

        self._failure_count = 0
        self._is_up = True
        self._healthy = True
        self._latency = 0.0

    @property
    def is_up(self) -> bool:
        return self._is_up

    @property
    def healthy(self) -> bool:
        return self._healthy

    @property
    def failure_count(self) -> int:
        return self._failure_count

    @property
    def latency(self) -> float:
        return self._latency

    def mark_up(self):
        self._is_up = True
        self._healthy = True
        self._failure_count = 0

    def mark_down(self):
        self._is_up = False
        self._healthy = False

    def record_failure(self):
        self._failure_count += 1

    def set_healthy(self, healthy: bool):
        self._healthy = healthy

    def set_latency(self, latency: float):
        self._latency = latency

    def get_data(self, data_key: str):
        if self._cache.has(data_key):
            return self._cache.get(data_key)

        return None

    def update_data(self, data_key: str, data):
        self._cache.set(data_key, data)

    def invalidate_local_data(self, data_key: str):
        self._cache.delete(data_key)


class ClientNode(Node):
    pass