# Superadmin Portal Implementation Plan (COMPLETED)

**Goal:** Build a complete, functional Superadmin portal with Franchise management and Feature approval.

**Architecture:** Centralized React state with a Shell Layout pattern for persistent navigation. Flat routing structure for maximum reliability.

**Tech Stack:** React (Vite), Tailwind CSS v4, Lucide Icons, Axios.

---

### Phase 1 Infrastructure & Utilities (Added during execution)

**1. Subdomain & Local Dev Strategy**
- Implemented `subdomain.ts` utility supporting `dishto.in`, `lvh.me`, and a `LOCAL_DEV_OVERRIDE` for `localhost` testing.
- Configured Vite Proxy in `vite.config.ts` to handle CORS by routing `/api` to `https://dishto.in`.

**2. Authentication Layer**
- Created `AuthContext` with role mapping (e.g., `extras.superadmin` -> `superadmin`).
- Developed `ProtectedRoute` component for RBAC (Role-Based Access Control).

**3. System Health**
- Added a persistent "API Health Indicator" floating pill to monitor backend connectivity.

---

### Task 1: Superadmin Layout Shell (Completed)
- Persistent sidebar with navigation to Franchise Network, Feature Requests, and Settings.
- Glassmorphic design with `overflow-x-hidden` and `shrink-0` fixes to prevent global scrollbars.
- User profile summary and Logout logic.

### Task 2: Franchise Directory (Completed)
- Table-based view of registered franchises.
- **Note:** Removed "Primary Contact" column as the current API does not return admin details in the list view.
- Added internal table scrolling (`min-w-[800px]`) to keep the sidebar fixed on small screens.
- Polished "Empty State" with CTA for first-time setup.

### Task 3: Register Franchise Modal (Completed)
- Multi-step form flow:
  1. **Franchise Info:** Captures name (POST `/restaurant/franchise/`).
  2. **Admin Info:** Captures email and links to the new franchise slug (POST `/auth/admin/franchise`).

### Task 4: Feature Request Queue (Completed)
- Filterable list (Pending, Approved, Rejected) of outlet module requests.
- Integrated `prices` mapping during approval to set custom module pricing.
- Integrated `note` capture for rejection feedback.

### Task 5: Profile & Password Settings (Completed)
- Self-service interface for updating name, email, and phone.
- Secure password change interface with confirmation logic.
