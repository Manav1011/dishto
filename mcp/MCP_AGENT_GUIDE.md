# REST API Testing MCP - AI Agent Guide

This guide explains how to use the REST API Testing MCP server to efficiently interact with REST APIs using OpenAPI specifications.

## Quick Start Workflow

```
1. list_openapi_endpoints(openapi_url) → Loads and caches the API spec
2. analyze_endpoint_requirements(endpoint_path, method) → Understand what the endpoint needs
3. resolve_schema(schema_ref) → See exact field definitions (if needed)
4. create_session(session_name, base_url) → Set up authenticated session
5. call_with_session(...) → Make requests with automatic auth
```

## Available Tools

### 1. OpenAPI Discovery

#### `list_openapi_endpoints(openapi_url: str, search: str = "")`
**Purpose:** Load the OpenAPI spec and list all available endpoints.

**When to use:** Always use this FIRST before calling any other tool.

**Example:**
```python
list_openapi_endpoints("https://api.example.com/openapi.json")
# With search filter
list_openapi_endpoints("https://api.example.com/openapi.json", search="auth")
```

**Returns:** List of all endpoints with descriptions, cached for later use.

---

#### `get_endpoint_details(path: str)`
**Purpose:** Get detailed OpenAPI definition for a specific endpoint (all HTTP methods).

**When to use:** When you need the raw OpenAPI spec for an endpoint.

**Example:**
```python
get_endpoint_details("/protected/auth/login")
```

**Returns:** Full OpenAPI specification for the endpoint in JSON format.

---

### 2. Smart Endpoint Analysis ⭐ (Use This First!)

#### `analyze_endpoint_requirements(endpoint_path: str, method: str = "GET")`
**Purpose:** Automatically analyze what an endpoint requires and how to call it correctly.

**When to use:** ALWAYS use this before calling an endpoint for the first time!

**Example:**
```python
analyze_endpoint_requirements("/protected/auth/login", "POST")
```

**Returns:** Detailed analysis including:
- Where to place parameters (query, body, form-data, path, headers)
- Required vs optional fields
- Content-Type expectations (JSON vs form-data)
- Authentication requirements
- Schema references with hints to resolve them

**Key outputs:**
- `use_json_body: true` → Use `body` parameter in call_api
- `use_form_data: true` → Use `form_data` parameter in call_api
- `query_parameters` → Use `params` parameter in call_api
- `schema_ref` → Use resolve_schema() to see field details

---

#### `resolve_schema(schema_ref: str)`
**Purpose:** Resolve OpenAPI schema references to see exact field definitions.

**When to use:** When `analyze_endpoint_requirements` shows a `schema_ref` or you get validation errors.

**Example:**
```python
resolve_schema("#/components/schemas/FranchiseAdminCreationRequest")
```

**Returns:** Complete schema with:
- All field names
- Data types (string, integer, boolean, etc.)
- Required vs optional status
- Validation rules (minLength, maxLength, format, enum, etc.)
- Descriptions

---

### 3. Session Management ⭐ (Eliminates Token Copy-Paste!)

#### `create_session(session_name: str, base_url: str)`
**Purpose:** Create a named session to store base URL and authentication tokens.

**When to use:** After getting the base URL, before making authenticated requests.

**Example:**
```python
create_session("superadmin", "https://dishto.in/api/")
create_session("franchise_admin", "https://franchise.dishto.in/api/")
```

---

#### `save_session_tokens(session_name: str, access_token: str, refresh_token: str = None)`
**Purpose:** Save authentication tokens to a session for automatic use.

**When to use:** Immediately after successful login.

**Example:**
```python
# After login, extract tokens from response
save_session_tokens("superadmin", 
    access_token="eyJhbGc...",
    refresh_token="eyJhbGc...")
```

---

#### `call_with_session(session_name, endpoint, method="GET", params=None, body=None, form_data=None, ...)`
**Purpose:** Make API calls using saved session (automatic authentication).

**When to use:** For ALL authenticated requests after setting up a session.

**Example:**
```python
# Instead of manually adding cookies every time
call_with_session(
    session_name="superadmin",
    endpoint="protected/restaurant/franchise/",
    method="POST",
    params={"name": "Test Franchise"}
)
```

