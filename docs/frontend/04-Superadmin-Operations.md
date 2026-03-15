# Superadmin & Franchise Guide

These endpoints manage the overarching business rules and hierarchy of Dishto, typically restricted to `Superadmin` or `Franchise Admin` roles.

## Franchise Admin Endpoints
- **Create Outlet:** `POST /restaurant/outlet`
  - Accepts `multipart/form-data` with an optional `cover_image` and an array of `mid_page_slider` images.
- **Get Outlets:** `GET /restaurant/outlet?slug=__all__`

## Superadmin Endpoints
- **Create Franchise:** `POST /restaurant/franchise/`
- **Get Franchises:** `GET /restaurant/franchise?slug=__all__`
- **Review System Feature Requests:** `GET /feature/admin/requests/?status_filter=pending`
- **Process Feature Approval/Rejection:** `PATCH /feature/admin/requests/{request_id}/`
  - **Important Note for Frontend Devs:** When a Superadmin approves a feature, this endpoint allows the formulation of custom/quoted `price` values to attach to the Subscription before it is provisioned through the system.
