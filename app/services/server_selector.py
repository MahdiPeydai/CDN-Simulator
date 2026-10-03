from app.domain.node import ServerNode


class ServerSelector:
    def __init__(self, servers: dict[str, ServerNode]):
        self._servers = servers

    def select(
        self,
        edges: dict[str, float],
    ) -> list[tuple[ServerNode, float]]:
        return sorted(
            (
                (self._servers[name], distance)
                for name, distance in edges.items()
                if name in self._servers
                and self._servers[name].is_up
            ),
            key=lambda server: (
                server[0].latency
                + (server[1] / 100) * 10
            ),
        )