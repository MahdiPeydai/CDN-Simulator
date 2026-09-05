import asyncio

from app.node import ServerNode


class HealthChecker:
    def __init__(self, servers: list[ServerNode], interval: float = 5):
        self.servers = servers
        self.interval = interval
        self._task = None

    async def run(self):
        while True:
            await self.check_all()
            await asyncio.sleep(self.interval)

    async def check_all(self):
        await asyncio.gather(
            *(self._check(server) for server in self.servers)
        )

    @staticmethod
    async def _check(server: ServerNode):
        if server.healthy:
            server.mark_up()
        else:
            server.mark_down()