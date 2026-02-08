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
        """
        here we'll get the items in body.items so first we need to fetch all the items and their quantity.
        
        # costing part
        get all the menu items objects
        calculate the pricings aas per quantity
        
        #inventory transaction part
        from each item we'll get it's MenuItemIngredient object so we'll get all the ingrediants used in the menu item
        then we'll get the ingredient object and then we'll create an InventoryTransaction for each ingredient used in the menu item according to the quantity used.
        
        
        """
        try:
            # Calculate total amount and validate items
            total_amount = Decimal("0.00")
            order_items = []
            for item in body.items:
                menu_item = await MenuItem.objects.aget(slug=item.item_slug)
                item_price = menu_item.price
                total_amount += item_price * item.quantity
                order_items.append({
                    "menu_item": menu_item,
                    "quantity": item.quantity,
                    "price": item_price
                })

            # Wrap order, item creation, and inventory transaction in a sync transaction
            @sync_to_async
            def create_order_sync_with_inventory():
                with transaction.atomic():
                    order = Order.objects.create(
                        outlet=outlet,
                        total_amount=total_amount,
                        special_instructions=body.special_instructions,
                    )
                    item_objs = [
                        OrderItem.objects.create(
                            item=oi["menu_item"],
                            quantity=oi["quantity"],
                            price=oi["price"],
                        )
                        for oi in order_items
                    ]
                    order.order_items.set(item_objs)

                    # Inventory transaction part
                    for oi in order_items:
                        menu_item = oi["menu_item"]
                        quantity_ordered = oi["quantity"]
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
                                outlet=outlet
                            )
                            # Deduct from ingredient stock
                            ingredient.current_stock -= total_ingredient_used
                            ingredient.save()

                    return order, item_objs

            order, item_objs = await create_order_sync_with_inventory()

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
            raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")
