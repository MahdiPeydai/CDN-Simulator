from typing import Any

from fastapi import APIRouter, Request, Body, status
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/data")


@router.get("/{data_key}")
async def get_data(request: Request, data_key: str):
    cdn_service = request.app.state.cdn_service
    client = request.state.client_node

    result = await cdn_service.get_data(
        client,
        data_key,
    )

    if result.server_failed:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "result": None,
                "success": False,
                "message": "internal server error",
            },
        )

    if not result.found:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "result": None,
                "success": False,
                "message": "data not found",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "result": result.data,
            "success": True,
        },
    )


@router.post("/{data_key}")
async def update_data(
    request: Request,
    data_key: str,
    data: Any = Body(...),
):
    cdn_service = request.app.state.cdn_service
    client = request.state.client_node

    result = await cdn_service.update_data(
        client,
        data_key,
        data,
    )

    if result.server_failed:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "result": None,
                "success": False,
                "message": "internal server error",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "result": result.data,
            "success": True,
        },
    )