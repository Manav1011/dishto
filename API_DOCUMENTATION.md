# Dishto API Documentation

This document provides a detailed reference for the available API endpoints in the Dishto platform. The APIs are organized by module.

## ⚠️ Important: Feature-Based Access Control

Many protected API endpoints in Dishto are subject to **feature-based access control**. This means an authenticated Outlet Admin can only access functionalities (like managing the menu, inventory, or orders) if their outlet has an active subscription to the corresponding feature.

*   **Access Denied:** Attempts to access endpoints for features that are not enabled for an outlet will result in a `403 Forbidden` HTTP status code.
*   **Feature Management:** Outlet Admins can request to add or remove features, which must then be approved by a Superadmin. Superadmins also set the custom pricing for each feature subscription.

---

## 🔒 Authentication & Profile Module
**Base URL:** `/api/protected/auth`

These endpoints handle user authentication using JWT stored in secure cookies, as well as profile management tasks.

### Authentication
*   **POST** `/login`
    *   **Description:** Authenticates a user with credentials. Sets `access` and `refresh` tokens as HttpOnly, Secure cookies.
*   **POST** `/logout`
    *   **Description:** Logs out the user by clearing the authentication cookies.
*   **POST** `/refresh`
    *   **Description:** Uses the existing refresh cookie to issue a new access token.
*   **GET** `/user-info`
    *   **Description:** Retrieves detailed profile information for the currently logged-in user.

### Account Management
*   **POST** `/set-password`
    *   **Description:** Sets a password for a user (typically used for first-time setup).
*   **POST** `/update-password`
    *   **Description:** Updates the logged-in user's password. Requires current password verification.
*   **POST** `/update-profile`
    *   **Description:** Updates general profile information for the logged-in user.

### Admin Tools
*   **POST** `/admin/franchise`
    *   **Access:** Superadmin only.
    *   **Description:** Creates a new administrator account for a Franchise.
*   **POST** `/admin/outlet`
    *   **Access:** Franchise Admin only.
    *   **Description:** Creates a new administrator account for a specific Outlet.

---

## ✨ Feature Management Module
**Base URL:** `/api/protected/feature`

This module provides endpoints for managing feature subscriptions for outlets.

*   **GET** `/available`
    *   **Description:** Retrieve a list of all master features available in the system.
*   **GET** `/outlet/{outlet_slug}/active-features`
    *   **Access:** Outlet Admin only.
    *   **Description:** List all features currently enabled for the specified outlet, including their custom subscription prices.
*   **POST** `/outlet/{outlet_slug}/requests`
    *   **Access:** Outlet Admin only.
    *   **Description:** Submit a request to add or remove a feature for the specified outlet. Requests enter a 'pending' state.
*   **GET** `/outlet/{outlet_slug}/requests`
    *   **Access:** Outlet Admin only.
    *   **Description:** Retrieve all feature requests (pending, approved, rejected) made for the specified outlet.
*   **GET** `/admin/requests`
    *   **Access:** Superadmin only.
    *   **Description:** List all feature requests across all outlets. Can be filtered by status (e.g., 'pending').
*   **PATCH** `/admin/requests/{request_id}`
    *   **Access:** Superadmin only.
    *   **Description:** Approve or reject a specific feature request. When approving, the Superadmin can optionally set custom prices for the requested features.

---

## 🍽️ Restaurant & Menu Management Module
This module manages the core business hierarchy (Franchises, Outlets) and the Menu (Categories, Items).

### Franchise & Outlet Management
**Base URL:** `/api/protected/restaurant`

*   **POST** `/franchise/`
    *   **Description:** Create a new Franchise.
*   **GET** `/franchise`
    *   **Description:** Retrieve franchise details. Supports querying a specific slug or `__all__`.
*   **POST** `/outlet`
    *   **Description:** Create a new Outlet. Supports multipart upload for `cover_image` and `mid_page_slider` images.
*   **GET** `/outlet`
    *   **Description:** Retrieve outlet details.

### Menu Management
**Base URL:** `/api/protected/menu`
**Access:** Requires `menu` feature subscription for the outlet.

*   **POST** `/{outlet_slug}/categories`
    *   **Description:** Create a new menu category (e.g., "Starters", "Mains").
*   **GET** `/{outlet_slug}/categories`
    *   **Description:** List categories for an outlet.
*   **GET** `/{outlet_slug}/categories/search`
    *   **Description:** Search for categories by name or description.
*   **PUT** `/{outlet_slug}/categories/{slug}`
    *   **Description:** Update an existing category.
*   **DELETE** `/{outlet_slug}/categories/{slug}`
    *   **Description:** Delete a category.
*   **POST** `/{outlet_slug}/categories/rearrange_display_order`
    *   **Description:** Change the visual order in which categories appear in the menu.
*   **POST** `/{outlet_slug}/items`
    *   **Description:** Create a standard menu item with an image upload.