**Benefits:**
- ✅ No need to copy-paste tokens
- ✅ Automatic cookie headers
- ✅ Base URL remembered
- ✅ Cleaner, shorter calls

---

#### `list_sessions()`
**Purpose:** View all active sessions and their status.

**Returns:** List of sessions with base URLs and token status.

---

### 4. Making API Calls

#### `call_api(base_url, endpoint, endpoint_details, method="GET", params=None, headers=None, body=None, form_data=None, files=None, timeout=10.0)`
**Purpose:** Make a direct API call (use when not using sessions).

**When to use:** 
- Public endpoints (no auth needed)
- When you want full control
- First login call (before session exists)

**Parameters:**
- `base_url`: API base URL (e.g., "https://api.example.com/")
- `endpoint`: Endpoint path (e.g., "protected/auth/login")
- `endpoint_details`: Leave empty "" (used for reference only)
- `method`: HTTP method (GET, POST, PUT, PATCH, DELETE)
- `params`: Query parameters → `{"name": "value"}`
- `headers`: HTTP headers → `{"Content-Type": "application/json"}`
- `body`: JSON body → `{"field": "value"}` (use when endpoint expects JSON)
- `form_data`: Form data → `{"field": "value"}` (use when endpoint expects multipart/form-data)
- `files`: File uploads → `{"field_name": "path/to/file"}`

**Critical Rules:**
1. For **multipart/form-data** endpoints → Use `form_data` parameter
2. For **application/json** endpoints → Use `body` parameter
3. For **query parameters** → Use `params` parameter
4. **Never mix** `body` and `form_data` in the same call

**Example - JSON:**
```python
call_api(
    base_url="https://api.example.com/",
    endpoint="protected/auth/login",
    endpoint_details="",
    method="POST",
    body={"email": "user@example.com", "password": "pass123"},
    headers={"Content-Type": "application/json"}
)
```

**Example - Form Data:**
```python
call_api(
    base_url="https://api.example.com/",
    endpoint="protected/restaurant/outlet",
    endpoint_details="",
    method="POST",
    form_data={"name": "Test Outlet"},
    headers={"Cookie": "access=token; refresh=token"}
)
```

**Example - Query Params:**
```python
call_api(
    base_url="https://api.example.com/",
    endpoint="protected/restaurant/franchise/",
    endpoint_details="",
    method="POST",
    params={"name": "Test Franchise"},
    headers={"Cookie": "access=token"}
)
```

---

### 5. Error Analysis & Debugging

#### `analyze_api_error(error_response: str, endpoint_path: str, method: str = "POST")`
**Purpose:** Parse error responses and get specific fix suggestions.

**When to use:** When you get a 422 validation error or other API error.

**Example:**
```python
analyze_api_error(
    error_response='HTTP error 422: {"detail":[{"type":"missing","loc":["body","name"],"msg":"Field required"}]}',
    endpoint_path="/protected/restaurant/outlet",
    method="POST"
)
```

**Returns:** 
- Parsed error details
- Specific suggestions for fixing the issue
- What the endpoint expects (JSON vs form-data)
- Schema reference hints

---

#### `generate_request_example(endpoint_path: str, method: str = "GET", format: str = "curl")`
**Purpose:** Generate working example requests from OpenAPI spec.

**When to use:** When learning how to call a new endpoint.

**Formats:** `"curl"`, `"python"`, `"http"`

**Example:**
```python
generate_request_example("/protected/auth/login", "POST", "curl")
generate_request_example("/protected/auth/login", "POST", "python")
```

---

## Recommended Workflows

### Workflow 1: First Time Using an API

```python
# Step 1: Load OpenAPI spec
list_openapi_endpoints("https://api.example.com/openapi.json")

# Step 2: Find the endpoint you need (browse the list)

# Step 3: Analyze what it requires
analyze_endpoint_requirements("/protected/auth/login", "POST")

# Step 4: Resolve schema if needed
resolve_schema("#/components/schemas/LoginRequest")

# Step 5: Generate example for reference
generate_request_example("/protected/auth/login", "POST", "curl")

# Step 6: Make the call
call_api(...)
```

