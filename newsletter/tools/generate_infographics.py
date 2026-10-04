#!/usr/bin/env python3
"""
Generate infographics using Google Gemini API (Nano Banana models).

This tool creates professional newsletter graphics and images using
Google's Gemini Imagen models, saving results to .tmp/ for processing.
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Rate limit handling
GEMINI_RATE_LIMIT_PER_MIN = 5  # Max 5 requests per minute
GEMINI_RATE_LIMIT_PER_DAY = 100  # Max 100 requests per day

class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors."""
    pass

class GenerateInfographicsTool:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise GeminiAPIError("GOOGLE_API_KEY not found in environment")

        # Use Gemini API base URL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

        # Default model - can be configured
        self.default_model = "gemini-3.1-flash-image"

        # Headers for API calls
        self.headers = {
            "Content-Type": "application/json"
        }

    def generate_image(self, prompt: str, model: Optional[str] = None,
                      output_format: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an image from a text prompt using Gemini API.

        Args:
            prompt: Text description of the image to generate
            model: Gemini model to use (defaults to gemini-3.1-flash-image)
            output_format: Optional output format preference

        Returns:
            Dictionary containing generation result with metadata
        """
        model = model or self.default_model

        # Build the payload for text-to-image generation
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        if output_format:
            # Add output format if supported by model
            pass

        try:
            # Make API call
            url = f"{self.base_url}/models/{model}:generateContent"
            params = {"key": self.api_key}

            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                params=params,
                timeout=120
            )

            response.raise_for_status()

            result = response.json()

            # Extract image data if available
            image_data = self._extract_image_data(result)

            # Generate result structure
            generation_result = {
                "prompt": prompt,
                "model": model,
                "generation_timestamp": datetime.now().isoformat(),
                "api_response": result,
                "image_data": image_data,
                "success": True
            }

            return generation_result

        except requests.exceptions.RequestException as e:
            raise GeminiAPIError(f"Gemini API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise GeminiAPIError(f"Failed to parse Gemini API response: {str(e)}")
        except Exception as e:
            raise GeminiAPIError(f"Unexpected error in Gemini API call: {str(e)}")

    def _extract_image_data(self, api_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract image data from API response.

        Args:
            api_response: Raw API response

        Returns:
            Image data dictionary or None
        """
        try:
            # Look for image data in various possible locations
            if "candidates" in api_response and api_response["candidates"]:
                candidate = api_response["candidates"][0]

                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]

                    # Look for inline_data (base64 encoded image)
                    for part in parts:
                        if "inline_data" in part:
                            image_info = {
                                "mime_type": part["inline_data"].get("mime_type", "image/png"),
                                "data": part["inline_data"].get("data", ""),
                                "size": len(part["inline_data"].get("data", ""))
                            }

                            return image_info

            # Look for text-based image data or other formats
            if "candidates" in api_response and api_response["candidates"]:
                candidate = api_response["candidates"][0]

                # Check if response contains text description of generated image
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]

                    for part in parts:
                        if "text" in part:
                            return {
                                "text_description": part["text"],
                                "type": "text_response"
                            }

            return None

        except Exception as e:
            # Log error but don't fail the whole process
            return {"error": f"Failed to extract image data: {str(e)}"}

    def save_image_result(self, result: Dict[str, Any], output_path: str = None,
                         create_filename: bool = True) -> str:
        """
        Save image generation result to file.

        Args:
            result: Generation result dictionary
            output_path: Path to save file
            create_filename: Whether to create filename from prompt

        Returns:
            Path where file was saved
        """
        if not output_path:
            if create_filename:
                # Create filename from prompt
                prompt = result.get("prompt", "infographic")
                filename = prompt.replace(" ", "_").replace("/", "_")[:50]
                output_path = f"./tmp/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                output_path = f"./tmp/image_generation_result.json"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # For image data, save as binary if available
        image_data = result.get("image_data", {})
        if image_data and "data" in image_data:
            # If it's base64 data, save the binary
            try:
                image_binary_path = output_path.replace('.json', '.png')

                if image_data.get("mime_type") == "image/png" and image_data["data"]:
                    # Decode base64 and save
                    image_bytes = base64.b64decode(image_data["data"])

                    with open(image_binary_path, 'wb') as f:
                        f.write(image_bytes)

                    print(f"Generated image saved to: {image_binary_path}")
                    print(f"Image size: {image_data['size']} bytes")

            except Exception as e:
                print(f"Warning: Could not save binary image: {str(e)}")

        # Always save the JSON result
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return output_path

    def create_newsletter_header(self, topic: str, style: str = "professional") -> Dict[str, Any]:
        """
        Create a newsletter header image.

        Args:
            topic: Newsletter topic
            style: Header style (professional, modern, bold, etc.)

        Returns:
            Generation result dictionary
        """
        prompt = f"Create a professional newsletter header image for topic '{topic}'. Style: {style}. " \
                 f"Include modern design elements, clean typography area for title, and relevant visual metaphors. " \
                 f"Use a professional color palette with good contrast for digital display."

        return self.generate_image(prompt, self.default_model)

    def create_infographic_element(self, topic: str, element_type: str) -> Dict[str, Any]:
        """
        Create an infographic element for the newsletter.

        Args:
            topic: Newsletter topic
            element_type: Type of element (chart, diagram, icon, etc.)

        Returns:
            Generation result dictionary
        """
        prompt = f"Create a {element_type} infographic element for a newsletter about '{topic}'. " \
                 f"Make it visually clear, professional, and suitable for digital newsletter integration. " \
                 f"Use clean design with good readability."

        return self.generate_image(prompt, self.default_model)

def main():
    """CLI interface for the infographics tool."""
    if len(sys.argv) < 2:
        print("Usage: python generate_infographics.py <prompt> [model]")
        print("Example: python generate_infographics.py \"Newsletter header about AI trends\" gemini-3.1-flash-image")
        return

    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        tool = GenerateInfographicsTool()

        print(f"Generating image with prompt: {prompt}")
        if model:
            print(f"Using model: {model}")

        result = tool.generate_image(prompt, model)

        if result["success"]:
            print("\n=== Image Generation Result ===")
            print(f"Prompt: {result['prompt']}")
            print(f"Model: {result['model']}")
            print(f"Timestamp: {result['generation_timestamp']}")

            if result.get("image_data"):
                image_info = result["image_data"]
                if "size" in image_info:
                    print(f"Image size: {image_info['size']} bytes")
                if "mime_type" in image_info:
                    print(f"Image type: {image_info['mime_type']}")

            # Save results
            output_path = tool.save_image_result(result)
            print(f"Results saved to: {output_path}")

            # If text response available, show it
            if "text_description" in result.get("image_data", {}):
                print(f"\n=== Text Response ===")
                print(result["image_data"]["text_description"])

        else:
            print("Image generation failed")
            return 1

    except GeminiAPIError as e:
        print(f"Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    exit(main())