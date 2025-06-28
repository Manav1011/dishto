import os
import uuid
import mimetypes
import asyncio
from google import genai
from google.genai import types
from django.core.files.base import ContentFile
from core.utils.constants import MENU_ITEM_IMAGE_GENRATION_PROMPT
from anyio import to_thread  # Use anyio for FastAPI compatibility
import asyncio

GEMINI_IMAGE_SEMAPHORE = asyncio.Semaphore(9)

def _blocking_gemini_image(food_name: str, description:str, prompt: str, model: str, generate_content_config) -> ContentFile:
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
        types.Content(role="model", parts=[types.Part.from_text(
            text="Okay, I understand the situation and the task. I will generate a photorealistic image of a meticulously styled food dish, perfectly centered on a pure black background with dramatic side lighting to highlight its textures and vibrant colors. The composition will be pristine and clutter-free, aiming to create a sensory-triggering visual impact that communicates the restaurant's commitment to quality and authenticity. The aspect ratio will be 4:3, and the resolution will be ultra-high, ensuring a cinematic and premium aesthetic.\n\nPlease specify the food item you would like me to generate an image of."
        )]),
        types.Content(role="user", parts=[types.Part.from_text(text=food_name)]),
        types.Content(role="user", parts=[types.Part.from_text(text=description)]),
    ]
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates
            and chunk.candidates[0].content
            and chunk.candidates[0].content.parts
            and chunk.candidates[0].content.parts[0].inline_data
            and chunk.candidates[0].content.parts[0].inline_data.data
        ):
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".jpg"
            file_name = f"{food_name}_{uuid.uuid4().hex}{file_extension}"
            return ContentFile(data_buffer, name=file_name)
    raise RuntimeError("No image data returned from Gemini.")

async def generate_menu_item_image(food_name: str, description: str, max_retries: int = 3, delay: float = 2.0) -> ContentFile:
    """
    Generates a photorealistic menu item image using Gemini and returns a Django ContentFile.
    Runs the blocking Gemini call in a thread to avoid blocking the event loop.
    Retries on failure.
    """
    model = "gemini-2.0-flash-preview-image-generation"
    prompt = MENU_ITEM_IMAGE_GENRATION_PROMPT
    generate_content_config = types.GenerateContentConfig(
        temperature=2,
        top_p=1,
        response_modalities=["IMAGE", "TEXT"],
        response_mime_type="text/plain",
    )

    last_exception = None
    async with GEMINI_IMAGE_SEMAPHORE:
        for attempt in range(1, max_retries + 1):
            try:
                result = await to_thread.run_sync(
                    _blocking_gemini_image,
                    description,
                    food_name,
                    prompt,
                    model,
                    generate_content_config,
                )
                return result
            except Exception as e:
                last_exception = e
                print(f"[Gemini] Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                await asyncio.sleep(delay)
    raise RuntimeError(f"Failed to generate image from Gemini after {max_retries} attempts. Last error: {last_exception}")