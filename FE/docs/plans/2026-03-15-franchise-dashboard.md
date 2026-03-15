# Phase 2: Franchise Public Presence & Management Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the public-facing outlet picker and the restricted franchise management suite with strict separation of public/private API calls.

**Architecture:** Context-aware routing. The subdomain root (`/`) is strictly public. `/admin` is strictly protected.

**Tech Stack:** React (Vite), Tailwind CSS v4, Lucide Icons, Axios.

---

### Task 1: Public Franchise Landing (COMPLETED)
- Use `GET /open/` for all content.
- Ensure zero calls to `/protected/` endpoints on this route.

---

### Task 2: Lazy Authentication & Admin Entry
**Files:**
- Modify: `FE/src/context/AuthContext.tsx`
- Modify: `FE/src/App.tsx`

**Logic:**
- Disable global blocking loading state in `AuthContext`.
- Move the `user-info` check to be a requirement for `/admin` routes only.
- If `/admin` returns 401, render the Login Page.

---

### Task 3: Internal Dashboard Home
**Files:**
- Create: `FE/src/pages/dashboard/FranchiseHome.tsx`

**Logic:**
- Operational overview of all outlets.
- Status badges for approval and active module subscriptions.

---

### Task 4: Multipart Outlet Creation
**Files:**
- Create: `FE/src/components/dashboard/CreateOutletModal.tsx`
- Create: `FE/src/components/ui/ImageUpload.tsx`

**Logic:**
- Handle `multipart/form-data` for image uploads.
- Real-time preview for `cover_image` and `mid_page_slider` array.

---

### Task 5: Team Management
**Files:**
- Create: `FE/src/pages/dashboard/TeamManagement.tsx`

**Logic:**
- Invite outlet admins via `POST /protected/auth/admin/outlet`.
- Link managers to specific locations.
