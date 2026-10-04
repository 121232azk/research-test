#!/usr/bin/env python3
"""
Generate newsletter content from research and template.

This tool creates professional newsletter content based on research results
and integrates generated images, following the WAT framework for content creation.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ContentGenerationError(Exception):
    """Custom exception for content generation errors."""
    pass

class WriteContentTool:
    def __init__(self):
        # Load configuration
        self.newsletter_title = os.getenv('NEWSLETTER_TITLE', 'AI Trends Newsletter')
        self.author_name = os.getenv('NEWSLETTER_AUTHOR', 'AI Insights Team')
        self.email_signature = os.getenv('NEWSLETTER_SIGNATURE',
            'Best regards,\nAI Insights Team\nhttps://example.com')

        # Load templates if available
        self.header_template = self._load_template('templates/header.html')
        self.intro_template = self._load_template('templates/intro.html')
        self.body_template = self._load_template('templates/body.html')
        self.footer_template = self._load_template('templates/footer.html')

    def _load_template(self, template_path: str) -> Optional[str]:
        """
        Load HTML template from file.

        Args:
            template_path: Path to template file

        Returns:
            Template string or None if file doesn't exist
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Warning: Could not load template {template_path}: {str(e)}")
            return None

    def generate_newsletter(self, research_result: Dict[str, Any],
                          image_results: List[Dict[str, Any]],
                          topic: str = None) -> Dict[str, Any]:
        """
        Generate complete newsletter content from research and images.

        Args:
            research_result: Research data from Perplexity
            image_results: List of generated image results
            topic: Newsletter topic (if not in research)

        Returns:
            Dictionary containing complete newsletter HTML and metadata
        """
        # Use topic from research or parameter
        newsletter_topic = topic or research_result.get('topic', 'Latest Trends')

        # Generate components
        header_html = self._generate_header(newsletter_topic, research_result)
        intro_html = self._generate_intro(research_result)
        body_html = self._generate_body(research_result)
        images_html = self._integrate_images(image_results)
        call_to_action_html = self._generate_call_to_action()
        footer_html = self._generate_footer()

        # Assemble complete newsletter
        complete_html = self._assemble_newsletter(
            header_html, intro_html, body_html,
            images_html, call_to_action_html, footer_html
        )

        # Generate metadata
        metadata = {
            "topic": newsletter_topic,
            "author": self.author_name,
            "generated_at": datetime.now().isoformat(),
            "research_sources": len(research_result.get('citations', [])),
            "images_used": len(image_results),
            "template_version": "1.0",
            "content_sections": [
                "header", "intro", "body", "visuals",
                "call_to_action", "footer"
            ]
        }

        return {
            "html_content": complete_html,
            "metadata": metadata,
            "components": {
                "header": header_html,
                "intro": intro_html,
                "body": body_html,
                "images": images_html,
                "call_to_action": call_to_action_html,
                "footer": footer_html
            }
        }

    def _generate_header(self, topic: str, research_result: Dict[str, Any]) -> str:
        """Generate newsletter header."""
        if self.header_template:
            # Use custom template with placeholders
            header = self.header_template.replace('{{title}}', topic)
            header = header.replace('{{date}}', datetime.now().strftime('%B %d, %Y'))
            header = header.replace('{{author}}', self.author_name)
            return header
        else:
            # Default header generation
            return f"""
<header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white; padding: 40px; text-align: center; border-radius: 8px; margin-bottom: 30px;">
    <h1 style="font-size: 2.5em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{topic}</h1>
    <p style="font-size: 1.2em; margin: 10px 0 0 0; opacity: 0.9;">by {self.author_name}</p>
    <p style="font-size: 0.9em; margin: 5px 0 0 0; opacity: 0.8;">{datetime.now().strftime('%B %d, %Y')}</p>
</header>
"""

    def _generate_intro(self, research_result: Dict[str, Any]) -> str:
        """Generate newsletter introduction."""
        if self.intro_template:
            # Replace research summary placeholder
            response = research_result.get('response', '')
            intro_preview = response[:200] + "..." if len(response) > 200 else response

            intro = self.intro_template.replace('{{preview}}', intro_preview)
            intro = intro.replace('{{word_count}}', str(len(response.split())))
            return intro
        else:
            response = research_result.get('response', '')
            summary = response[:300] + "..." if len(response) > 300 else response

            return f"""
<section style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 30px; border-left: 4px solid #667eea;">
    <h2 style="color: #333; margin-top: 0;">Introduction</h2>
    <p style="font-size: 1.1em; line-height: 1.6; color: #555;">{summary}</p>
    <p style="color: #666; font-size: 0.9em; margin-top: 15px;">
        <strong>Quick Stats:</strong> {len(response.split())} words | {len(research_result.get('citations', []))} sources
    </p>
</section>
"""

    def _generate_body(self, research_result: Dict[str, Any]) -> str:
        """Generate newsletter body content."""
        if self.body_template:
            # Use custom template
            response = research_result.get('response', '')
            body = self.body_template.replace('{{content}}', response)

            # Add structured sections based on response
            if research_result.get('citations'):
                citations_html = ""
                for i, citation in enumerate(research_result['citations'], 1):
                    citations_html += f"<li style='margin: 8px 0;'>{citation}</li>"

                body += f"""
<div style="margin-top: 30px;">
    <h3 style="color: #333;">Sources & References</h3>
    <ul style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">{citations_html}</ul>
</div>
"""

            return body
        else:
            response = research_result.get('response', '')
            citations = research_result.get('citations', [])

            # Structure content based on response
            sections = self._structure_content(response)

            body_html = ""
            for section in sections:
                body_html += f"""
<section style="margin-bottom: 30px;">
    <h3 style="color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">{section['title']}</h3>
    <p style="line-height: 1.7; color: #555;">{section['content']}</p>
</section>
"""

            if citations:
                citations_html = ""
                for i, citation in enumerate(citations, 1):
                    citations_html += "<li style='margin: 10px 0; padding-left: 10px; border-left: 3px solid #ddd;'>\n                        <strong>" + str(i) + ".</strong> " + citation + "\n                    </li>"

                body_html += f"""
<section style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-top: 30px;">
    <h3 style="color: #333; margin-top: 0;">Sources & References</h3>
    <ul style="list-style: none; padding: 0;">{citations_html}</ul>
</section>
"""

            return body_html

    def _structure_content(self, content: str) -> List[Dict[str, str]]:
        """
        Structure content into logical sections.

        Args:
            content: Raw content text

        Returns:
            List of structured sections
        """
        sections = []

        # Simple structure detection based on content
        lines = content.split('\n')
        current_section = "Overview"
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers (lines that start with ##, ###, or are all caps)
            if (line.startswith('## ') or line.startswith('### ') or
                (line.isupper() and len(line) > 10 and len(line) < 50)):
                # Save previous section
                if current_content:
                    sections.append({
                        'title': current_section,
                        'content': ' '.join(current_content)
                    })

                current_section = line.replace('#', '').strip()
                current_content = []
            else:
                current_content.append(line)

        # Add last section
        if current_content:
            sections.append({
                'title': current_section,
                'content': ' '.join(current_content)
            })

        return sections if sections else [{
            'title': 'Content',
            'content': content
        }]

    def _integrate_images(self, image_results: List[Dict[str, Any]]) -> str:
        """Integrate generated images into the newsletter."""
        if not image_results:
            return ""

        images_html = """
<div style="margin: 40px 0; text-align: center;">
    <h3 style="color: #333; margin-bottom: 25px;">Visual Content</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px; margin-top: 20px;">
"

        for i, result in enumerate(image_results):
            image_data = result.get('image_data', {})
            prompt = result.get('prompt', f'Newsletter image {i+1}')

            if image_data and 'data' in image_data:
                # Embed base64 image
                image_b64 = image_data['data']
                mime_type = image_data.get('mime_type', 'image/png')

                images_html += """
        <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                 alt="{prompt}"
                 style="max-width: 100%; height: auto; border-radius: 5px;">
            <p style="font-size: 0.9em; color: #666; margin-top: 10px; font-style: italic;">
                {prompt}
            </p>
        </div>
"""
            else:
                # Placeholder for text-based response
                images_html += f"""
        <div style="background: #f5f5f5; padding: 30px; border-radius: 8px;
                    border: 2px dashed #ddd;">
            <p style="color: #666; font-style: italic;">{prompt}</p>
        </div>
"""

        images_html += """
    </div>
</div>
"""

        return images_html

    def _generate_call_to_action(self) -> str:
        """Generate call-to-action section."""
        if self.body_template:
            # Try to extract call-to-action from template
            cta = self.body_template.replace('{{content}}', '')
            if 'call' in cta.lower() or 'action' in cta.lower():
                return cta

        return f"""
<section style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white; padding: 30px; border-radius: 8px; text-align: center; margin: 40px 0;">
    <h3 style="margin-top: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
        Ready to Explore More?
    </h3>
    <p style="font-size: 1.1em; margin: 15px 0;">
        Discover more insights and join the conversation about {topic}
    </p>
    <a href="#" style="background: white; color: #667eea; padding: 12px 30px;
                       text-decoration: none; border-radius: 25px;
                       font-weight: bold; display: inline-block;
                       transition: transform 0.2s;">
        Read More Articles
    </a>
</section>
"""

    def _generate_footer(self) -> str:
        """Generate newsletter footer."""
        if self.footer_template:
            footer = self.footer_template.replace('{{author}}', self.author_name)
            footer = footer.replace('{{date}}', datetime.now().strftime('%B %d, %Y'))
            footer = footer.replace('{{signature}}', self.email_signature)
            return footer
        else:
            return f"""
<footer style="background-color: #2c3e50; color: white; padding: 30px;
              text-align: center; border-radius: 8px; margin-top: 40px;">
    <p style="margin: 0; font-size: 0.95em;">{self.author_name}</p>
    <p style="margin: 5px 0 0 0; font-size: 0.85em; opacity: 0.8;">
        {datetime.now().strftime('%B %d, %Y')} | Generated by AI Newsletter System
    </p>
    <div style="margin-top: 15px; opacity: 0.7;">
        <a href="#" style="color: #3498db; text-decoration: none; margin: 0 10px;">Unsubscribe</a>
        <a href="#" style="color: #3498db; text-decoration: none; margin: 0 10px;">Privacy Policy</a>
    </div>
</footer>
"""

    def _assemble_newsletter(self, header: str, intro: str, body: str,
                            images: str, cta: str, footer: str) -> str:
        """Assemble all newsletter components into complete HTML."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.newsletter_title} - {datetime.now().strftime('%B %d, %Y')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}

        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #1a1a1a;
                color: #e0e0e0;
            }}
            section, header, footer {{
                background-color: #2d2d2d !important;
                color: #e0e0e0 !important;
            }}
        }}

        a {{
            color: #3498db;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }}

        h1, h2, h3 {{
            color: #2c3e50;
        }}

        @media (prefers-color-scheme: dark) {{
            h1, h2, h3 {{
                color: #e0e0e0;
            }}
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        section, header, footer {{
            animation: fadeIn 0.5s ease-out;
        }}
    </style>
</head>
<body>
    {header}
    {intro}
    {body}
    {images}
    {cta}
    {footer}
</body>
</html>
"""

    def save_newsletter(self, newsletter_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Save newsletter to HTML file.

        Args:
            newsletter_data: Newsletter data dictionary
            output_path: Output file path

        Returns:
            Path where file was saved
        """
        if not output_path:
            topic_slug = newsletter_data.get('metadata', {}).get('topic', 'newsletter').replace(' ', '_')
            output_path = f"./tmp/newsletter_{topic_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(newsletter_data['html_content'])

        return output_path

    def get_newsletter_summary(self, newsletter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary information about the newsletter.

        Args:
            newsletter_data: Newsletter data dictionary

        Returns:
            Summary dictionary
        """
        metadata = newsletter_data.get('metadata', {})
        components = newsletter_data.get('components', {})

        return {
            "topic": metadata.get('topic'),
            "author": metadata.get('author'),
            "generated_at": metadata.get('generated_at'),
            "word_count": len(newsletter_data['html_content'].split()),
            "sections_count": len(components),
            "images_used": metadata.get('images_used'),
            "sources_count": metadata.get('research_sources'),
            "estimated_reading_time": max(1, len(newsletter_data['html_content'].split()) // 200)
        }

def main():
    """CLI interface for the content writing tool."""
    if len(sys.argv) < 2:
        print("Usage: python write_content.py <research_file> [output_file] [topic]")
        print("Example: python write_content.py ./tmp/research_ai_trends.json ./output/newsletter.html \"AI Trends\"")
        return

    research_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    topic = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        # Load research data
        with open(research_file, 'r', encoding='utf-8') as f:
            research_result = json.load(f)

        # Load image results if available
        image_results = []
        images_dir = "./tmp"
        for filename in os.listdir(images_dir) if os.path.exists(images_dir) else []:
            if filename.startswith('image_') and filename.endswith('.json'):
                try:
                    with open(os.path.join(images_dir, filename), 'r', encoding='utf-8') as f:
                        image_results.append(json.load(f))
                except Exception as e:
                    print(f"Warning: Could not load image file {filename}: {str(e)}")

        # Generate newsletter
        tool = WriteContentTool()
        newsletter = tool.generate_newsletter(research_result, image_results, topic)

        # Save newsletter
        output_path = tool.save_newsletter(newsletter, output_file)
        print(f"Newsletter generated and saved to: {output_path}")

        # Print summary
        summary = tool.get_newsletter_summary(newsletter)
        print("\n=== Newsletter Summary ===")
        for key, value in summary.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    exit(main())