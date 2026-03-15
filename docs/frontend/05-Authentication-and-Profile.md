# Authentication & Profile Guide

This guide covers the endpoints meant for handling user sessions, authentication, and profile updates. The authentication is powered by **JWT (JSON Web Tokens)** that are securely stored in **HttpOnly Cookies**.

**Important Note for Frontend Developers:**
Because the backend issues tokens as `HttpOnly`, `Secure`, and `SameSite=none` cookies, you do **not** have to manually store them in `localStorage` or append headers to your requests. They will be automatically sent by the browser. Just make sure to configure your HTTP client (e.g., Axios) to include credentials (`withCredentials: true`).

## Base URL Convention
Typically available under `/auth` or `/api/protected/auth`.

---

## 1. Authentication Endpoints

#### Login
**Endpoint:** `POST /auth/login`
- **Payload:** Requires user credentials (e.g., `email` and `password`).
- **Response:** The backend returns an HTTP response containing tokens in the body, but more importantly, attaches the `access` and `refresh` tokens as secure cookies.

#### Logout
**Endpoint:** `POST /auth/logout`
- **Response:** Removes both the `access` and `refresh` cookies from the browser, effectively terminating the session.

#### Refresh Token
**Endpoint:** `POST /auth/refresh`
- **Description:** When the `access` token expires, the frontend can hit this endpoint. The backend will read the `refresh` cookie, issue a fresh pair of tokens, and inject them as new cookies.

---

## 2. Profile Management

These endpoints require the user to be fully authenticated.

#### Get Current User Info
**Endpoint:** `GET /auth/user-info`
- **Returns:** The profile information and Role (e.g., `franchise_admin`, `outlet_admin`) of the presently logged-in user.

#### Update Profile Information
**Endpoint:** `POST /auth/update-profile`
- **Payload:** Data object containing the fields to update (e.g., `first_name`, `last_name`, `phone`).

#### Update Password
**Endpoint:** `POST /auth/update-password`
- **Payload:** typically requires `old_password` and `new_password`.

#### Set Password
**Endpoint:** `POST /auth/set-password`
- **Description:** Normally used to establish a password the very first time an account finishes setup operations.

---

## 3. Superadmin/Franchise Admin Account Creation
These endpoints are strictly for generating new manager accounts.

- **Create Franchise Admin:** `POST /auth/admin/franchise` (Requires Superadmin role).
- **Create Outlet Admin:** `POST /auth/admin/outlet` (Requires Franchise Admin role).
