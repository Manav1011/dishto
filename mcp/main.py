from fastmcp import FastMCP
import httpx
import json
from typing import Optional, Dict, Any, List

mcp = FastMCP("API Tester MCP")
openapi_cache = {}
session_cache = {}  # Store authentication sessions

@mcp.tool
def list_openapi_endpoints(openapi_url: str, search: str = "") -> str:
    """
    Fetches an OpenAPI JSON from the given URL and returns all endpoints with their descriptions.
    Also stores the OpenAPI JSON in a global cache for later use.
    Optionally filters endpoints by a search term (path, method, or description).
    """
    global openapi_cache
    try:
        response = httpx.get(openapi_url)
        response.raise_for_status()
        openapi = response.json()
        openapi_cache['data'] = openapi
    except Exception as e:
        return f"Failed to fetch or parse OpenAPI JSON: {e}"

    paths = openapi.get("paths", {})
    if not paths:
        return "No endpoints found in the OpenAPI spec."

    output = []
    search_lower = search.lower()
    for path, methods in paths.items():
        for method, details in methods.items():
            desc = details.get("description") or details.get("summary") or "No description."
            entry = f"{method.upper()} {path}: {desc}"
            if search_lower:
                if (
                    search_lower in method.lower()
                    or search_lower in path.lower()
                    or search_lower in desc.lower()
                ):
                    output.append(entry)
            else:
                output.append(entry)
    if not output:
        return f"No endpoints found matching '{search}'."
    return "\n".join(output)

@mcp.tool
def get_endpoint_details(path: str) -> str:
    """
    Returns all details for a given endpoint path from the cached OpenAPI JSON, including all methods.
    """
    openapi = openapi_cache.get('data')
    if not openapi:
        return "No OpenAPI spec loaded. Please run list_openapi_endpoints first."
    paths = openapi.get("paths", {})
    endpoint = paths.get(path)
    if not endpoint:
        return f"Endpoint '{path}' not found."
    # Format all details (all methods) as a string
    return json.dumps(endpoint, indent=2)

@mcp.tool
def resolve_schema(schema_ref: str) -> str:
    """
    Resolves a schema reference (e.g., #/components/schemas/FranchiseAdminCreationRequest) 
    from the cached OpenAPI spec and returns the complete schema definition with all fields,
    types, validation rules, and descriptions.
    
    Args:
        schema_ref: The schema reference to resolve (e.g., "#/components/schemas/MySchema")
    
    Returns:
        JSON string with the resolved schema including all fields and their properties
    """
    openapi = openapi_cache.get('data')
    if not openapi:
        return "No OpenAPI spec loaded. Please run list_openapi_endpoints first."
    
    # Parse the reference
    if not schema_ref.startswith("#/"):
        return f"Invalid schema reference format. Expected '#/...' but got '{schema_ref}'"
    
    parts = schema_ref.split("/")[1:]  # Skip the '#'
    
    # Navigate to the schema
    current = openapi
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
            if current is None:
                return f"Schema path '{schema_ref}' not found in OpenAPI spec."
        else:
            return f"Cannot navigate to '{part}' in schema path."
    
    # Recursively resolve nested $ref references
    def resolve_refs(obj, depth=0):
        if depth > 10:  # Prevent infinite recursion
            return obj
        
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                resolved = resolve_schema_internal(ref)
                return resolve_refs(resolved, depth + 1)
            else:
                return {k: resolve_refs(v, depth) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve_refs(item, depth) for item in obj]
        else:
            return obj
    
    def resolve_schema_internal(ref):
        parts = ref.split("/")[1:]
        current = openapi
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
                if current is None:
                    return {"error": f"Reference '{ref}' not found"}
            else:
                return {"error": f"Cannot resolve '{ref}'"}
        return current
    
    resolved = resolve_refs(current)
    
    # Format the output in a more readable way
    result = {
        "schema_name": parts[-1] if parts else "Unknown",
        "schema": resolved
    }
    
    # Extract key information for easier reading
    if isinstance(resolved, dict):
        properties = resolved.get("properties", {})
        required = resolved.get("required", [])
        
        if properties:
            result["fields"] = {}
            for field_name, field_info in properties.items():
                field_summary = {
                    "type": field_info.get("type", "unknown"),
                    "required": field_name in required,
                }
                if "description" in field_info:
                    field_summary["description"] = field_info["description"]
                if "format" in field_info:
                    field_summary["format"] = field_info["format"]
                if "minLength" in field_info:
                    field_summary["minLength"] = field_info["minLength"]
                if "maxLength" in field_info:
                    field_summary["maxLength"] = field_info["maxLength"]
                if "minimum" in field_info:
                    field_summary["minimum"] = field_info["minimum"]
                if "maximum" in field_info:
                    field_summary["maximum"] = field_info["maximum"]
                if "enum" in field_info:
                    field_summary["enum"] = field_info["enum"]
                if "items" in field_info:
                    field_summary["items"] = field_info["items"]
                
                result["fields"][field_name] = field_summary
    
    return json.dumps(result, indent=2)

