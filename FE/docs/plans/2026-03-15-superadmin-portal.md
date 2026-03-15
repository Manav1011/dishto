# Superadmin Portal Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete, functional Superadmin portal with Franchise management and Feature approval.

**Architecture:** Centralized React state with a Shell Layout pattern for persistent navigation.

**Tech Stack:** React (Vite), Tailwind CSS v4, Lucide Icons, Axios.

---

### Task 1: Superadmin Layout Shell

**Files:**
- Create: `FE/src/layouts/SuperAdminLayout.tsx`
- Modify: `FE/src/App.tsx`

**Logic:**
- Persistent sidebar with navigation.
- User profile summary and Logout button.
- Subdomain-aware route protection.

---

### Task 2: Franchise Directory Enhancements

**Files:**
- Modify: `FE/src/pages/superadmin/FranchiseDirectory.tsx`

**Logic:**
- Integrate "Register Franchise" trigger.
- Add "Empty State" with CTA.
- Polish table rows with animations (Framer Motion).

---

### Task 3: Register Franchise Modal

**Files:**
- Create: `FE/src/components/superadmin/CreateFranchiseModal.tsx`

**Logic:**
- Multi-step form:
  1. Franchise Info (Name).
  2. Admin User Info (Email, Name).
- Success feedback and list refresh.

---

### Task 4: Feature Request Queue

**Files:**
- Create: `FE/src/pages/superadmin/FeatureRequests.tsx`
- Modify: `FE/src/App.tsx`

**Logic:**
- List all `pending` OutletFeatureRequests.
- Approval interface with `price` input.
- Rejection interface with `note` input.

---

### Task 5: Profile & Password Settings

**Files:**
- Create: `FE/src/pages/auth/ProfileSettings.tsx`

**Logic:**
- Update Profile Info (POST /auth/update-profile).
- Change Password (POST /auth/update-password).
