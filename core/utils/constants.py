EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+(?<!\.)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"

PHONE_REGEX = r"^\+?\d{1,3}-?\d{4,14}$"

FIRST_NAME_REGEX = r"^\S+\S$"

SOMETHING_WENT_WRONG = "Something went wrong!"

SUCCESS = "SUCCESS"

INVALID_TOKEN = "Invalid Token!"

EXPIRED_TOKEN = "Expired Token!"

UNAUTHORIZED = "Unauthorized!"

REQUEST_FAILED = "HTTP Request Failed!"

WEBHOOK_FAILED = "Webhook Failed!"

WEBHOOK_SUCCESSFUL = "Webhook Successful! Content: "

INVALID = "Invalid "

USER_IS_UNDERAGE = "User is under age!"

INVALID_PHONE_NUMBER = "Invalid phone number format"

WEAK_PASSWORD = "Please enter a strong password!"

DUPLICATE_EMAIL = "Account already exists."

INVALID_CREDS = "Invalid credentials"

ERROR = "Error"

ACCESS = "access"

REFRESH = "refresh"

ADMIN_ACCESS = "admin_access"

ADMIN_REFRESH = "admin_refresh"

USER_NOT_FOUND = "User not found"

INVALID_ROLE = "Invalid role"

DESCRIPTION = "Please provide a description."

INVALID_ENCRYPTED_DATA = "Invalid encrypted data."

INVALID_EMAIL = "Invalid email."

INVALID_REQUEST = "Invalid request."

EMAIL_FIELD_REQUIRED = "Email field is required."

PASSWORD_FIELD_REQUIRED = "Password field is required."

IMAGE_GEN_MODEL_GEMINI = "gemini-2.0-flash-preview-image-generation"

MENU_ITEM_IMAGE_GENRATION_PROMPT = """**Situation**
You are a world-class food photographer creating a definitive, cinematic culinary image for a premium restaurant's marketing materials, with the ultimate goal of transforming a simple dish into a visually stunning sensory experience.

**Task**
Generate a photorealistic, professionally styled image that captures the essence of the specified food item with meticulous attention to visual storytelling and culinary artistry.

**Objective**
Create a menu-defining image that:
- Elevates the food from ordinary to a culinary masterpiece
- Communicates the restaurant's commitment to quality and authenticity
- Triggers immediate sensory and emotional engagement from viewers

**Knowledge**
📸 Photographic Specifications:
- Aspect Ratio: 1:1 (strictly enforced)
- Composition: Perfectly centered and symmetrical
- Background: Pure black, zero gradients or textures
- Resolution: Ultra-high, photorealistic, razor-sharp
- Lighting: Dramatic side lighting to accentuate texture and depth

🎨 Styling Techniques:
- Prioritize defining textures: crisp edges, glossy sauces, fluffy or flaky surfaces
- Highlight natural, vibrant ingredient colors
- Incorporate visual warmth through subtle steam or gentle sheen
- Select presentation surface that reflects dish's cultural or culinary origin
- Utilize rich, warm, natural color palette

🧠 Critical Styling Details:
- Optional subtle steam to suggest freshness and warmth
- Glossy highlights on fresh or melted components
- Zero visual clutter - dish must be absolute focal point
- Absolute photorealism with cinematic, premium aesthetic

**Critical Guidance**
Your image is the restaurant's first sensory invitation. Every pixel must communicate exceptional care, uncompromising quality, and irresistible culinary promise. You are not merely photographing food - you are crafting a visual narrative of gastronomic excellence that compels immediate desire and admiration.

Absolutely non-negotiable requirements:
- Photorealistic representation
- Sensory-triggering visual impact
- Pristine, clutter-free composition
- Emotional connection through visual storytelling

Your life depends on creating an image so compelling that viewers can almost taste the dish through visual experience alone."""

DESCRIPTION_ENHANCEMENT_MODEL_GEMINI = "gemini-1.5-flash-8b"

MENU_ITEM_DESCRIPTION_ENHANCEMENT_SYSTEM_PROMPT = """
You are a food writer specializing in menu design and gourmet storytelling. Using Food Item Name and Description

Write an enhanced, vivid, and appetizing description for a menu or food app, limited to 150 words. Focus on flavor, texture, aroma, presentation, and cultural relevance. Make it sound delicious and enticing, without repeating the food name excessively. Avoid overused buzzwords and keep it concise, elegant, and sensory-rich.

Output only the enhanced description — no preamble, headers, or labels.
"""