@mcp.tool
def analyze_endpoint_requirements(endpoint_path: str, method: str = "GET") -> str:
    """
    Analyzes an endpoint and returns detailed information about what it requires:
    - Where parameters should be placed (query, body, form-data)
    - Required vs optional fields
    - Data types and validation rules
    - Authentication requirements
    - Content-Type expectations
    
    Args:
        endpoint_path: The API endpoint path (e.g., "/protected/auth/login")
        method: HTTP method (default: "GET")
    
    Returns:
        Detailed analysis of endpoint requirements in JSON format
    """
    openapi = openapi_cache.get('data')
    if not openapi:
        return "No OpenAPI spec loaded. Please run list_openapi_endpoints first."
    
    paths = openapi.get("paths", {})
    endpoint = paths.get(endpoint_path)
    
    if not endpoint:
        return f"Endpoint '{endpoint_path}' not found in OpenAPI spec."
    
    method = method.lower()
    method_details = endpoint.get(method)
    
    if not method_details:
        available = list(endpoint.keys())
        return f"Method '{method.upper()}' not found for '{endpoint_path}'. Available: {available}"
    
    analysis = {
        "endpoint": endpoint_path,
        "method": method.upper(),
        "summary": method_details.get("summary", "No summary"),
        "description": method_details.get("description", "No description"),
        "requirements": {}
    }
    
    # Check for parameters (query, path, header, etc.)
    parameters = method_details.get("parameters", [])
    if parameters:
        query_params = []
        path_params = []
        header_params = []
        
        for param in parameters:
            param_info = {
                "name": param.get("name"),
                "required": param.get("required", False),
                "type": param.get("schema", {}).get("type", "unknown"),
                "description": param.get("description", "")
            }
            
            location = param.get("in", "unknown")
            if location == "query":
                query_params.append(param_info)
            elif location == "path":
                path_params.append(param_info)
            elif location == "header":
                header_params.append(param_info)
        
        if query_params:
            analysis["requirements"]["query_parameters"] = query_params
        if path_params:
            analysis["requirements"]["path_parameters"] = path_params
        if header_params:
            analysis["requirements"]["header_parameters"] = header_params
    
    # Check for request body
    request_body = method_details.get("requestBody")
    if request_body:
        content = request_body.get("content", {})
        analysis["requirements"]["request_body"] = {
            "required": request_body.get("required", False),
            "content_types": list(content.keys())
        }
        
        # Analyze each content type
        for content_type, content_details in content.items():
            schema = content_details.get("schema", {})
            
            if "$ref" in schema:
                analysis["requirements"]["schema_ref"] = schema["$ref"]
                analysis["requirements"]["hint"] = f"Use resolve_schema('{schema['$ref']}') to see field details"
            
            if "multipart/form-data" in content_type:
                analysis["requirements"]["use_form_data"] = True
                analysis["requirements"]["hint"] = "Use form_data parameter in call_api"
            elif "application/json" in content_type:
                analysis["requirements"]["use_json_body"] = True
                analysis["requirements"]["hint"] = "Use body parameter in call_api"
            elif "application/x-www-form-urlencoded" in content_type:
                analysis["requirements"]["use_form_data"] = True
                analysis["requirements"]["hint"] = "Use form_data parameter in call_api"
    
    # Check authentication requirements
    security = method_details.get("security", [])
    if security:
        analysis["requirements"]["authentication"] = security
    
    # Check responses
    responses = method_details.get("responses", {})
    if responses:
        analysis["responses"] = {}
        for status_code, response_details in responses.items():
            analysis["responses"][status_code] = {
                "description": response_details.get("description", "")
            }
    
    return json.dumps(analysis, indent=2)

