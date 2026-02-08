# AI and Contextual Features in Dishto

The Dishto platform incorporates several Artificial Intelligence (AI) and contextual features to enhance user experience, streamline content creation, and provide intelligent search capabilities. These features leverage modern AI models and specialized databases to deliver powerful functionalities.

## 1. Contextual Menu Item Search

This feature allows users to search for menu items not just by keywords, but by their semantic meaning and context.

*   **Mechanism:**
    *   **Vector Embeddings:** Each menu item's name and description are transformed into a numerical vector (embedding) that captures its semantic meaning.
    *   **Qdrant Vector Database:** These embeddings are stored in Qdrant, a high-performance vector similarity search engine.
*   **How it Works:**
    1.  **Embedding Generation:** When a `MenuItem` is created or updated, a `pre_save` signal triggers an asynchronous **Celery task** (`generate_menu_item_embedding_task`). This task utilizes a **Large Language Model (LLM)** to convert the menu item's name and description into a vector embedding. The project's `requirements.txt` suggests tools like `google-genai` and `langchain` are used for this.
    2.  **Storage:** The generated vector embedding is then stored in a dedicated collection within the **Qdrant** database, alongside the menu item's identifier.
    3.  **Search Query:** When a user performs a search (`/open/menu/{outlet_slug}/search/contextual` endpoint), their query is also converted into a vector embedding using the same LLM.
    4.  **Similarity Search:** This query vector is then sent to Qdrant, which efficiently finds the most semantically similar menu item embeddings.
    5.  **Results:** The system returns menu items that are contextually relevant to the user's search, even if the exact keywords are not present in the item's description.
*   **Technologies Used:** Google Generative AI (for LLM), Langchain (for LLM interaction), Qdrant, Celery, Redis.

## 2. AI-Powered Menu Item Description Enhancement

This feature assists outlet administrators in creating engaging and descriptive menu item descriptions.

*   **Mechanism:** An explicit API endpoint allows for sending a basic menu item name and description to an AI model, which then returns an enhanced, more appealing version.
*   **How it Works:**
    1.  **API Call:** An administrator calls the `GET /restaurant/{outlet_slug}/items/enhance_description_with_ai` endpoint, providing the item's name and current description.
    2.  **Service Interaction:** The `Restaurant.service.MenuService` processes this request and calls a utility function (`Restaurant.utils.enhance_menu_item_description_with_ai`).
    3.  **LLM Processing:** This utility function interfaces with an **LLM** (likely via `google-genai` and `langchain`) to generate a more creative, detailed, or appetizing description based on the input.
    4.  **Return Enhanced Description:** The enhanced text is returned to the administrator, who can then choose to use it for the menu item.
*   **Technologies Used:** Google Generative AI (for LLM), Langchain.

## 3. AI-Powered Image Generation

To ensure that every menu item and category has a visually appealing representation, the platform can automatically generate photorealistic images using AI.

*   **Mechanism:** When a menu item or category is created without an explicit image upload, the system can prompt an AI image generation model to create a relevant image.
*   **How it Works (Menu Items):**
    1.  **No Image Upload:** If an administrator creates a menu item via the `/restaurant/{outlet_slug}/items/no-image` endpoint (which specifically bypasses manual image upload), the system detects the absence of an image.
    2.  **AI Generation Trigger:** The `Restaurant.service.MenuService` then calls `Restaurant.utils.generate_menu_item_image`.
    3.  **Image Synthesis:** This utility function interacts with an **AI Image Generation model** (likely Google Generative AI) using the menu item's name and description as prompts to synthesize a photorealistic image.
    4.  **Image Association:** The generated image is then saved and associated with the menu item.
*   **How it Works (Menu Categories):**
    1.  **Category Creation:** During the creation of a `MenuCategory` via `Restaurant.service.MenuService.create_menu_category`, if a pre-existing `CategoryImage` for that category name is not found, the system can trigger image generation.
    2.  **AI Generation Trigger:** The `Restaurant.utils.generate_menu_category_image` function is invoked.
    3.  **Image Synthesis:** Similar to menu items, an **AI Image Generation model** creates an image based on the category name.
    4.  **Image Association:** The generated image is saved as a `CategoryImage` and linked to the `MenuCategory`.
*   **Technologies Used:** Google Generative AI (for AI Image Generation).

These AI and contextual features collectively provide a more intelligent and user-friendly experience for both the administrators managing the restaurant content and the end-users exploring the menu.
