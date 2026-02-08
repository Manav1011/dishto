from .request import IngredientCreationRequest, IngredientUpdateRequest, MenuItemIngredientCreateRequest, MenuItemIngredientUpdateRequest, InventoryTransactionCreateRequest, InventoryTransactionUpdateRequest, OrderCreateRequest
from .response import IngredientCreationResponse, IngredientObject, IngredientObjects, MenuItemIngredientObject, MenuItemIngredientObjects, InventoryTransactionObject, InventoryTransactionObjects, OrderResponse, OrderItemResponse
from .models import Ingredient, MenuItemIngredient, InventoryTransaction, Order, OrderItem
from Menu.models import MenuItem, Outlet
from fastapi import HTTPException, status
from core.utils.asyncs import get_queryset, get_related_object
from dishto.GlobalUtils import generate_unique_hash
from decimal import Decimal
from asgiref.sync import sync_to_async
from django.db import transaction

class InventoryService:
    async def create_ingredient(self, body: IngredientCreationRequest, outlet) -> IngredientCreationResponse:
        try:
            ingredient = await Ingredient.objects.acreate(
                name=body.name,
                unit=body.unit,
                current_stock=body.current_stock,
                minimum_stock=body.minimum_stock,
                outlet=outlet
            )
            return IngredientCreationResponse(
                name=ingredient.name,
                unit=ingredient.unit,
                current_stock=float(ingredient.current_stock),
                minimum_stock=float(ingredient.minimum_stock),
                slug=ingredient.slug
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create ingredient: {str(e)}"
            )

    async def get_ingredients(self, slug: str, outlet) -> IngredientObject | IngredientObjects:
        from django.db.models import F
        try:
            if slug == "__all__":
                queryset = Ingredient.objects.filter(outlet=outlet)
                ingredients = await get_queryset(list, queryset)
                return IngredientObjects(
                    ingredients=[
                        IngredientObject(
                            name=i.name,
                            unit=i.unit,
                            current_stock=float(i.current_stock),
                            minimum_stock=float(i.minimum_stock),
                            is_active=i.is_active,
                            slug=i.slug
                        ) for i in ingredients
                    ]
                )
            else:
                ingredient = await Ingredient.objects.aget(slug=slug, outlet=outlet)
                return IngredientObject(
                    name=ingredient.name,
                    unit=ingredient.unit,
                    current_stock=float(ingredient.current_stock),
                    minimum_stock=float(ingredient.minimum_stock),
                    is_active=ingredient.is_active,
                    slug=ingredient.slug
                )
        except Ingredient.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve ingredient(s): {str(e)}"
            )

    async def update_ingredient(self, slug: str, body: IngredientUpdateRequest, outlet) -> IngredientObject:
        try:
            ingredient = await Ingredient.objects.aget(slug=slug, outlet=outlet)
            update_fields = body.dict(exclude_unset=True)
            for field, value in update_fields.items():
                if hasattr(ingredient, field):
                    setattr(ingredient, field, value)
            await ingredient.asave()
            return IngredientObject(
                name=ingredient.name,
                unit=ingredient.unit,
                current_stock=float(ingredient.current_stock),
                minimum_stock=float(ingredient.minimum_stock),
                is_active=ingredient.is_active,
                slug=ingredient.slug
            )
        except Ingredient.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update ingredient: {str(e)}"
            )

    async def delete_ingredient(self, slug: str, outlet) -> dict:
        try:
            ingredient = await Ingredient.objects.aget(slug=slug, outlet=outlet)
            await ingredient.adelete()
            return {"message": "Ingredient deleted successfully"}
        except Ingredient.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete ingredient: {str(e)}"
            )

    async def set_ingredient_active(self, slug: str, is_active: bool, outlet) -> IngredientObject:
        try:
            ingredient = await Ingredient.objects.aget(slug=slug, outlet=outlet)
            ingredient.is_active = is_active
            await ingredient.asave()
            return IngredientObject(
                name=ingredient.name,
                unit=ingredient.unit,
                current_stock=float(ingredient.current_stock),
                minimum_stock=float(ingredient.minimum_stock),
                is_active=ingredient.is_active,
                slug=ingredient.slug
            )
        except Ingredient.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update ingredient active status: {str(e)}"
            )

    async def list_menu_item_ingredients(self, menu_item_slug: str, outlet) -> MenuItemIngredientObjects:
        try:
            menu_item = await MenuItem.objects.aget(slug=menu_item_slug)
            queryset = MenuItemIngredient.objects.filter(menu_item=menu_item)
            menu_item_ingredients = await get_queryset(list, queryset)
            result = []
            for mi in menu_item_ingredients:                
                ingredient = await get_related_object(mi, "ingredient")
                result.append(
                    MenuItemIngredientObject(
                        menu_item_slug=menu_item.slug,
                        ingredient_slug=ingredient.slug,
                        quantity=float(mi.quantity),
                        slug=mi.slug
                    )
                )
            return MenuItemIngredientObjects(ingredients=result)
        except MenuItem.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list menu item ingredients: {str(e)}"
            )

    async def add_menu_item_ingredient(self, body: MenuItemIngredientCreateRequest, outlet) -> MenuItemIngredientObject:        
        try:
            menu_item = await MenuItem.objects.aget(slug=body.menu_item_slug)
            ingredient = await Ingredient.objects.aget(slug=body.ingredient_slug, outlet=outlet)
            mi = await MenuItemIngredient.objects.acreate(
                menu_item=menu_item,
                ingredient=ingredient,
                quantity=body.quantity
            )
            return MenuItemIngredientObject(
                menu_item_slug=mi.menu_item.slug,
                ingredient_slug=mi.ingredient.slug,
                quantity=float(mi.quantity),
                slug=mi.slug
            )
        except MenuItem.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found."
            )
        except Ingredient.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add menu item ingredient: {str(e)}"
            )

    async def update_menu_item_ingredient(self, slug: str, body: MenuItemIngredientUpdateRequest, outlet) -> MenuItemIngredientObject:        
        try:
            mi = await MenuItemIngredient.objects.aget(slug=slug)
            update_fields = body.dict(exclude_unset=True)
            for field, value in update_fields.items():
                if hasattr(mi, field):
                    setattr(mi, field, value)
            await mi.asave()
            ingredient = await get_related_object(mi, "ingredient")
            menu_item = await get_related_object(mi, "menu_item")
            return MenuItemIngredientObject(
                menu_item_slug=menu_item.slug,
                ingredient_slug=ingredient.slug,
                quantity=float(mi.quantity),
                slug=mi.slug
            )
        except MenuItemIngredient.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MenuItemIngredient mapping not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update menu item ingredient: {str(e)}"
            )

    async def delete_menu_item_ingredient(self, slug: str, outlet) -> dict:        
        try:
            mi = await MenuItemIngredient.objects.aget(slug=slug)
            await mi.adelete()
            return {"message": "MenuItemIngredient deleted successfully"}
        except MenuItemIngredient.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MenuItemIngredient mapping not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete menu item ingredient: {str(e)}"
            )

    async def list_transactions_for_outlet(self, outlet) -> InventoryTransactionObjects:        
        try:
            queryset = InventoryTransaction.objects.filter(outlet=outlet)
            transactions = await get_queryset(list, queryset)
            result = []
            for t in transactions:
                ingredient = await get_related_object(t, "ingredient")
                outlet = await get_related_object(t, "outlet")
                result.append(
                    InventoryTransactionObject(
                        ingredient_slug=ingredient.slug,
                        transaction_type=t.transaction_type,
                        quantity=float(t.quantity),
                        note=t.note,
                        outlet_slug=outlet.slug,
                        slug=t.slug
                    )
                )
            return InventoryTransactionObjects(transactions=result)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve transactions for outlet: {str(e)}"
            )

    async def list_transactions_for_ingredient(self, ingredient_slug: str, outlet) -> InventoryTransactionObjects:        
        try:
            ingredient = await Ingredient.objects.aget(slug=ingredient_slug, outlet=outlet)
            queryset = InventoryTransaction.objects.filter(ingredient=ingredient)
            transactions = await get_queryset(list, queryset)
            results = []
            for t in transactions:
                ingredient = await get_related_object(t, "ingredient")
                outlet = await get_related_object(t, "outlet")
                results.append(
                    InventoryTransactionObject(
                        ingredient_slug=ingredient.slug,
                        transaction_type=t.transaction_type,
                        quantity=float(t.quantity),
                        note=t.note,
                        outlet_slug=outlet.slug,
                        slug=t.slug
                    )
                )
            return InventoryTransactionObjects(transactions=results)        
        except Ingredient.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve transactions for ingredient: {str(e)}"
            )

    async def create_transaction(self, body: InventoryTransactionCreateRequest, outlet) -> InventoryTransactionObject:        
        try:
            ingredient = await Ingredient.objects.aget(slug=body.ingredient_slug, outlet=outlet)
            transaction = await InventoryTransaction.objects.acreate(
                ingredient=ingredient,
                transaction_type=body.transaction_type,
                quantity=body.quantity,
                note=body.note,
                outlet=outlet
            )
            return InventoryTransactionObject(
                ingredient_slug=transaction.ingredient.slug,
                transaction_type=transaction.transaction_type,
                quantity=float(transaction.quantity),
                note=transaction.note,
                outlet_slug=transaction.outlet.slug,
                slug=transaction.slug
            )
        except Ingredient.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create transaction: {str(e)}"
            )

    async def get_transaction_details(self, slug: str, outlet) -> InventoryTransactionObject:        
        try:
            transaction = await InventoryTransaction.objects.aget(slug=slug, outlet=outlet)
            ingredient = await get_related_object(transaction, "ingredient")            
            return InventoryTransactionObject(
                ingredient_slug=ingredient.slug,
                transaction_type=transaction.transaction_type,
                quantity=float(transaction.quantity),
                note=transaction.note,
                outlet_slug=outlet.slug,
                slug=transaction.slug
            )
        except InventoryTransaction.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve transaction details: {str(e)}"
            )

    async def update_transaction(self, slug: str, body: InventoryTransactionUpdateRequest, outlet) -> InventoryTransactionObject:        
        try:
            transaction = await InventoryTransaction.objects.aget(slug=slug, outlet=outlet)
            update_fields = body.dict(exclude_unset=True)
            for field, value in update_fields.items():
                if hasattr(transaction, field):
                    setattr(transaction, field, value)
            await transaction.asave()
            return InventoryTransactionObject(
                ingredient_slug=transaction.ingredient.slug,
                transaction_type=transaction.transaction_type,
                quantity=float(transaction.quantity),
                note=transaction.note,
                outlet_slug=transaction.outlet.slug,
                slug=transaction.slug
            )
        except InventoryTransaction.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update transaction: {str(e)}"
            )

    async def delete_transaction(self, slug: str, outlet) -> dict:        
        try:
            transaction = await InventoryTransaction.objects.aget(slug=slug, outlet=outlet)
            await transaction.adelete()
            return {"message": "Transaction deleted successfully"}
        except InventoryTransaction.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete transaction: {str(e)}"
            )

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