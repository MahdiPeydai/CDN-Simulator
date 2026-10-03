import time
from dataclasses import dataclass
from typing import Any

from app.domain.node import ClientNode
from app.helpers.cdn_helpers import (
    calculate_network_latency_by_km,
    sleep_ms,
)
from app.services.content_fetcher import ContentFetcher
from app.services.invalidation import InvalidationService
from app.services.server_selector import ServerSelector


@dataclass
class CDNResult:
    data: Any | None
    found: bool
    server_failed: bool = False


class CDNService:
    def __init__(
        self,
        content_fetcher: ContentFetcher,
        server_selector: ServerSelector,
        invalidation_service: InvalidationService,
    ):
        self._content_fetcher = content_fetcher
        self._server_selector = server_selector
        self._invalidation_service = invalidation_service

    async def get_data(
            self,
            client: ClientNode,
            data_key: str,
    ) -> CDNResult:
        servers = self._server_selector.select(client.edges)

        for server, distance_km in servers:
            await sleep_ms(calculate_network_latency_by_km(distance_km))

            try:
                start_time = time.monotonic()

                response = await self._content_fetcher.fetch(
                    server,
                    data_key,
                )

                duration = time.monotonic() - start_time
                server.set_latency(duration)

            except Exception:
                server.record_failure()
                continue

            if response is not None:
                server.mark_up()
                return CDNResult(
                    data=response,
                    found=True,
                )

            return CDNResult(
                data=None,
                found=False,
            )

        return CDNResult(
            data=None,
            found=False,
            server_failed=True,
        )

    async def update_data(
            self,
            client: ClientNode,
            data_key: str,
            data: Any,
    ) -> CDNResult:

        servers = self._server_selector.select(client.edges)

        for server, distance_km in servers:
            await sleep_ms(
                calculate_network_latency_by_km(distance_km)
            )

            try:
                start_time = time.monotonic()

                server.update_data(data_key, data)

                self._invalidation_service.invalidate(
                    data_key,
                    server,
                )

                server.set_latency(
                    time.monotonic() - start_time
                )

            except Exception:
                server.record_failure()
                continue

            server.mark_up()

            return CDNResult(
                data=data,
                found=True,
            )

        return CDNResult(
            data=None,
            found=False,
            server_failed=True,
        )