---

### Workflow 2: Authenticated API Session (RECOMMENDED)

```python
# Step 1: Load OpenAPI spec
list_openapi_endpoints("https://api.example.com/openapi.json")

# Step 2: Create session
create_session("main", "https://api.example.com/")

# Step 3: Login (direct call, no session yet)
response = call_api(
    base_url="https://api.example.com/",
    endpoint="auth/login",
    endpoint_details="",
    method="POST",
    body={"email": "user@example.com", "password": "pass"}
)

# Step 4: Extract tokens from response and save
# Parse response JSON to get access_token and refresh_token
save_session_tokens("main", access_token="...", refresh_token="...")

# Step 5: Now use session for all subsequent calls
call_with_session(
    session_name="main",
    endpoint="protected/resource",
    method="GET"
)

call_with_session(
    session_name="main",
    endpoint="protected/resource",
    method="POST",
    body={"name": "test"}
)
```

---

### Workflow 3: Handling Errors

```python
# Make a call that fails
response = call_with_session(...)

# If you get an error, analyze it
analysis = analyze_api_error(
    error_response=response,
    endpoint_path="/the/endpoint",
    method="POST"
)

# Follow the suggestions in the analysis

# If still unclear, check endpoint requirements
requirements = analyze_endpoint_requirements("/the/endpoint", "POST")

# Resolve schema for field details
resolve_schema("#/components/schemas/SchemaName")
```

---

## Best Practices

### ✅ DO:
1. **Always** run `list_openapi_endpoints()` first to cache the spec
2. **Always** use `analyze_endpoint_requirements()` before calling a new endpoint
3. **Always** use sessions for authenticated APIs (create_session → save_session_tokens → call_with_session)
4. Use `resolve_schema()` when you see schema references or get validation errors
5. Use `analyze_api_error()` when requests fail
6. Match the data location to what `analyze_endpoint_requirements()` suggests:
   - `use_json_body` → Use `body` parameter
   - `use_form_data` → Use `form_data` parameter
   - `query_parameters` → Use `params` parameter

### ❌ DON'T:
1. Don't call endpoints without first analyzing them
2. Don't manually copy-paste tokens for every request (use sessions!)
3. Don't mix `body` and `form_data` in the same call
4. Don't guess parameter locations (query vs body vs form-data)
5. Don't ignore the hints from `analyze_endpoint_requirements()`

---

## Common Patterns

### Pattern: Login & Save Session
```python
# 1. Create session
create_session("user", "https://api.example.com/")

# 2. Login
login_response = call_api(
    base_url="https://api.example.com/",
    endpoint="auth/login",
    endpoint_details="",
    method="POST",
    body={"email": "user@example.com", "password": "password"}
)

# 3. Parse response (you'll need to extract tokens from the JSON response)
# Example: response has {"access": "token1", "refresh": "token2"}
# Extract these values and:

save_session_tokens("user", 
    access_token="extracted_access_token",
    refresh_token="extracted_refresh_token"
)

# 4. Now use for all calls
call_with_session("user", endpoint="protected/data", method="GET")
```

---

### Pattern: Multi-tenant API (Different Subdomains)
```python
# Load main OpenAPI
list_openapi_endpoints("https://api.example.com/openapi.json")

# Create different sessions for different tenants
create_session("tenant1", "https://tenant1.example.com/api/")
create_session("tenant2", "https://tenant2.example.com/api/")

# Login to each
# ... (login and save tokens for each session)

# Use appropriate session
call_with_session("tenant1", endpoint="resource", method="GET")
call_with_session("tenant2", endpoint="resource", method="GET")
```

---

### Pattern: CRUD Operations
```python
# Create (POST with body or form_data)
analyze_endpoint_requirements("/resource", "POST")
call_with_session("main", endpoint="resource", method="POST", 
    body={"name": "item"})  # or form_data based on analysis

# Read (GET)
call_with_session("main", endpoint="resource/123", method="GET")

# Update (PUT/PATCH)
call_with_session("main", endpoint="resource/123", method="PUT",
    body={"name": "updated"})

# Delete (DELETE)
call_with_session("main", endpoint="resource/123", method="DELETE")
```

