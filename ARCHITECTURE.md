# Dishto - Architecture and API Documentation

## Project Overview

Dishto is a comprehensive restaurant management platform designed to handle everything from user authentication and restaurant administration to menu management, inventory control, and order processing. The platform is built with a modern technology stack, leveraging the strengths of both Django and FastAPI to provide a robust and performant solution. It supports multi-tenancy for franchises, allowing each franchise to have its own subdomain and manage its outlets independently. The application also incorporates AI-powered features for an enhanced user experience, such as contextual menu search and automatic image generation for menu items.

## Architecture

Dishto employs a hybrid architecture that combines a Django backend with a FastAPI application. This approach allows for the rapid development of the admin interface and other traditional web application features with Django, while leveraging the high performance of FastAPI for the public-facing API.

The overall architecture consists of the following components:

*   **Django:** Used for the admin interface, database migrations, and ORM.
*   **FastAPI:** Powers the main API, providing a fast and modern interface for all client-facing operations.
*   **PostgreSQL:** The primary relational database for storing all application data.
*   **Redis:** Used as a message broker for Celery and for caching.
*   **Celery:** An asynchronous task queue used for background processing, such as generating AI-powered embeddings for menu items.
*   **Qdrant:** A vector database used for contextual search and other AI-powered features.
*   **Docker:** The entire application stack is containerized with Docker, making it easy to set up and deploy.

## Technologies Used

*   **Backend:** Python, Django, FastAPI
*   **API:** RESTful API with Pydantic for data validation
*   **Database:** PostgreSQL
*   **Caching/Message Broker:** Redis
*   **Asynchronous Tasks:** Celery
*   **Vector Database:** Qdrant
*   **Authentication:** JWT (JSON Web Tokens)
*   **Containerization:** Docker, Docker Compose
*   **AI/ML:** Google Generative AI, Langchain

## Project Structure

The project is organized into several Django apps, each with a specific responsibility:

*   `core`: Provides core functionalities, shared utilities, and handles Franchise and Outlet management.
*   `dishto`: The main project directory, containing the settings, URL configurations, and FastAPI setup.
*   `Profile`: Manages user authentication, profiles, and roles.
*   `Menu`: The core app for managing menu categories and items.
*   `Inventory`: Handles inventory management, ingredients, recipes, and stock control.
*   `Ordering`: Processes customer orders.
*   `Analysis`: Provides functionalities for data analysis and reporting.

## Module Breakdown

### `core`

The `core` app provides foundational functionalities for the project, including the management of Franchises, Outlets, and a new **subscription-based feature management system**.

*   **Models:**
    *   `TimeStampedModel`: An abstract model that adds `created_at` and `updated_at` fields to other models.
    *   `Franchise`: Represents a franchise.
    *   `Outlet`: An outlet belonging to a franchise. **Now manages features via `OutletFeature` through `GlobalFeature`.**
    *   `GlobalFeature`: **A new model that serves as the master list of all available features (e.g., "Menu", "Ordering", "Inventory"). It defines the generic feature.**
    *   `OutletFeature`: **A new model that represents a specific subscription of an `Outlet` to a `GlobalFeature`. It stores the custom price for that particular outlet's feature subscription.**
    *   `OutletFeatureRequest`: **A new model to handle requests from Outlet Admins to add or remove features, pending Superadmin approval. Each request points to `GlobalFeature`s.**
    *   `OutletFeatureHistory`: **Tracks changes in an outlet's approved features, referencing `GlobalFeature`s.**
*   **API Endpoints (FastAPI):**
    *   `/restaurant/franchise`: CRUD operations for franchises (Superadmin only).
    *   `/restaurant/outlet`: CRUD operations for outlets (Franchise Admin only).
    *   **/feature/available**: List available master features (public).
    *   **/feature/outlet/{outlet_slug}/requests**: Create and list feature requests for a specific outlet (Outlet Admin).
    *   **/feature/admin/requests**: List all feature requests and update (approve/reject/set price) feature requests (Superadmin).
*   **FastAPI Integration:**
    *   `schema.py`: Defines base Pydantic models for standardized API responses.
    *   `request.py` and `response.py`: **Now contain specific Pydantic schemas for feature management requests and responses.**
    *   `dependencies.py`: Includes FastAPI dependencies for authorization, such as `is_superadmin` and the new `require_feature` factory for enforcing subscription-based access control.
    *   `service.py`: **Introduces `FeatureService` to handle the business logic for feature management.**
    *   `exceptions.py`: Defines a custom exception handler for the FastAPI app.
    *   `lifespan.py`: Manages the application's lifespan events, including the initialization of the Qdrant collection.

