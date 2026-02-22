from .request import OrderCreateRequest
from .response import OrderResponse, OrderItemResponse
from .models import Order, OrderItem
from Menu.models import MenuItem
from Inventory.models import MenuItemIngredient, InventoryTransaction, Ingredient
from fastapi import HTTPException, status
from core.utils.asyncs import get_related_object
from decimal import Decimal
from asgiref.sync import sync_to_async
from django.db import transaction

class OrderService:
    async def create_order(self, body: OrderCreateRequest, outlet) -> OrderResponse:
        try:
            # Check if the outlet has the inventory feature enabled
            has_inventory_feature = await outlet.features.filter(name="inventory").aexists()

            # Calculate total amount and validate items
            total_amount = Decimal("0.00")
            order_items_details = []
            menu_item_slugs = [item.item_slug for item in body.items]
            menu_items_qs = MenuItem.objects.filter(slug__in=menu_item_slugs)
            menu_items_map = {item.slug: item async for item in menu_items_qs}

            if len(menu_items_map) != len(menu_item_slugs):
                raise HTTPException(status_code=404, detail="One or more menu items not found.")

            for item in body.items:
                menu_item = menu_items_map.get(item.item_slug)
                if not menu_item:
                    raise HTTPException(status_code=404, detail=f"Menu item '{item.item_slug}' not found.")
                
                item_price = menu_item.price
                total_amount += item_price * item.quantity
                order_items_details.append({
                    "menu_item": menu_item,
                    "quantity": item.quantity,
                    "price": item_price
                })

            # Wrap order, item creation, and inventory transaction in a sync transaction
            @sync_to_async
            def create_order_sync_with_inventory(current_outlet, items_details, inventory_enabled):
                with transaction.atomic():
                    order = Order.objects.create(
                        outlet=current_outlet,
                        total_amount=total_amount,
                        special_instructions=body.special_instructions,
                    )
                    item_objs = []
                    for oi_detail in items_details:
                        order_item = OrderItem.objects.create(
                            order=order, # Link order_item to the created order
                            item=oi_detail["menu_item"],
                            quantity=oi_detail["quantity"],
                            price=oi_detail["price"],
                        )
                        item_objs.append(order_item)

                    # Inventory transaction part - only if inventory is enabled
                    if inventory_enabled:
                        for oi_detail in items_details:
                            menu_item = oi_detail["menu_item"]
                            quantity_ordered = oi_detail["quantity"]
                            # Get all MenuItemIngredient objects for this menu item
                            menu_item_ingredients = list(MenuItemIngredient.objects.filter(menu_item=menu_item))
                            for mii in menu_item_ingredients:
                                ingredient = mii.ingredient
                                # Total quantity used = ingredient quantity per item * number of items ordered
                                total_ingredient_used = mii.quantity * quantity_ordered
                                # Create InventoryTransaction (assume 'OUT' for usage)
                                InventoryTransaction.objects.create(
                                    ingredient=ingredient,
                                    transaction_type='usage',
                                    quantity=total_ingredient_used,
                                    note=f"Used in order {order.slug}",
                                    outlet=current_outlet
                                )
                                # Deduct from ingredient stock
                                ingredient.current_stock -= total_ingredient_used
                                ingredient.save()

                    return order, item_objs

            order, item_objs = await create_order_sync_with_inventory(outlet, order_items_details, has_inventory_feature)

            # Build response
            items = []
            for oi in item_objs:
                menu_item = await get_related_object(oi, "item")
                items.append(OrderItemResponse(
                    item_slug=menu_item.slug,
                    quantity=oi.quantity,
                    price=oi.price,
                    slug=oi.slug
                ))

            return OrderResponse(
                outlet_slug=outlet.slug,
                order_date=str(order.order_date),
                status=order.status,
                total_amount=order.total_amount,
                special_instructions=order.special_instructions,
                slug=order.slug,
                items=items
            )

        except MenuItem.DoesNotExist:
            raise HTTPException(status_code=404, detail="Menu item not found")
        except Exception as e:
            # Added more specific exception handling for better debugging
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")
