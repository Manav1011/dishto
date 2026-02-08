from fastapi import APIRouter, Depends, status
from core.schema import BaseResponse
from core.dependencies import is_outlet_admin
from .request import OrderCreateRequest
from .response import OrderResponse
from .service import OrderService


# router
ordering_router = APIRouter(tags=["Ordering"])


# Order Endpoints

@ordering_router.post(
    "/{outlet_slug}/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Order",
    description="""
    Create a new order for an outlet.
    Requires the user to be the admin of the outlet.
    """,
)
async def create_order(
    body: OrderCreateRequest,
    service: OrderService = Depends(OrderService),
    outlet=Depends(is_outlet_admin),
) -> OrderResponse:
    return await service.create_order(body=body, outlet=outlet)