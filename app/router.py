import time
from typing import Any

from fastapi import APIRouter, Request, Body
from starlette import status
from starlette.responses import JSONResponse

from app.helpers.cdn_helpers import calculate_network_latency_by_km, time_sleep_ms
from app.node import ServerNode

router = APIRouter(prefix="/data")

@router.get("/{data_key}")
async def get_data(request: Request, data_key: str):
    enable_servers_nodes: list[tuple[ServerNode, float]] = (
        request.state.sorted_enable_servers
    )
    for node in enable_servers_nodes:
        server = node[0]

        await time_sleep_ms(calculate_network_latency_by_km(distance_km=node[1]))

        try:
            start_time = time.monotonic()
            response = await server.get_data(data_key)
            duration = time.monotonic() - start_time
            server.set_latency(duration)
        except:
            server.add_failure()
            continue


        if response is not None:
            server.flash_failure()
            return JSONResponse(status_code=status.HTTP_200_OK, content={"result": response,
                                                                         "success": True})

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"result": None,
                                                                            "success": False,
                                                                            "message": "data not found"})

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"result": None,
                                                                                    "success": False,
                                                                                    "message": "internal server error"})


@router.post("/{data_key}")
async def update_data(request: Request, data_key: str, data: Any = Body(...)):
    enable_servers_nodes: list[tuple[ServerNode, float]] = (
        request.state.sorted_enable_servers
    )
    for node in enable_servers_nodes:
        server = node[0]

        await time_sleep_ms(calculate_network_latency_by_km(distance_km=node[1]))

        try:
            start_time = time.monotonic()
            response = await server.update_data(data_key, data)
            duration = time.monotonic() - start_time
            server.set_latency(duration)
        except:
            server.add_failure()
            continue


        if response is not None:
            server.flash_failure()
            return JSONResponse(status_code=status.HTTP_200_OK, content={"result": response,
                                                                         "success": True})

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"result": None,
                                                                            "success": False,
                                                                            "message": "data not found"})

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"result": None,
                                                                                    "success": False,
                                                                                    "message": "internal server error"})
