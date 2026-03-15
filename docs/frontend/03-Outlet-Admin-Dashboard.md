# Outlet Admin Dashboard Guide

This covers endpoints used by the **Outlet Admin** to configure their restaurant, menus, inventory, subscriptions, and process orders.
**Important:** All endpoints below require JWT Authentication via Cookies and assume the Outlet Admin has the requested feature subscription enabled.

---

## 1. Feature Subscriptions

Before accessing functionalities, an Outlet Admin can manage what modules their restaurant is paying for.

- **Check Available Master Features:** `GET /feature/available`
- **Check Active Enabled Features:** `GET /feature/outlet/{outlet_slug}/active-features` (Also returns the custom price of each feature).
- **Request Add/Remove Feature:** `POST /feature/outlet/{outlet_slug}/requests/`
  - Payload requires a request to "add" or "remove" features. Enters a `pending` state awaiting a Superadmin.
- **List Past/Pending Requests:** `GET /feature/outlet/{outlet_slug}/requests/`

---

## 2. Menu Module
*Requires the `menu` subscription feature.*

### Managing Categories
- **Create:** `POST /menu/{outlet_slug}/categories`
- **List/Get:** `GET /menu/{outlet_slug}/categories?slug=__all__`
- **Update:** `PUT /menu/{outlet_slug}/categories/{slug}`
- **Delete:** `DELETE /menu/{outlet_slug}/categories/{slug}`
- **Rearrange GUI Order:** `POST /menu/{outlet_slug}/categories/rearrange_display_order`
- **Search:** `GET /menu/{outlet_slug}/categories/search?query=name`

### Managing Items
Menu items utilize multipart form payloads for Image Uploads.

- **Create standard item:** `POST /menu/{outlet_slug}/items` (Expects `image` file along with form data).
- **Create via AI (No Image):** `POST /menu/{outlet_slug}/items/no-image`
  - *Magic:* Uses Gemini to automatically build a photorealistic image based on `name` and `description`. Send as standard JSON request.
- **AI Description Enhancer:** `GET /menu/{outlet_slug}/items/enhance_description_with_ai?item_name=Pizza&description=good`
- **List/Get:** `GET /menu/{outlet_slug}/items?category_slug={cat}&slug={item_slug_or_all}`
- **Update with Image:** `PUT /menu/{outlet_slug}/items/{category_slug}/{slug}` (Multipart)
- **Update text only:** `PATCH /menu/{outlet_slug}/items/{category_slug}/{slug}` (JSON format)
- **Upload Image Later:** `POST /menu/{outlet_slug}/items/upload-image/{category_slug}/{slug}`
- **Reorder within Category:** `POST /menu/{outlet_slug}/items/{category_slug}/rearrange_display_order`
- **Add 'Like' on Item:** `PATCH /menu/{outlet_slug}/items/{category_slug}/{slug}/like` (Rate limited 1/minute)

---

## 3. Inventory Module
*Requires the `inventory` subscription feature.*

### Ingredients (Raw Stock)
- **Create:** `POST /inventory/{outlet_slug}/ingredients`
- **Update:** `PUT /inventory/{outlet_slug}/ingredients/{slug}`
- **Activate/Deactivate:** `PATCH /inventory/{outlet_slug}/ingredients/{slug}/activate`
- **List:** `GET /inventory/{outlet_slug}/ingredients?slug=__all__`

### Recipes (Mapping Menus to Stock)
- **Add mapping:** `POST /inventory/{outlet_slug}/menu_item/ingredient` (e.g., requires 5g of cheese)
- **List mapping:** `GET /inventory/{outlet_slug}/menu_item/{menu_item_slug}/ingredients`

### Inventory Transactions (Wastage / Audit / Adjustment)
- **Create Transaction:** `POST /inventory/{outlet_slug}/transactions`
- **List All:** `GET /inventory/{outlet_slug}/transactions`
- **List per Ingredient:** `GET /inventory/{outlet_slug}/ingredient/{ingredient_slug}/transactions`

---

## 4. Ordering Module
*Requires the `ordering` subscription feature.*

The Ordering feature is tightly integrated. If the system has `inventory` feature active alongside `ordering`, creating an order automatically deducts the stock values correctly via transactions based on the recipe map.

- **Create Order:** `POST /ordering/{outlet_slug}/orders`