@mcp.tool
def create_session(session_name: str, base_url: str) -> str:
    """
    Creates a new API session to store authentication tokens and base URL.
    This allows subsequent requests to automatically use saved authentication.
    
    Args:
        session_name: A unique name for this session (e.g., "superadmin", "franchise_admin")
        base_url: The base URL for API requests in this session
    
    Returns:
        Confirmation message
    """
    session_cache[session_name] = {
        "base_url": base_url,
        "tokens": {},
        "headers": {}
    }
    return f"Session '{session_name}' created with base_url: {base_url}"

@mcp.tool
def save_session_tokens(session_name: str, access_token: str, refresh_token: Optional[str] = None) -> str:
    """
    Saves authentication tokens to a session for automatic use in subsequent requests.
    
    Args:
        session_name: The name of the session to update
        access_token: The access token (JWT or other)
        refresh_token: Optional refresh token
    
    Returns:
        Confirmation message
    """
    if session_name not in session_cache:
        return f"Session '{session_name}' not found. Create it first with create_session."
    
    session_cache[session_name]["tokens"] = {
        "access": access_token,
        "refresh": refresh_token
    }
    
    # Update headers with cookie
    cookie_parts = [f"access={access_token}"]
    if refresh_token:
        cookie_parts.append(f"refresh={refresh_token}")
    
    session_cache[session_name]["headers"]["Cookie"] = "; ".join(cookie_parts)
    
    return f"Tokens saved to session '{session_name}'"

@mcp.tool
def call_with_session(
    session_name: str,
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict] = None,
    body: Optional[Dict] = None,
    form_data: Optional[Dict] = None,
    files: Optional[Dict] = None,
    additional_headers: Optional[Dict] = None,
    timeout: float = 10.0
) -> str:
    """
    Makes an API call using a saved session (with automatic authentication).
    
    Args:
        session_name: The name of the session to use
        endpoint: The endpoint path to call
        method: HTTP method (default: "GET")
        params: Query parameters
        body: JSON body
        form_data: Form data
        files: Files to upload
        additional_headers: Extra headers to add
        timeout: Request timeout
    
    Returns:
        API response as a string
    """
    if session_name not in session_cache:
        return f"Session '{session_name}' not found. Create it first with create_session."
    
    session = session_cache[session_name]
    base_url = session["base_url"]
    headers = session["headers"].copy()
    
    if additional_headers:
        headers.update(additional_headers)
    
    # Call the original call_api with session headers
    return call_api(
        base_url=base_url,
        endpoint=endpoint,
        endpoint_details="",  # Not needed for actual call
        method=method,
        params=params,
        headers=headers,
        body=body,
        form_data=form_data,
        files=files,
        timeout=timeout
    )

@mcp.tool
def list_sessions() -> str:
    """
    Lists all active sessions with their base URLs.
    
    Returns:
        JSON string with session information
    """
    if not session_cache:
        return "No active sessions. Create one with create_session."
    
    sessions = {}
    for name, session in session_cache.items():
        sessions[name] = {
            "base_url": session["base_url"],
            "has_tokens": bool(session["tokens"])
        }
    
    return json.dumps(sessions, indent=2)

@mcp.tool
def analyze_api_error(error_response: str, endpoint_path: str, method: str = "POST") -> str:
    """
    Analyzes an API error response and provides suggestions for fixing it.
    
    Args:
        error_response: The error response from the API
        endpoint_path: The endpoint that was called
        method: The HTTP method used
    
    Returns:
        Analysis with suggestions for fixing the error
    """
    analysis = {
        "error": error_response,
        "suggestions": []
    }
    
    # Try to parse error as JSON
    try:
        if "HTTP error" in error_response:
            # Extract JSON from error message
            json_start = error_response.find("{")
            if json_start != -1:
                json_str = error_response[json_start:]
                error_data = json.loads(json_str)
                analysis["parsed_error"] = error_data
                
                # Analyze validation errors
                if "detail" in error_data:
                    detail = error_data["detail"]
                    
                    if isinstance(detail, list):
                        for err in detail:
                            field = err.get("loc", [])
                            msg = err.get("msg", "")
                            
                            if "missing" in err.get("type", ""):
                                field_name = field[-1] if field else "unknown"
                                location = field[0] if len(field) > 1 else "unknown"
                                
                                suggestions = []
                                if location == "query":
                                    suggestions.append(f"Add query parameter: ?{field_name}=<value>")
                                    suggestions.append(f"In call_api, use: params={{\"{field_name}\": \"value\"}}")
                                elif location == "body":
                                    suggestions.append(f"Add to JSON body: {{\"{field_name}\": \"value\"}}")
                                    suggestions.append(f"In call_api, use: body={{\"{field_name}\": \"value\"}}")
                                    suggestions.append(f"Or use form_data={{\"{field_name}\": \"value\"}} if multipart/form-data")
                                
                                analysis["suggestions"].extend(suggestions)
    except Exception as e:
        analysis["parse_error"] = str(e)
    
    # Get endpoint requirements for more context
    try:
        openapi = openapi_cache.get('data')
        if openapi:
            paths = openapi.get("paths", {})
            endpoint = paths.get(endpoint_path, {})
            method_details = endpoint.get(method.lower(), {})
            
            request_body = method_details.get("requestBody", {})
            if request_body:
                content = request_body.get("content", {})
                if "multipart/form-data" in content:
                    analysis["endpoint_expects"] = "multipart/form-data (use form_data parameter)"
                elif "application/json" in content:
                    analysis["endpoint_expects"] = "application/json (use body parameter)"
                
                # Get schema reference if available
                for content_type, content_details in content.items():
                    schema = content_details.get("schema", {})
                    if "$ref" in schema:
                        analysis["schema_ref"] = schema["$ref"]
                        analysis["hint"] = f"Use resolve_schema('{schema['$ref']}') to see required fields"
    except Exception as e:
        analysis["context_error"] = str(e)
    
    return json.dumps(analysis, indent=2)

