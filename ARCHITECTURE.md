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

*   `core`: Provides core functionalities and utilities shared across the project.
*   `dishto`: The main project directory, containing the settings, URL configurations, and FastAPI setup.
*   `Profile`: Manages user authentication, profiles, and roles.
*   `Restaurant`: The core app for managing franchises, outlets, menus, and menu items.
*   `Inventory`: Handles inventory management, order processing, and stock control.
*   `Analysis`: Provides functionalities for data analysis and reporting.

## Module Breakdown

### `core`

The `core` app provides foundational functionalities for the project.

*   **Models:**
    *   `TimeStampedModel`: An abstract model that adds `created_at` and `updated_at` fields to other models.
*   **FastAPI Integration:**
    *   `schema.py`: Defines base Pydantic models for standardized API responses.
    *   `dependencies.py`: Includes FastAPI dependencies for authorization, such as `is_superadmin`.
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

### `Restaurant`

The `Restaurant` app is the heart of the application, managing all restaurant-related data.

*   **Models:**
    *   `Franchise`: Represents a franchise.
    *   `Outlet`: An outlet belonging to a franchise.
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
        *   `/restaurant/franchise`: CRUD operations for franchises.
        *   `/restaurant/outlet`: CRUD operations for outlets.
        *   `/restaurant/{outlet_slug}/categories`: CRUD operations for menu categories.
        *   `/restaurant/{outlet_slug}/items`: CRUD operations for menu items.
*   **AI Features:**
    *   Asynchronous generation of embeddings for menu items for contextual search.
    *   AI-powered enhancement of menu item descriptions.
    *   Automatic generation of images for menu items.

### `Inventory`

The `Inventory` app manages inventory, orders, and stock levels.

*   **Models:**
    *   `Ingredient`: An ingredient used in menu items.
    *   `MenuItemIngredient`: Maps ingredients to menu items with quantities.
    *   `InventoryTransaction`: Tracks all changes in ingredient stock.
    *   `Order`: Represents a customer order.
    *   `OrderItem`: An item within an order.
*   **API Endpoints (FastAPI):**
    *   `/{outlet_slug}/ingredients`: CRUD operations for ingredients.
    *   `/{outlet_slug}/menu_item/ingredient`: Manage the mapping of ingredients to menu items.
    *   `/{outlet_slug}/transactions`: CRUD operations for inventory transactions.
    *   `/{outlet_slug}/orders`: Create and manage orders.

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
