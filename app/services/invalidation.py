from app.domain.node import ServerNode


class InvalidationService:
    def __init__(self, servers: dict[str, ServerNode]):
        self._servers = servers

    def invalidate(
        self,
        data_key: str,
        source_server: ServerNode,
    ):
        for server in self._servers.values():
            if server is source_server:
                continue

            server.invalidate_local_data(data_key)