# Phase 3A: Outlet Administrative Gateway Implementation Plan

> **For Claude:** REQUIRED: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the foundational Dashboard Layout and Authentication loop exclusively for Individual Outlet Branches.

**Architecture:** Use React Router scoped under `/:outlet_slug/admin` protecting the branch management zone securely, utilizing `is_outlet_admin` protections while building a localized sidebar and overview data. 

**Tech Stack:** React (Vite), Tailwind CSS v4, Lucide Icons, Axios.

---

### Task 1: Scoped Outlet Authentication (Login)

**Files:**
- Create: `FE/src/pages/outlet/OutletLogin.tsx`
- Modify: `FE/src/App.tsx`

- [ ] **Step 1: Create OutletLogin Component**
Create a login screen specifically parameterized to read `outlet_slug` from the URL, showing branch context on the login card. It should share the API authentication call but hit a specific redirect to the branch home upon success.

- [ ] **Step 2: Add OutletAdmin Login Route**
Update `App.tsx` to include `<Route path="/:outlet_slug/admin/login" element={<OutletLogin />} />` right before the generic fallbacks.

- [ ] **Step 3: Test Isolation**
Ensure that visiting `ldce.dishto.in/123/admin/login` renders the specific login screen correctly without bleeding into Superadmin/Franchise generic loggers.

---

### Task 2: Build the Outlet Management Layout

**Files:**
- Create: `FE/src/layouts/OutletLayout.tsx`

- [ ] **Step 1: Scaffold OutletLayout Shell**
Create a new layout identical in structural quality to `FranchiseLayout` but featuring a Sidebar explicitly tailored to Outlet Managers.
Include links for: `Overview`, `Live Orders` (locked if feature inactive), `Menu Catalog`, and `Inventory` (locked if inactive).

- [ ] **Step 2: Sidebar Security & Data Hydration**
Fetch the specific Outlet DB row inside the layout to populate the Sidebar Header with the specific Branch Name (e.g. "Computer Department") instead of the Parent Franchise.

---

### Task 3: Branch Overview Metrics (Home Page)

**Files:**
- Create: `FE/src/pages/outlet/OutletOverview.tsx`
- Modify: `FE/src/App.tsx`

- [ ] **Step 1: Scaffold Overview Page**
Develop the root content component for `/admin` under the branch location. This will display daily snapshot grids: Active KOTs, Low Stock warnings, and Quick Actions to jump into the active modules.

- [ ] **Step 2: Register Guarded Route Tree**
Map `<OutletLayout>` and `<OutletOverview>` wrapped inside a strict `<ProtectedRoute allowedRoles={['outlet_owner']}>` into `App.tsx` precisely targeting `path="/:outlet_slug/admin"`.

- [ ] **Step 3: Test Layout Protection**
Navigate to `/:outlet_slug/admin` as an unauthenticated user and ensure it forces a redirect specifically to `/:outlet_slug/admin/login`. Log in as a Manager and verify the Overview dashboard mounts.

---

### Task 4: Setup Feature Flag Constraints (Prep for 3B/3C)

**Files:**
- Modify: `FE/src/layouts/OutletLayout.tsx`

- [ ] **Step 1: Read Live Features Array**
During the layout boot, hit the `GET /protected/feature/outlet/{outlet_slug}/active-features` endpoint to fetch the subscribed modules list.

- [ ] **Step 2: Conditionally Render Sidebar Tabs**
Disable or hide the `Inventory` or `Ordering` tabs dynamically if the API array does not return those specific slugs. This prevents branch managers from accessing features the franchise hasn't purchased for them.