@mcp.tool
def generate_request_example(endpoint_path: str, method: str = "GET", format: str = "curl") -> str:
    """
    Generates a working example request for an endpoint based on the OpenAPI spec.
    
    Args:
        endpoint_path: The API endpoint path
        method: HTTP method (default: "GET")
        format: Output format - "curl", "python", or "http" (default: "curl")
    
    Returns:
        Example request in the specified format
    """
    openapi = openapi_cache.get('data')
    if not openapi:
        return "No OpenAPI spec loaded. Please run list_openapi_endpoints first."
    
    paths = openapi.get("paths", {})
    endpoint = paths.get(endpoint_path)
    
    if not endpoint:
        return f"Endpoint '{endpoint_path}' not found."
    
    method = method.lower()
    method_details = endpoint.get(method)
    
    if not method_details:
        return f"Method '{method.upper()}' not found for endpoint '{endpoint_path}'."
    
    # Build example
    base_url = openapi.get("servers", [{}])[0].get("url", "https://api.example.com")
    url = f"{base_url}{endpoint_path}"
    
    example_params = []
    example_body = {}
    use_form_data = False
    
    # Extract parameters
    parameters = method_details.get("parameters", [])
    for param in parameters:
        name = param.get("name")
        param_in = param.get("in")
        schema = param.get("schema", {})
        param_type = schema.get("type", "string")
        
        if param_in == "query":
            example_value = "value" if param_type == "string" else "123"
            example_params.append(f"{name}={example_value}")
    
    # Extract request body
    request_body = method_details.get("requestBody", {})
    content = request_body.get("content", {})
    
    for content_type, content_details in content.items():
        if "multipart/form-data" in content_type:
            use_form_data = True
        
        schema = content_details.get("schema", {})
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                prop_type = prop_schema.get("type", "string")
                if prop_type == "string":
                    example_body[prop_name] = "example_value"
                elif prop_type == "integer":
                    example_body[prop_name] = 123
                elif prop_type == "boolean":
                    example_body[prop_name] = True
                elif prop_type == "number":
                    example_body[prop_name] = 123.45
    
    # Generate output based on format
    if format == "curl":
        cmd = f"curl -X '{method.upper()}' \\\n"
        
        if example_params:
            url += "?" + "&".join(example_params)
        cmd += f"  '{url}' \\\n"
        cmd += "  -H 'accept: application/json' \\\n"
        
        if example_body:
            if use_form_data:
                for key, value in example_body.items():
                    cmd += f"  -F '{key}={value}' \\\n"
            else:
                cmd += "  -H 'Content-Type: application/json' \\\n"
                cmd += f"  -d '{json.dumps(example_body)}'"
        
        return cmd.rstrip(" \\\n")
    
    elif format == "python":
        code = "import requests\n\n"
        code += f"url = '{url}'\n"
        
        if example_params:
            code += f"params = {json.dumps(dict(p.split('=') for p in example_params), indent=2)}\n"
        else:
            code += "params = {}\n"
        
        if example_body:
            if use_form_data:
                code += f"data = {json.dumps(example_body, indent=2)}\n"
                code += f"\nresponse = requests.{method}(url, params=params, data=data)\n"
            else:
                code += f"json_data = {json.dumps(example_body, indent=2)}\n"
                code += f"\nresponse = requests.{method}(url, params=params, json=json_data)\n"
        else:
            code += f"\nresponse = requests.{method}(url, params=params)\n"
        
        code += "print(response.json())"
        return code
    
    elif format == "http":
        http_req = f"{method.upper()} {endpoint_path}"
        if example_params:
            http_req += "?" + "&".join(example_params)
        http_req += " HTTP/1.1\n"
        http_req += f"Host: {base_url.replace('https://', '').replace('http://', '')}\n"
        http_req += "Accept: application/json\n"
        
        if example_body:
            if use_form_data:
                http_req += "Content-Type: multipart/form-data\n\n"
                for key, value in example_body.items():
                    http_req += f"{key}={value}\n"
            else:
                body_json = json.dumps(example_body, indent=2)
                http_req += "Content-Type: application/json\n"
                http_req += f"Content-Length: {len(body_json)}\n\n"
                http_req += body_json
        
        return http_req
    
    return f"Unsupported format: {format}. Use 'curl', 'python', or 'http'."