*   **POST** `/{outlet_slug}/items/no-image`
    *   **Description:** **(AI Powered)** Create a menu item *without* providing an image. The system automatically uses Google Gemini to generate a photorealistic image based on the item description.
*   **GET** `/{outlet_slug}/items/enhance_description_with_ai`
    *   **Description:** **(AI Powered)** Takes a basic food name/description and returns a marketing-enhanced, appetizing description generated by AI.
*   **GET** `/{outlet_slug}/items`
    *   **Description:** List menu items. Can filter by category.
*   **GET** `/{outlet_slug}/items/search`
    *   **Description:** Search menu items by name.
*   **PUT** `/{outlet_slug}/items/{category_slug}/{slug}`
    *   **Description:** Update a menu item (supports multipart form for image updates).
*   **PATCH** `/{outlet_slug}/items/{category_slug}/{slug}`
    *   **Description:** Update a menu item via JSON (no image update).
*   **POST** `/{outlet_slug}/items/upload-image/{category_slug}/{slug}`
    *   **Description:** Upload a specific image for an existing menu item.
*   **PATCH** `/{outlet_slug}/items/{category_slug}/{slug}/like`
    *   **Description:** Increment the "popularity" or like count of an item.
*   **POST** `/{outlet_slug}/items/{category_slug}/rearrange_display_order`
    *   **Description:** Change the order of items within a specific category.

---

## 📦 Inventory Module
**Base URL:** `/api/protected/inventory`
**Access:** Requires `inventory` feature subscription for the outlet.

Manages stock, recipes, and inventory logging.

### Ingredients
*   **POST** `/{outlet_slug}/ingredients`
    *   **Description:** Create raw ingredients (e.g., "Tomato", "Cheese").
*   **GET** `/{outlet_slug}/ingredients`
    *   **Description:** List ingredients.
*   **PUT** `/{outlet_slug}/ingredients/{slug}`
    *   **Description:** Update ingredient details.
*   **DELETE** `/{outlet_slug}/ingredients/{slug}`
    *   **Description:** Delete an ingredient.
*   **PATCH** `/{outlet_slug}/ingredients/{slug}/activate`
    *   **Description:** Toggle an ingredient as active/inactive.

### Recipes (Menu Item Linking)
*   **GET** `/{outlet_slug}/menu_item/{menu_item_slug}/ingredients`
    *   **Description:** View the recipe (listed ingredients) for a specific menu dish.
*   **POST** `/{outlet_slug}/menu_item/ingredient`
    *   **Description:** Add an ingredient and quantity to a menu item's recipe.
*   **PUT** `/{outlet_slug}/menu_item/ingredient/{slug}`
    *   **Description:** Update the quantity of an ingredient in a recipe.
*   **DELETE** `/{outlet_slug}/menu_item/ingredient/{slug}`
    *   **Description:** Remove an ingredient from a recipe.

### Transactions
*   **GET** `/{outlet_slug}/transactions`
    *   **Description:** View the full history of inventory changes (Purchases, Wastage, etc.).
*   **GET** `/{outlet_slug}/ingredient/{ingredient_slug}/transactions`
    *   **Description:** View inventory history for a specific ingredient.
*   **POST** `/{outlet_slug}/transactions`
    *   **Description:** Log a new inventory event (e.g., "Purchased 10kg of Rice").
*   **GET** `/{outlet_slug}/transactions/{slug}`
    *   **Description:** Retrieve details for a specific inventory transaction.
*   **PUT** `/{outlet_slug}/transactions/{slug}`
    *   **Description:** Update an inventory transaction.
*   **DELETE** `/{outlet_slug}/transactions/{slug}`
    *   **Description:** Delete an inventory transaction.

---

## 🧾 Ordering Module
**Base URL:** `/api/protected/ordering`
**Access:** Requires `ordering` feature subscription for the outlet.

*   **POST** `/{outlet_slug}/orders`
    *   **Description:** Create a new customer order. This endpoint now **conditionally triggers stock deduction** based on the recipes defined in the Inventory module: if the outlet does not have the `inventory` feature enabled, no inventory transactions will be recorded.

---

## 🌐 Public End-User Module
**Base URL:** `/api/open`

These endpoints are public (no authentication required) and are optimized for customers utilizing the digital menu.

*   **GET** `/` (Get Outlets)
    *   **Description:** Retrieve all active outlets for the current Franchise.
*   **GET** `/category/{outlet_slug}`
    *   **Description:** Get the list of menu categories for an outlet.
*   **GET** `/menu/{outlet_slug}`
    *   **Description:** Get the full menu (items and categories) for an outlet.
*   **GET** `/menu/{outlet_slug}/{category_slug}/{slug}`
    *   **Description:** Get details for a specific single menu item.
*   **GET** `/menu/{outlet_slug}/search/contextual`
    *   **Description:** **(Semantic Search)** Search for items using natural language (e.g., "something spicy for dinner"). Uses Vector Search (Qdrant) to match user intent with dish descriptions.
