# Module Interactions in Dishto

This document outlines how different modules (Django apps) and components within the Dishto project interact with each other, covering dependencies, data flow, and shared functionalities.

## 1. Core (`core` app)

The `core` app serves as the foundational layer, providing common utilities and base structures that other modules build upon.

*   **Provides to others:**
    *   **`TimeStampedModel`**: An abstract base model inherited by almost all models in `Profile`, `Restaurant`, `Inventory`, and `Analysis` apps to automatically manage `created_at` and `updated_at` timestamps.
    *   **`User` Model (via `get_user_model()`):** The `Profile` app defines the custom `Profile` user model, which is then made available globally as `core.models.User` for other apps to reference (e.g., in `Restaurant.models.Franchise.admin` foreign key).
    *   **FastAPI Schemas (`BaseResponse`, `CamelCaseModel`):** Standardizes API request and response formats. Used by all FastAPI views and services across `Profile`, `Restaurant`, and `Inventory` apps.
    *   **FastAPI Dependencies (`is_superadmin`):** Provides reusable authorization checks. `Profile.views` uses `is_superadmin` for creating franchise admins.
    *   **FastAPI Exception Handling (`CustomException`):** Ensures consistent error responses across all FastAPI endpoints.
    *   **Lifespan Management (`lifespan.py`):** Configures application startup/shutdown. Crucially, it initializes the **Qdrant** vector database collection, which is essential for `Restaurant`'s AI features.
    *   **Asynchronous Utilities (`asyncs.py`):** Provides helper functions like `get_queryset` and `get_related_object` for efficient asynchronous database operations, used extensively by services in `Profile`, `Restaurant`, and `Inventory`.
    *   **Constants and Logger (`constants.py`, `logger.py`):** Shared configurations and logging utilities.

## 2. Profile (`Profile` app)

The `Profile` app manages user identity, authentication, and authorization.

*   **Uses from `core`:**
    *   Inherits `TimeStampedModel` for its `Profile` model.
    *   Uses `core.schema` for request/response Pydantic models in its FastAPI endpoints.
    *   Utilizes `core.dependencies.is_superadmin` for securing the franchise admin creation endpoint.
    *   Relies on `core.utils.asyncs` for asynchronous database interactions in its services.
*   **Uses from `Restaurant`:**
    *   References `Restaurant.models.Franchise` and `Restaurant.models.Outlet` when creating franchise and outlet admins, respectively.
    *   Leverages `Restaurant.dependencies.is_franchise_admin` to secure the outlet admin creation endpoint, ensuring only franchise admins can perform this action.
*   **Provides to `Restaurant` & `Inventory`:**
    *   **`Profile` Model:** Foreign keys in `Restaurant.models.Franchise` (`admin`) and `Restaurant.models.Outlet` (`admin`) link to this model, establishing administrative relationships.
    *   **Auth-related FastAPI Endpoints:** `dishto.urls` integrates `Profile.views.profile_router` (as part of `base_router_protected`), making authentication and user management APIs available to the rest of the system and external clients.

## 3. Restaurant (`Restaurant` app)

This app is central to the platform, managing all aspects of franchises, outlets, and menus.

*   **Uses from `core`:**
    *   Inherits `TimeStampedModel` for its primary models (`Franchise`, `Outlet`, `MenuCategory`, `MenuItem`, etc.).
    *   Uses `core.schema` for its extensive FastAPI request/response models.
    *   Employs `core.dependencies.is_superadmin` for franchise creation and `core.utils.limiters` for rate limiting its API endpoints.
    *   Utilizes `core.utils.asyncs` for efficient asynchronous ORM operations.
*   **Uses from `Profile`:**
    *   **`Profile` Model:** Establishes administrative links via foreign keys (`Franchise.admin`, `Outlet.admin`). `Restaurant.dependencies.is_franchise_admin` and `is_outlet_admin` rely on the `Profile` model and its roles to enforce authorization.
