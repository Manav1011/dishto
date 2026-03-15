# Dishto Frontend Guide: Core Architecture & Setup

Welcome to the Dishto frontend documentation. This guide focuses strictly on what you need as a frontend developer: the API endpoints, data flow, architecture mechanics, and authentication.

## 1. Multi-tenant Architecture (Franchise & Outlets)

Dishto uses a hierarchical structure:
* **Franchise:** The master entity (e.g., `Dominos`). Franchises are mapped using completely separate subdomains (e.g., `dominos.dishto.live`).
* **Outlet:** Individual restaurants or branches that belong to a franchise (e.g., `Dominos Navrangpura`). They are identified by slugs in the path.
* For the frontend, **all incoming requests** MUST be able to handle subdomain routing. The backend determines the current active franchise based on the request subdomain context.

> **💡 Best Practice:** Many endpoints require `outlet_slug` in the URL path, effectively making the frontend structure reflect `{subdomain}.dishto.live/{outlet_slug}/...`

## 2. Authentication Strategy

Dishto uses **JWT (JSON Web Tokens)**, but the tokens are stored securely in **HttpOnly Cookies**.
* **You do not need to manually parse or store tokens in `localStorage` or `sessionStorage`.**
* Make sure all requests from the frontend client to the backend include credentials (e.g., in Axios: `withCredentials: true` or natively using `credentials: "include"`).

### Roles
The backend enforces Role-Based Access Control (RBAC):
- **Superadmin:** Can create Franchises and approve Feature requests for all outlets globally.
- **Franchise Admin:** Can create Outlets under their given Franchise.
- **Outlet Admin:** Can manage menus, inventory, process orders, and request feature subscriptions for a specific Outlet.
- **End User (Public):** No authentication needed. Hits the open customer-facing endpoints via rate limiters.

## 3. The Feature Subscription Model (CRITICAL)

The Dishto platform separates modules (like Menu, Ordering, and Inventory) into **Feature Subscriptions**.
* Outlets are not given access to the Menu, Ordering, or Inventory by default.
* Every protected endpoint expects a specific active feature subscription.
* For example, accessing a Menu endpoint for creating an item requires the `menu` feature.

### Mechanics Flow
1. **Outlet Admin View:** Submits a `OutletFeatureRequest` (Add or Remove) to the backend. Status is `pending`.
2. **Superadmin View:** Evaluates request, optionally sets a custom `price` for the feature, and marks the request as `approved`.
3. **Activation:** Code automatically records it in the `OutletFeatureHistory`, mapping the `Outlet` to the `GlobalFeature` with a specific price. This becomes an active `OutletFeature`.
4. **Backend Validation:** Any restricted endpoint executes `require_feature("menu")` middleware to block `403 Forbidden` if it's unauthorized.

---
**Next Step:** Check out the specific guide depending on which application you are building:
- `02-Public-Customer-App.md`: For the open end-user catalog interface.
- `03-Outlet-Admin-Dashboard.md`: For the protected restaurant management operations.
- `04-Superadmin-Operations.md`: For global master admin tasks.