@mcp.tool
def call_api(
    base_url: str,
    endpoint: str,
    endpoint_details: str,
    method: str = "GET",
    params: dict = None,
    headers: dict = None,
    body: dict = None,
    form_data: dict = None,
    files: dict = None,
    timeout: float = 10.0
) -> str:
    """
    Makes an API call to the given endpoint with the specified method, parameters, headers, and body.
    Before making the call, first try to get the details for this endpoint using the get_endpoint_details tool if not already available.
    If the OpenAPI spec is not loaded or the endpoint is not found, proceeds with the API call regardless.
    
    Args:
        base_url (str): The base URL of the API.
        endpoint (str): The endpoint path to call.
        endpoint_details (str): The details of the endpoint, typically obtained from get_endpoint_details. Used for reference or validation, but not required for the call itself.
        method (str): The HTTP method to use (GET, POST, etc.).
        params (dict): Query parameters for the request.
        headers (dict): HTTP headers for the request.
        body (dict): JSON body for the request (use when Content-Type is application/json).
        form_data (dict): Form data for the request (use for application/x-www-form-urlencoded or multipart/form-data).
        files (dict): Files to upload. Keys are field names, values are file paths or tuples of (filename, file_content, content_type). Requires form_data to be set.
        timeout (float): Timeout for the request in seconds.
    
    Returns:
        str: The API response as a string, or an error message if the call fails.
    
    Supports all HTTP methods, JSON, form data, and file uploads.
    """
    url = base_url.rstrip("/") + "/" + endpoint.lstrip("/")
    method = method.upper()
    params = params or {}
    headers = headers or {}

    try:
        with httpx.Client(timeout=timeout) as client:
            # Remove Content-Type header if using form_data or files
            # httpx will automatically set it with the correct boundary
            if form_data or files:
                headers = {k: v for k, v in headers.items() if k.lower() != 'content-type'}

            request_kwargs = {
                "method": method,
                "url": url,
                "params": params,
                "headers": headers,
            }

            # If files are present, use multipart/form-data with files and form fields
            if files:
                files_dict = {}
                # Add files
                for field_name, file_info in files.items():
                    if isinstance(file_info, str):
                        with open(file_info, 'rb') as f:
                            files_dict[field_name] = (file_info.split('/')[-1], f.read())
                    elif isinstance(file_info, tuple):
                        files_dict[field_name] = file_info
                    else:
                        files_dict[field_name] = file_info
                # Add form fields as extra multipart fields
                
                if form_data:
                    for field_name, value in form_data.items():
                        if field_name not in files_dict:
                            files_dict[field_name] = (None, str(value))
                request_kwargs["files"] = files_dict
            # If only form_data (no files), use data= for form fields (httpx will use x-www-form-urlencoded)
            elif form_data:
                request_kwargs["data"] = form_data
            # If only body, use JSON
            elif body:
                request_kwargs["json"] = body

            response = client.request(**request_kwargs)
            response.raise_for_status()

            # Try to pretty-print JSON, else return as text
            try:
                return json.dumps(response.json(), indent=2)
            except Exception:
                return response.text
    except httpx.HTTPStatusError as e:
        return f"HTTP error {e.response.status_code}: {e.response.text}"
    except httpx.RequestError as e:
        return f"Request error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    mcp.run()