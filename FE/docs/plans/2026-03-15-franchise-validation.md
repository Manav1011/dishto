# Franchise Validation & Error Handling Plan

**Goal:** Detect unregistered subdomains and display a premium "Brand Not Found" page.

**Architecture:** Utilize the 404 response from the backend's `FranchiseMiddleware` to trigger a global error state in the React application.

**Tech Stack:** React, Tailwind CSS v4, Lucide Icons.

---

### Task 1: Brand Not Found Component
**Files:**
- Create: `FE/src/pages/public/BrandNotFound.tsx`

**UI Logic:**
- Sleek error state with "Vyahan" styling.
- "We couldn't find this brand" message.
- Redirect button to the main `dishto.in` portal.

---

### Task 2: AuthContext Error Handling
**Files:**
- Modify: `FE/src/context/AuthContext.tsx`

**Logic:**
- Add `brandNotFound: boolean` to the context state.
- In `fetchUserInfo`, catch 404 errors from the backend.
- If a 404 occurs on a subdomain (excluding 'admin'), set `brandNotFound` to `true`.

---

### Task 3: Global Route Guard
**Files:**
- Modify: `FE/src/App.tsx`

**Logic:**
- Read `brandNotFound` from `useAuth()`.
- If `true`, override all routing to show the `BrandNotFound` component.
- Ensure the API health indicator still shows the correct status.
