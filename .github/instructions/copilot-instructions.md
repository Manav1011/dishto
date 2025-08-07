# Dishto API & Code Structure - Important Rules

## API Creation Workflow

1. **Request/Response Models**

   - Every API must have dedicated request and response models in `request.py` and `response.py`.
   - Use Pydantic models for validation and serialization.
   - Do not use generic types (e.g., dict, bool) in endpoint signatures.
2. **Service Layer**

   - All business logic and DB access go in async service methods in `service.py`.
   - Service methods accept request models/context, return response models, and raise `HTTPException` for errors.
   - Use dependency injection for context (e.g., `outlet`).
3. **API Route Definition**

   - Routes are defined in `views.py` using FastAPI's `APIRouter`.
   - Group endpoints under routers (e.g., `inventory_router`).
   - Use descriptive paths, summaries, docstrings, and dependency injection.
   - Handlers accept request models, inject service/context, call service methods, and return a `BaseResponse` wrapping the response model.
4. **Listing/Detail APIs**

   - Use a single GET API for both list and detail, with a `slug` parameter (`__all__` for list, specific slug for detail).
   - **Code Structure**
5. - All imports must be at the top of the file.
   - Models in `models.py`, requests in `request.py`, responses in `response.py`, services in `service.py`, routes in `views.py`.
   - Keep function signatures clean and minimal, only include required parameters.
   - Use dependency injection for permissions and context.
6. **Error Handling**

   - Use FastAPI `HTTPException` for API errors, with clear status codes and messages.
7. **General Rules**

   - Follow DRY and clear separation of concerns.
   - Modular, extensible, and maintainable code.
   - All API responses wrapped in `BaseResponse` for consistent format.

## ORM Relationship Access & Async Context

- **Related Objects:**
  - Do not use generic helpers like `get_related_object` for ORM relationships.
  - Always use direct attribute access (e.g., `obj.related_field`) for related objects.
  - For foreign key lookups, use double underscore syntax in queries (e.g., `category__outlet=outlet`).

- **Async Context:**
  - Do not use sync ORM calls in async service methods. Use only async ORM methods (`aget`, `acreate`, etc.).
  - If you see errors like "You cannot call this from an async context - use a thread or sync_to_async", refactor to use async ORM calls and avoid sync access.

---

**Follow these rules for all new APIs and code changes.**
