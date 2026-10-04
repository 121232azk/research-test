#!/usr/bin/env python3
"""
Format and finalize HTML newsletter content.

This tool takes HTML content and image results, formats them into a complete
newsletter, and handles final touches like optimization and metadata.
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HTMLFormattingError(Exception):
    """Custom exception for HTML formatting errors."""
    pass

class HTMLFormatter:
    def __init__(self):
        # Load configuration
        self.template_path = os.getenv('NEWSLETTER_TEMPLATE_PATH', './templates/newsletter.html')
        self.output_quality = os.getenv('OUTPUT_QUALITY', 'high')  # high, medium, low
        self.optimize_images = os.getenv('OPTIMIZE_IMAGES', 'true').lower() == 'true'
        self.max_image_size = int(os.getenv('MAX_IMAGE_SIZE', '500000'))  # bytes

        # Load custom template if available
        self.custom_template = self._load_template()

    def _load_template(self) -> Optional[str]:
        """
        Load HTML newsletter template.

        Args:
            template_path: Path to template file

        Returns:
            Template string or None if file doesn't exist
        """
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Warning: Could not load template {self.template_path}: {str(e)}")
            return None

    def format_newsletter(self, html_content: str, image_results: List[Dict[str, Any]],
                         metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format newsletter HTML content with images and metadata.

        Args:
            html_content: Base HTML content
            image_results: List of generated image results
            metadata: Optional metadata dictionary

        Returns:
            Dictionary containing formatted newsletter and metadata
        """
        if metadata is None:
            metadata = {}

        # Process and optimize images
        processed_images = self._process_images(image_results)

        # Inject images into HTML content
        formatted_html = self._inject_images(html_content, processed_images)

        # Add metadata and optimization
        final_html = self._apply_template(formatted_html, processed_images, metadata)

        # Generate final metadata
        final_metadata = self._generate_metadata(metadata, processed_images, len(formatted_html))

        return {
            "html_content": final_html,
            "metadata": final_metadata,
            "processed_images": processed_images,
            "formatting_info": {
                "template_used": self.template_path if self.custom_template else "default",
                "image_count": len(processed_images),
                "formatting_timestamp": datetime.now().isoformat(),
                "output_quality": self.output_quality,
                "images_optimized": self.optimize_images
            }
        }

    def _process_images(self, image_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and optimize images for newsletter inclusion.

        Args:
            image_results: List of image generation results

        Returns:
            List of processed image information
        """
        processed = []

        for result in image_results:
            image_data = result.get('image_data', {})

            if image_data and 'data' in image_data:
                # Create processed image info
                processed_image = {
                    "prompt": result.get('prompt', ''),
                    "model": result.get('model', ''),
                    "generation_timestamp": result.get('generation_timestamp', ''),
                    "mime_type": image_data.get('mime_type', 'image/png'),
                    "original_size": image_data.get('size', 0),
                    "optimized": False
                }

                # Check if optimization is needed
                if self.optimize_images and processed_image["original_size"] > self.max_image_size:
                    try:
                        # TODO: Implement actual image optimization
                        # For now, mark as needing optimization
                        processed_image["optimized"] = True
                        processed_image["optimization_note"] = "Image exceeds size limit"
                    except Exception as e:
                        processed_image["optimization_error"] = str(e)

                processed.append(processed_image)
            else:
                # Handle text-based responses or missing image data
                processed.append({
                    "prompt": result.get('prompt', ''),
                    "model": result.get('model', ''),
                    "generation_timestamp": result.get('generation_timestamp', ''),
                    "type": "text_response",
                    "content": image_data.get('text_description', '') if isinstance(image_data, dict) else None,
                    "original_size": 0,
                    "optimized": False
                })

        return processed

    def _inject_images(self, html_content: str, processed_images: List[Dict[str, Any]]) -> str:
        """
        Inject processed images into HTML content.

        Args:
            html_content: Base HTML content
            processed_images: List of processed images

        Returns:
            HTML content with images injected
        """
        # Look for image placeholders in HTML
        # Common patterns: [[IMAGE_1]], {{IMAGE_2}}, <!-- IMAGE_INSERTION:1 -->
        formatted_html = html_content

        # If no placeholders found, add images to a dedicated section
        if not re.search(r'\[\[IMAGE_\d+\]\]|\{\{IMAGE_\d+\}\}|<!-- IMAGE_INSERTION:\d+ -->', formatted_html):
            # Add image gallery section
            image_gallery = self._create_image_gallery(processed_images)

            # Insert before closing body tag
            formatted_html = formatted_html.replace('</body>', f'{image_gallery}\n</body>')
        else:
            # Replace placeholders with actual images
            for i, image in enumerate(processed_images):
                placeholder_patterns = [
                    f'[[IMAGE_{i+1}]]',
                    f'{{{{IMAGE_{i+1}}}}}',
                    f'<!-- IMAGE_INSERTION:{i+1} -->'
                ]

                for pattern in placeholder_patterns:
                    if pattern in formatted_html:
                        image_html = self._create_image_html(image)
                        formatted_html = formatted_html.replace(pattern, image_html)

        return formatted_html

    def _create_image_gallery(self, processed_images: List[Dict[str, Any]]) -> str:
        """
        Create HTML for image gallery.

        Args:
            processed_images: List of processed images

        Returns:
            HTML string for image gallery
        """
        if not processed_images:
            return ""

        gallery_html = """
<section style="margin: 50px 0; background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
    <h2 style="text-align: center; color: #333; margin-bottom: 30px;">Visual Content</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px; padding: 20px;">
"

        for image in processed_images:
            gallery_html += self._create_image_html(image) + "\n"

        gallery_html += """
    </div>
</section>
"""

        return gallery_html

    def _create_image_html(self, image: Dict[str, Any]) -> str:
        """
        Create HTML for a single image.

        Args:
            image: Processed image information

        Returns:
            HTML string for the image
        """
        if image.get('type') == 'text_response':
            # Handle text-based responses
            return f"""
    <div style="background: white; padding: 20px; border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;">
        <p style="color: #666; font-style: italic; margin: 0;">
            {image.get('prompt', 'Image not generated')}
        </p>
        {f'<p style="color: #999; font-size: 0.9em; margin-top: 10px;">Generated via: {image.get("model", "")}</p>' if image.get("model") else ''}
    </div>
"""

        # Handle actual images
        image_base64 = image.get('data', '')
        if image_base64:
            mime_type = image.get('mime_type', 'image/png')

            # TODO: Add actual base64 image embedding here
            # For now, use placeholder
            return f"""
    <div style="background: white; padding: 15px; border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center;">
        <div style="width: 100%; height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 5px; margin-bottom: 15px;
                    display: flex; align-items: center; justify-content: center;">
            <span style="color: white; font-weight: bold; padding: 20px;
                         text-align: center;">{image.get('prompt', 'Newsletter Image')}</span>
        </div>
        <p style="color: #666; font-size: 0.9em; margin: 0;">
            {image.get('prompt', '')}
        </p>
        <p style="color: #999; font-size: 0.8em; margin-top: 8px;">
            Generated via: {image.get('model', '')} | Size: {image.get('original_size', 0)} bytes
        </p>
        {f'<p style="color: #e74c3c; font-size: 0.8em; margin-top: 5px;">Requires optimization</p>' if image.get('optimized') else ''}
    </div>
"""

        # Fallback for missing image data
        return f"""
    <div style="background: #f5f5f5; padding: 30px; border-radius: 8px;
                border: 2px dashed #ddd; text-align: center;">
        <p style="color: #999; font-style: italic; margin: 0;">
            Image placeholder: {image.get('prompt', 'Newsletter Image')}
        </p>
    </div>
"""

    def _apply_template(self, html_content: str, processed_images: List[Dict[str, Any]],
                       metadata: Dict[str, Any]) -> str:
        """
        Apply custom template if available, otherwise add final touches.

        Args:
            html_content: HTML content
            processed_images: List of processed images
            metadata: Metadata dictionary

        Returns:
            Final formatted HTML
        """
        if self.custom_template:
            # Replace template placeholders
            template = self.custom_template

            # Add metadata comments for debugging
            metadata_comment = f"<!-- Generated: {datetime.now().isoformat()} -->\n"
            metadata_comment += f"<!-- Images: {len(processed_images)} -->\n"

            template = template.replace('<!-- METADATA_INJECTION -->', metadata_comment)

            # Add image gallery if needed
            if '{{IMAGE_GALLERY}}' in template:
                image_gallery = self._create_image_gallery(processed_images)
                template = template.replace('{{IMAGE_GALLERY}}', image_gallery)

            return template
        else:
            # Add final touches to default HTML
            return self._add_final_touches(html_content)

    def _add_final_touches(self, html_content: str) -> str:
        """
        Add final touches to HTML content.

        Args:
            html_content: HTML content

        Returns:
            HTML with final touches
        """
        # Add meta tags if not present
        if '<meta name="generator"' not in html_content:
            generator_meta = f'        <meta name="generator" content="AI Newsletter System {datetime.now().strftime("%Y.%m.%d")}">\n'
            html_content = html_content.replace('</head>', f'{generator_meta}</head>')

        # Add styling for responsive design
        responsive_style = """
        <style>
            @media (max-width: 600px) {
                .image-gallery {
                    grid-template-columns: 1fr !important;
                }
            }

            .image-container:hover {
                transform: scale(1.02);
                transition: transform 0.3s ease;
            }
        </style>
"""

        # Insert responsive styles before closing head
        if '<style>' in html_content and '</style>' in html_content:
            html_content = html_content.replace('</style>', f'{responsive_style}</style>')

        # Add timestamp footer if not present
        if 'generated by AI Newsletter System' not in html_content.lower():
            timestamp = f"<!-- Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')} by AI Newsletter System -->"
            html_content = html_content.replace('</body>', f'{timestamp}\n</body>')

        return html_content

    def _generate_metadata(self, base_metadata: Dict[str, Any],
                          processed_images: List[Dict[str, Any]],
                          html_length: int) -> Dict[str, Any]:
        """
        Generate comprehensive metadata.

        Args:
            base_metadata: Base metadata
            processed_images: List of processed images
            html_length: Length of HTML content

        Returns:
            Final metadata dictionary
        """
        # Calculate image statistics
        image_stats = {
            "total_generated": len(processed_images),
            "with_image_data": len([img for img in processed_images if img.get('type') != 'text_response']),
            "text_responses": len([img for img in processed_images if img.get('type') == 'text_response']),
            "optimized_count": len([img for img in processed_images if img.get('optimized')]),
            "total_original_size": sum(img.get('original_size', 0) for img in processed_images)
        }

        return {
            "generation_metadata": {
                "generated_at": datetime.now().isoformat(),
                "system": "AI Newsletter Formatter v1.0",
                "html_length": html_length,
                "word_count": len(html_content.split()) if html_content else 0
            },
            "content_metadata": base_metadata,
            "image_metadata": image_stats,
            "formatting_metadata": {
                "template_used": self.template_path if self.custom_template else "default",
                "quality_setting": self.output_quality,
                "image_optimization": self.optimize_images,
                "max_image_size": self.max_image_size
            },
            "technical_metadata": {
                "charset": "UTF-8",
                "viewport": "width=device-width, initial-scale=1.0",
                "doctypes": ["html5"],
                "validation": "basic"
            }
        }

def main():
    """CLI interface for the HTML formatting tool."""
    if len(sys.argv) < 2:
        print("Usage: python format_html.py <html_file> [image_results_file] [output_file]")
        print("Example: python format_html.py newsletter.html ./tmp/images.json formatted_newsletter.html")
        return

    html_file = sys.argv[1]
    image_file = sys.argv[2] if len(sys.argv) > 2 else None
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        # Load HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Load image results if available
        image_results = []
        if image_file and os.path.exists(image_file):
            with open(image_file, 'r', encoding='utf-8') as f:
                image_results = json.load(f)

        # Format newsletter
        formatter = HTMLFormatter()
        formatted = formatter.format_newsletter(html_content, image_results)

        # Save formatted newsletter
        if not output_file:
            output_file = f"./tmp/formatted_newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted['html_content'])

        print(f"Formatted newsletter saved to: {output_file}")

        # Print formatting info
        info = formatted['formatting_info']
        print(f"\n=== Formatting Information ===")
        print(f"Template used: {info['template_used']}")
        print(f"Images processed: {info['image_count']}")
        print(f"Quality setting: {info['output_quality']}")
        print(f"Images optimized: {info['images_optimized']}")
        print(f"Generated at: {info['formatting_timestamp']}")

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    import json
    exit(main())