---

### Pattern: Query Parameters
```python
# When endpoint expects query params
analyze_endpoint_requirements("/search", "GET")
# Shows: query_parameters: [{name: "q", required: true}]

call_with_session("main", 
    endpoint="search",
    method="GET",
    params={"q": "search term", "limit": 10}
)
```

---

### Pattern: File Upload
```python
# When endpoint expects multipart/form-data with files
analyze_endpoint_requirements("/upload", "POST")
# Shows: use_form_data: true

call_with_session("main",
    endpoint="upload",
    method="POST",
    form_data={"title": "My File"},
    files={"file": "/path/to/file.jpg"}
)
```

---

## Troubleshooting Guide

### Error: "Field required" (422 Validation Error)

**Solution:**
1. Run `analyze_api_error()` on the error response
2. Check suggestions for where to place the field
3. Run `analyze_endpoint_requirements()` to confirm
4. Use `resolve_schema()` to see exact field requirements

---

### Error: "Authentication credentials were not provided" (401)

**Solution:**
1. Check if session has tokens: `list_sessions()`
2. Re-login if needed and save tokens with `save_session_tokens()`
3. Make sure using `call_with_session()` not `call_api()`
4. Verify base URL matches the subdomain (multi-tenant APIs)

---

### Error: Can't figure out request format

**Solution:**
1. Run `analyze_endpoint_requirements()` - it will tell you!
2. Look for these keys:
   - `use_json_body: true` → Use `body={...}`
   - `use_form_data: true` → Use `form_data={...}`
   - `query_parameters: [...]` → Use `params={...}`
3. Run `generate_request_example()` to see a working example
4. Use `resolve_schema()` to see exact field definitions

---

### Error: Base URL / Subdomain confusion

**Solution:**
1. Create separate sessions for each subdomain
2. Use the full base URL in `create_session()`
3. May need to re-run `list_openapi_endpoints()` with subdomain's OpenAPI URL

---

## Summary Cheat Sheet

| Goal | Tools to Use |
|------|--------------|
| Start using an API | `list_openapi_endpoints()` |
| Understand an endpoint | `analyze_endpoint_requirements()` → `resolve_schema()` |
| See example request | `generate_request_example()` |
| Set up authentication | `create_session()` → login → `save_session_tokens()` |
| Make authenticated calls | `call_with_session()` |
| Debug errors | `analyze_api_error()` |
| See field requirements | `resolve_schema()` |
| View active sessions | `list_sessions()` |

---

## Example: Complete Workflow

```python
# 1. Load API spec
list_openapi_endpoints("https://dishto.in/api/openapi.json")

# 2. Create session
create_session("superadmin", "https://dishto.in/api/")

# 3. Understand login endpoint
analyze_endpoint_requirements("/protected/auth/login", "POST")
# Output: use_json_body: true, requires email & password

# 4. Login
login_result = call_api(
    base_url="https://dishto.in/api/",
    endpoint="protected/auth/login",
    endpoint_details="",
    method="POST",
    body={"email": "admin@example.com", "password": "pass123"}
)

# 5. Save tokens (extract from login_result)
save_session_tokens("superadmin", 
    access_token="<extracted>",
    refresh_token="<extracted>")

# 6. Understand franchise creation endpoint
analyze_endpoint_requirements("/protected/restaurant/franchise/", "POST")
# Output: query_parameters: [{name: "name", required: true}]

# 7. Create franchise
call_with_session(
    session_name="superadmin",
    endpoint="protected/restaurant/franchise/",
    method="POST",
    params={"name": "My Franchise"}
)

# 8. If error occurs
analyze_api_error(error_response="...", endpoint_path="/protected/restaurant/franchise/", method="POST")
```

---

## Key Takeaway

**The MCP eliminates trial-and-error by telling you exactly what an endpoint needs before you call it.**

Use the analysis tools (`analyze_endpoint_requirements`, `resolve_schema`) FIRST, then make informed calls. Use sessions to avoid repetitive token management. Use error analysis when things go wrong.

Happy API testing! 🚀
