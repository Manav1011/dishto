# Defined UI Pages

Based on the functionality exposed via the APIs, here is the breakdown of the user interfaces we will need for the platform, organized by the role that accesses them.

---

## 1. Dishto Superadmin Portal
This portal is accessed by system administrators building and managing the Dishto network.
- **Login screen**: Authentication entry point.
- **Franchise directory**: A table/list view showing all registered franchises.
- **Create franchise modal/page**: Form to create a new franchise.
- **Feature subscriptions approval queue**: A page to view all `pending`, `approved`, and `rejected` OutletFeatureRequests. Should allow the superadmin to set custom pricing (`price`) and approve the request.

---

## 2. Franchise Admin Dashboard
This portal is accessed by the owners of a specific franchise (e.g., the owner of all "Dominos" chains) to manage their underlying locations.
- **Login screen**: Authentication entry point.
- **Outlet directory**: A map or table showing all created outlets for this specific franchise. Includes their approval status.
- **Create outlet page**: A complex form to define a new outlet. Must support uploading the `cover_image` and an array of `mid_page_slider` images via multipart forms.
- **Outlet details view**: A summary of a single outlet's configuration, their assigned admin, and active feature subscriptions.
- **Create Outlet Admin**: Interface to invite/create a new admin profile specifically bound to an outlet.

---

## 3. Outlet Admin Dashboard (The Restaurant Manager)
This is the heavily featured core management dashboard. An admin of a specific outlet accesses this to run day-to-day operations.

### General & Setup
- **Login screen**: Authentication entry point.
- **Outlet dashboard (Home)**: High-level metrics, active modules, and quick actions.
- **Feature shop / Subscription management**: A page where the outlet admin can see available features ("Inventory", "Menu", "Ordering"), request to activate/deactivate them, and view their currently active subscriptions with pricing.

### Menu Module (Only if `menu` feature is active)
- **Menu builder (Categories list)**: Drag-and-drop or ordered list to view and arrange `MenuCategory` items. Includes a "Create Category" modal.
- **Menu builder (Items list)**: A page showing items inside a specific category. Includes the ability to rearrange the display order of items.
- **Create / Edit Menu Item**: A form for defining an item (price, description, availability). Needs a toggle or specific flow for:
  - **Standard**: Uploading a physical image.
  - **AI Magic**: Generating a photorealistic image using the Google Gemini integration.
- **AI Description Enhancer**: A small utility/button within the Item Edit page to automatically rewrite basic food descriptions into appetizing marketing copy.

### Inventory Module (Only if `inventory` feature is active)
- **Ingredients master list**: Table showing all raw stock items, adjusting their active status, or creating a new raw ingredient.
- **Recipe builder**: A sub-page on a Menu Item that maps raw ingredients and exact quantities to that specific dish.
- **Stock transactions log**: A ledger showing all additions, wastage, or subtractions of stock over time.
- **Log physical inventory**: Form to manually adjust stock levels (e.g., logging a new delivery or recording spoiled goods).

### Orders Module (Only if `ordering` feature is active)
- **Live order board (KDS or equivalent)**: A real-time view of incoming, processing, and completed orders placed by customers.

---

## 4. Public Customer Facing Application
This is what the end-users see when they attempt to browse a restaurant's digital menu or order food under a franchise's specific subdomain (e.g., `dominos.dishto.live`).

- **Location picker page (Gateway)**: A landing page shown if the user goes to the root domain. Prompts the user to select which specific outlet they are currently visiting (e.g., "Dominos Navrangpura").
- **Digital menu (Main View)**: The core catalog showing menu categories as tabs/sections and the menu items beneath them with images, prices, and descriptions.
- **Item details / Customize modal**: Popping up a specific item to read the expanded description and perhaps view current offers/discounts.
- **Contextual AI search bar**: A highly visible search input leveraging Qdrant vector search so customers can type natural phrases like, "Something sweet and crispy" instead of just exact dish names.
- **Cart & Checkout interface**: (Assumes `ordering` feature active) Reviewing selected items and placing the `OrderCreateRequest` which automatically handles inventory depletion on the backend.