*   **Uses from `dishto` project level:**
    *   **`dishto.GlobalUtils.generate_unique_hash`**: Used for creating unique slugs for models.
    *   **`dishto.GlobalUtils.qdrant_client_`**: Directly interacts with the Qdrant client for contextual search of menu items.
    *   **Celery (`Restaurant.tasks.generate_menu_item_embedding_task`):** Triggered by the `MenuItem`'s `pre_save` signal, this asynchronous task uses `dishto.GlobalUtils.qdrant_client_` and generative AI (implicitly via `enhance_menu_item_description_with_ai` in `Restaurant.utils`) to create and update vector embeddings in Qdrant for efficient search.
*   **Provides to `Inventory` & `Analysis`:**
    *   **`Outlet` Model:** Crucial for `Inventory.models.Order` (each order belongs to an `Outlet`), `Inventory.models.Ingredient` (each ingredient belongs to an `Outlet`), and `Analysis.models.MonthlyBillingCycle` (each billing cycle is for an `Outlet`).
    *   **`MenuItem` Model:** Essential for `Inventory.models.OrderItem` (orders contain `MenuItem`s) and `Inventory.models.MenuItemIngredient` (ingredients are linked to `MenuItem`s).
    *   **FastAPI Endpoints:** `dishto.urls` integrates `Restaurant.views.restaurant_router` and `Restaurant.views.end_user_router`, providing APIs for managing restaurant data and for end-user interactions, which `Inventory`'s order creation process might implicitly leverage.

## 4. Inventory (`Inventory` app)

This app handles the management of ingredients, inventory transactions, and customer orders.

*   **Uses from `core`:**
    *   Inherits `TimeStampedModel` for its models (`Order`, `OrderItem`, `Ingredient`, `InventoryTransaction`, `MenuItemIngredient`).
    *   Uses `core.schema` for its FastAPI request/response models.
    *   Relies on `core.utils.asyncs` for asynchronous database operations.
*   **Uses from `Restaurant`:**
    *   **`MenuItem` Model:** `Inventory.models.OrderItem` (what was ordered) and `Inventory.models.MenuItemIngredient` (what goes into a menu item) directly reference `MenuItem`.
    *   **`Outlet` Model:** `Inventory.models.Order` and `Inventory.models.Ingredient` are tied to specific `Outlet` instances.
    *   **FastAPI Dependencies (`is_outlet_admin`):** Ensures that inventory and order management operations are performed by authorized outlet administrators.
*   **Provides to `Analysis`:**
    *   **`Order` Model:** `Analysis.models.MonthlyBillingCycle` aggregates `Order` instances to create monthly billing summaries.
*   **Internal Interactions:**
    *   **`InventoryTransaction` Signal:** The `post_save` signal on `InventoryTransaction` models automatically updates the `current_stock` of the related `Ingredient` in `Inventory.models.Ingredient`.
    *   **Order Creation Logic (`Inventory.service.InventoryService.create_order`):** This complex interaction involves:
        1.  Fetching `MenuItem` details from the `Restaurant` app.
        2.  Creating `OrderItem` instances.
        3.  Determining ingredient usage by querying `MenuItemIngredient` models.
        4.  Creating new `InventoryTransaction` records (type 'usage') for each ingredient consumed.
        5.  Updating `Ingredient.current_stock` based on transactions.
        This entire process occurs within an atomic database transaction to ensure data consistency.

## 5. Analysis (`Analysis` app)

This app is designed for aggregating data for reporting and financial analysis.

*   **Uses from `core`:**
    *   Inherits `TimeStampedModel` for its `MonthlyBillingCycle` model.
*   **Uses from `Restaurant`:**
    *   **`Outlet` Model:** `MonthlyBillingCycle` links directly to an `Outlet` to define the scope of the billing cycle.
