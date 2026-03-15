# Recommended Frontend Build Order

When building the Dishto frontend, it is crucial to follow the dependencies set by the backend architecture. Building out of order will result in endpoints failing because their prerequisite data (like an active Franchise, an authenticated Session, or an approved Feature Subscription) doesn't exist yet.

Here is the recommended phase-by-phase implementation plan for the frontend team:

---

## Phase 1: Core Foundation & Superadmin Portal
**Goal:** Establish the multi-tenant routing, authentication state, and the master data layer.

1. **Subdomain Routing Setup:** Configure the frontend application to parse and utilize `window.location.hostname` to extract the `franchise` string for routing logic.
2. **Authentication Flow (`Profile` Module):**
   - Build the `/login` page and configure the HTTP client (e.g., Axios) to correctly accept `HttpOnly` cookies (`withCredentials: true`).
   - Build the `/auth/user-info` context provider to wrap the application and guard protected routes.
   - Build the `/setup` password creation page.
3. **Superadmin Dashboard:**
   - Build the "Create Franchise" and "Create Franchise Admin" forms.
   - Build the "Feature Subscriptions Approval" queue.
   - *Checkpoint:* You can now manually create a Franchise (e.g., `dominos`) and log in as its Admin.

---

## Phase 2: Franchise Admin Dashboard
**Goal:** Allow the newly created Franchise to set up its physical restaurant locations.

1. **Outlet Management (`core` Module):**
   - Build the Franchise Admin portal home page.
   - Build the "Create Outlet" multipart form (handling the `cover_image` and `mid_page_slider` image arrays).
   - Build the "Create Outlet Admin" interface.
   - *Checkpoint:* You can now navigate to `dominos.dishto.live`, log in as the newly created Outlet Admin, and see the specific Outlet dashboard.

---

## Phase 3: Outlet Admin - Feature Subscriptions & Inventory
**Goal:** Activate the required modules and establish the fundamental building blocks (raw ingredients) before building recipes.

1. **Subscription Management:**
   - Build the "Feature Shop" where the Outlet Admin requests the `inventory`, `menu`, and `ordering` features.
   - *(Wait for Superadmin approval in Phase 1 dashboard).*
2. **Inventory Foundation (`Inventory` Module):**
   - Build the raw Ingredient management table (Create/Update/Activate rules).
   - Build the Inventory Transaction logger (logging physical stock deliveries or wastage).
   - *Checkpoint:* The database now has active Outlets with raw stock (e.g., 50kg of flour, 20L of milk) ready to be attached to Menu Items.

---

## Phase 4: Outlet Admin - Menu Builder
**Goal:** Create the digital assets that the end customers will see, hooking them up to the Phase 3 Inventory.

1. **Category Management (`Menu` Module):**
   - Build the drag-and-drop/ordered list for `MenuCategory` creation.
2. **Item Management & AI Creation:**
   - Build the "Create/Edit Menu Item" form.
   - Implement the "No Image" (AI-generated image) and "AI Description Enhancer" UI tools.
3. **Recipe Linking (Integration):**
   - Build the interface inside the Menu Item view that allows the Admin to link Phase 3 Ingredients to the item (e.g., 1 Pizza requires 200g of flour).
   - *Checkpoint:* The menu is fully built, visually appealing via AI, and mapped securely to real-world stock.

---

## Phase 5: Public Customer App & Ordering
**Goal:** Launch the public-facing storefront and close the loop by generating orders that deplete the inventory.

1. **Public Catalog (`end_user_router`):**
   - Build the Location Gateway (Outlet Picker).
   - Build the Main Digital Menu, fetching `MenuItemObjectsUser` and displaying the `mid_page_slider` images.
   - Implement the Qdrant-powered Contextual AI Search Bar.
2. **Cart & Checkout (`Ordering` Module):**
   - Build the shopping cart state.
   - Build the Checkout interface that fires the `POST /ordering/{outlet_slug}/orders` endpoint.
   - Build the Order Success/Confirmation page.
3. **Live Order Board:**
   - Go back to the Outlet Admin Dashboard and build the live view to monitor incoming orders.
   - *Checkpoint:* The entire system is functional. An end user places an order, the Outlet Admin sees it arrive, and the backend automatically depletes the exact raw ingredients defined in Phase 4 from the stock logged in Phase 3.
