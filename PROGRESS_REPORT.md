# Dishto Project - Progress Report & Status

## Project Overview
**Dishto** is a modern, high-performance restaurant management platform built on a hybrid backend architecture. It leverages **Django (5.2)** for robust data modeling and administration, integrated with **FastAPI (0.115)** for high-speed, asynchronous API endpoints. The system acts as a multi-tenant platform managing Franchises, Outlets, Menus, and Inventory with advanced AI capabilities.

---

## ✅ Completed Modules & Features

### 1. Core Infrastructure & Architecture
*   **Hybrid Backend**: Successfully integrated Django ORM with FastAPI router mounting.
*   **Multi-Tenancy**: Implemented `FranchiseMiddleware` to dynamically serve specific Franchise data based on subdomains (e.g., `store.dishto.in`), with a fallback for local development.
*   **Authentication & Security**:
    *   Custom User Model (`Profile`).
    *   JWT-based authentication using **HttpOnly, Secure Cookies**.
    *   Role-Based Access Control (RBAC) hierarchy: Superadmin > Franchise Admin > Outlet Admin.
*   **Rate Limiting**: Integrated `slowapi` to protect public endpoints (e.g., `10/minute`).
*   **Vector Database**: Integrated **Qdrant** for semantic search capabilities, initialized via application lifespan events.

### 2. Restaurant Management Module (`/restaurant`)
*   **Franchise & Outlet Management**:
    *   Full CRUD API for managing Franchises.
    *   Outlet creation with media support (Cover images, Mid-page sliders).
*   **Advanced Menu System**:
    *   Category & Item management with image support.
    *   **AI Integration (Google Gemini)**:
        *   **Image Generation**: Auto-generate photorealistic food images for items without photos.
        *   **Text Enhancement**: AI-powered rewriting of menu descriptions for better marketing appeal.
    *   **Contextual Search**: Endpoints for searching items based on semantic meaning/description using Qdrant.

### 3. Inventory & Logistics Module (`/inventory`)
*   **Ingredient Tracking**: specific tracking for raw materials.
*   **Recipe Management**:
    *   Mapping between **Menu Items** and **Ingredients**.
    *   Allows defining quantities (recipes) to automate stock deduction.
*   **Transaction Ledger**:
    *    Comprehensive logging of inventory events: **Purchases**, **Usage**, **Wastage**, and **Adjustments**.
*   **Order Systems**: Basic order creation logic linked to inventory status.

### 4. End-User public API (`/open`)
*   **Public Access**: Optimized, unauthenticated endpoints for customers to view menus.
*   **Smart Search**: Semantic search implementation allowing users to find dishes by description or "vibe" rather than just keyword matching.
*   **Dynamic Data**: Outlet-specific menu retrieval based on URL slugs.

---

## 🛠 Technical Stack Summary
*   **Frameworks**: Django 5.2, FastAPI 0.115
*   **Database**: PostgreSQL (Structured Data), Qdrant (Vector Engine)
*   **Async Processing**: Celery 5.5 + Redis
*   **AI/LLM**: Google Geneartive AI (Gemini)
*   **API Standards**: RESTful, OpenAPI/Swagger Documentation enabled.

## 🔜 Next Steps / Pending Areas (Inferred)
*   **Frontend Integration**: Full integration with client-side applications (Web/Mobile).
*   **Advanced Analytics**: While data is collected, a dedicated Dashboard/Analytics module for sales reports is likely the next logical phase.
*   **Payment Gateway**: Integration of payment processing for the Order system.