### `Profile`

The `Profile` app handles user authentication and management.

*   **Models:**
    *   `Profile`: A custom user model that uses email for authentication and supports roles like `franchise_owner` and `outlet_owner`.
*   **API Endpoints (FastAPI):**
    *   `/auth/login`: Authenticates a user and returns JWT tokens.
    *   `/auth/logout`: Logs out a user.
    *   `/auth/refresh`: Refreshes JWT tokens.
    *   `/auth/user-info`: Retrieves information about the authenticated user.
    *   `/auth/set-password`: Sets a new password for a user.
    *   `/auth/update-password`: Updates the password for the authenticated user.
    *   `/auth/update-profile`: Updates the profile of the authenticated user.
    *   `/auth/admin/franchise`: Creates a new franchise admin.
    *   `/auth/admin/outlet`: Creates a new outlet admin.

### `Menu`

The `Menu` app is the heart of the application, managing all menu-related data.

*   **Models:**
    *   `MenuCategory`: A category of menu items.
    *   `MenuItem`: A specific item on the menu.
    *   `Offers`: Special offers for menu items.
*   **API Endpoints (FastAPI):**
    *   **End-user Endpoints (Open):**
        *   `/`: Get all outlets for a franchise.
        *   `/category/{outlet_slug}`: Get all menu categories for an outlet.
        *   `/menu/{outlet_slug}/search/contextual`: Contextual search for menu items.
        *   `/menu/{outlet_slug}`: Get the full menu for an outlet.
    *   **Admin Endpoints (Protected):**
        *   `/menu/{outlet_slug}/categories`: CRUD operations for menu categories.
        *   `/menu/{outlet_slug}/items`: CRUD operations for menu items.
*   **AI Features:**
    *   Asynchronous generation of embeddings for menu items for contextual search.
    *   AI-powered enhancement of menu item descriptions.
    *   Automatic generation of images for menu items.

### `Inventory`

The `Inventory` app manages inventory, recipes, and stock levels.

*   **Models:**
    *   `Ingredient`: An ingredient used in menu items.
    *   `MenuItemIngredient`: Maps ingredients to menu items with quantities (the recipe).
    *   `InventoryTransaction`: Tracks all changes in ingredient stock (e.g., purchase, wastage).
*   **API Endpoints (FastAPI):**
    *   `/{outlet_slug}/ingredients`: CRUD operations for ingredients.
    *   `/{outlet_slug}/menu_item/ingredient`: Manage the recipe mapping of ingredients to menu items.
    *   `/{outlet_slug}/transactions`: CRUD operations for inventory transactions.

### `Ordering`

The `Ordering` app handles the creation of customer orders.

*   **Models:**
    *   `Order`: Represents a customer order.
    *   `OrderItem`: An item within an order.
*   **API Endpoints (FastAPI):**
    *   `/{outlet_slug}/orders`: Create a new order, which automatically triggers inventory deduction.

### `Analysis`

The `Analysis` app is used for data analysis and reporting.

*   **Models:**
    *   `MonthlyBillingCycle`: Groups orders into monthly billing cycles for an outlet.

## FastAPI Integration

The project seamlessly integrates FastAPI with Django.

*   **Middleware:**
    *   `AuthMiddleware`: Handles JWT-based authentication by reading tokens from cookies.
    *   `FranchiseMiddleware`: Implements multi-tenancy by identifying the franchise based on the subdomain.
*   **Routing:**
    *   API endpoints are organized into `open` and `protected` routers, with further separation by app.
*   **Asynchronous Operations:** The application is built to be fully asynchronous, using `async`/`await` and running on a `uvicorn` server.

## Docker Setup

The entire application is containerized using Docker and managed with Docker Compose. The `docker-compose.yml` file defines the following services:

*   `app`: The main application service running the FastAPI app.
*   `celery`: The Celery worker for handling asynchronous tasks.
*   `postgres`: The PostgreSQL database service.
*   `redis`: The Redis service for caching and message broking.
*   `qdrant`: The Qdrant vector database service.

## How to Run

To run the project locally, you need to have Docker and Docker Compose installed.

1.  **Create a `.env` file:**
    Create a `.env` file in the root of the project and add the necessary environment variables for the database, Redis, etc. You can use the `.env.docker` as a template.

2.  **Build and run the containers:**
    ```bash
    docker-compose up --build
    ```

This command will build the Docker images, start all the services, and run the database migrations. The application will be available at `http://localhost:10008`.
