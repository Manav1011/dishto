from fastapi import APIRouter, Depends, status
from core.schema import BaseResponse
from core.dependencies import is_outlet_admin, require_feature # CHANGED: from has_feature to require_feature
from core.models import Outlet # ADDED: Import Outlet model
from functools import partial # ADDED: Import partial
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
    dependencies=[Depends(is_outlet_admin), Depends(require_feature("ordering"))], # CHANGED
)
async def create_order(
    body: OrderCreateRequest,
    service: OrderService = Depends(OrderService),
    outlet: Outlet = Depends(is_outlet_admin), # RESTORED: Keep `outlet` parameter for service call
) -> OrderResponse:
    return await service.create_order(body=body, outlet=outlet)