*   **Uses from `Inventory`:**
    *   **`Order` Model:** `MonthlyBillingCycle` establishes a many-to-many relationship with `Order` instances, grouping them into monthly summaries for reporting.

## 6. Dishto Project Level (`dishto` directory)

This top-level directory orchestrates the integration of all apps and external services.

*   **`settings.py`:** Central configuration for the entire Django project, specifying `INSTALLED_APPS`, database connections (PostgreSQL), Celery broker (Redis), and JWT settings, which indirectly influences all app interactions.
*   **`urls.py`:** Defines the main URL routing for both Django (`admin/`) and FastAPI. It acts as the central hub by `include_router`-ing all the specific FastAPI app routers (`Profile.views.profile_router`, `Restaurant.views.restaurant_router`, `Inventory.views.inventory_router`).
*   **`middleware.py`:** Contains FastAPI-specific middleware (`AuthMiddleware`, `FranchiseMiddleware`) that intercepts requests before they reach the app-specific views. These middlewares enrich the `Request.state` with `user` and `franchise` objects, enabling downstream dependencies and views to perform authentication, authorization, and multi-tenancy logic.
*   **`fastapi_setup.py`:** The entry point for the FastAPI application, where all FastAPI-related configurations, middlewares, and routers are assembled and exposed.
*   **`GlobalUtils.py`:** Provides global utility functions and singletons (like the Qdrant client instance) used across various apps, ensuring consistent behavior and centralized management of external service connections.

## Overall Interaction Flow

1.  **Incoming Request:**
    *   **Django Admin:** Requests directly hit Django's URL dispatcher via `dishto/urls.py` for standard Django functionalities.
    *   **FastAPI:** Requests are routed to the FastAPI application initialized by `dishto/fastapi_setup.py`.
2.  **Middleware Processing:**
    *   `dishto.middleware.FranchiseMiddleware` extracts subdomain to identify the `Restaurant.Franchise` and attaches it to the request.
    *   `dishto.middleware.AuthMiddleware` processes JWT tokens from cookies, authenticates the `Profile.Profile` user, and attaches it to the request.
3.  **FastAPI Routing & Dependency Injection:** Requests are dispatched by `dishto/urls.py`'s `base_router_open` or `base_router_protected` to the appropriate `Profile`, `Restaurant`, or `Inventory` app's FastAPI view function. Dependencies (e.g., `is_franchise_admin`, `is_outlet_admin` from `Restaurant.dependencies` or `is_superadmin` from `core.dependencies`) are injected, leveraging the `user` and `franchise` objects set by middleware.
4.  **Business Logic Execution:** View functions delegate to app-specific services (e.g., `Profile.service.AuthService`, `Restaurant.service.MenuService`, `Inventory.service.InventoryService`).
5.  **Database & External Services Interaction:**
    *   Services perform CRUD operations using Django models (from `Profile`, `Restaurant`, `Inventory`, `Analysis` apps) interacting with **PostgreSQL**.
    *   `Restaurant` app interacts with **Qdrant** (via `dishto.GlobalUtils.qdrant_client_`) for vector search and triggers **Celery** tasks (which use **Redis** as a broker) for asynchronous embedding generation.
    *   `Inventory` app's `create_order` service method performs complex, atomic transactions involving `Restaurant.MenuItem`, `Inventory.OrderItem`, `Inventory.MenuItemIngredient`, and `Inventory.InventoryTransaction` models, while updating `Inventory.Ingredient` stock.
6.  **Response Generation:** Services return data which is formatted by FastAPI views using `core.schema.BaseResponse` and returned to the client.
7.  **Asynchronous Background Tasks (Celery):** Run independently, primarily triggered by signals (e.g., `Restaurant.MenuItem.pre_save` -> `Restaurant.tasks.generate_menu_item_embedding_task`) or directly by services (e.g., `Restaurant.service.MenuService` enhancing descriptions with AI).

This intricate web of interactions ensures a robust, scalable, and feature-rich platform for restaurant management.
