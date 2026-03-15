# Public Customer Application

This covers endpoints meant for **End Users** visiting a Franchise subdomain (e.g., checking the menu, browsing items, placing an order). No JWT authentication is necessary here.

## Base URL Convention
Typically available under `/api/open` or defined via the `end_user_router`.

---

## 1. Fetching Locations (Outlets)
Before a customer selects a menu to view, they need to select what outlet they are visiting.

**Endpoint:** `GET /`
- **Dependencies:** Rate Limited `50/minute`. Automatically filters by the Franchise identified by the request domain mapping.
- **Returns:** A list of active, `superadmin_approved` outlets belonging to the Franchise.

---

## 2. Navigating the Menu

Once the user clicks into an `outlet_slug`, load the categories and items via the following endpoints:

#### Fetch Categories
**Endpoint:** `GET /category/{outlet_slug}`
- **Returns:** List of active `MenuCategory` objects for the specified outlet.

#### Fetch Full Menu
**Endpoint:** `GET /menu/{outlet_slug}`
- **Returns:** A complete dump of `MenuItemObjectsUser`, which bundles all categories and their items. Can be useful if building a single-page scrolling menu.

#### Fetch Items for Specific Category
**Endpoint:** `GET /menu/{outlet_slug}/{category_slug}/{slug}`
- **Note:** The parameter `{slug}` can target a specific item, while `__all__` could be passed if the design pattern aligns with the admin dashboard approach.

---

## 3. Intelligent Semantic Search

Dishto integrates AI Vector search (via Qdrant) so users can search using natural language (e.g., "something spicy for dinner").

**Endpoint:** `GET /menu/{outlet_slug}/search/contextual`
- **Query Params:** `?query=something spicy`
- **Returns:** Enhanced contextual mapping matching `MenuItem` descriptions and embeddings against the user intent instead of just flat string matching.
