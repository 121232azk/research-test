#!/usr/bin/env python3
"""
Create a slide deck from trading news analysis.

This tool generates a PowerPoint or Google Slides presentation from the analysis
results, including charts and visualizations.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

class SlideDeckError(Exception):
    """Custom exception for slide deck generation errors."""
    pass

class SlideDeckGenerator:
    def __init__(self):
        # Load configuration
        self.output_dir = os.getenv('SLIDE_DECK_OUTPUT_DIR', './tmp')
        self.template_path = os.getenv('SLIDE_DECK_TEMPLATE', None)
        self.title = os.getenv('SLIDE_DECK_TITLE', 'Trading News Analysis')
        self.author = os.getenv('SLIDE_DECK_AUTHOR', 'AI Insights Team')

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def create_slide_deck(self, analysis_data: Dict[str, Any], visualizations: List[Dict[str, Any]],
                            output_path: Optional[str] = None) -> str:
        """
        Create a slide deck from analysis data and visualizations.

        Args:
            analysis_data: Dictionary containing analysis results
            visualizations: List of visualization data
            output_path: Optional output path for the slide deck

        Returns:
            Path to the generated slide deck
        """
        try:
            # Create presentation
            if self.template_path and os.path.exists(self.template_path):
                prs = Presentation(self.template_path)
            else:
                prs = Presentation()
                # Set default layout
                slide_layout = prs.slide_layouts[1]  # Title and Content layout

            # Add title slide
            self._add_title_slide(prs)

            # Add analysis slides
            for category, data in analysis_data.items():
                self._add_analysis_slide(prs, category, data)

            # Add visualization slides
            for viz in visualizations:
                self._add_visualization_slide(prs, viz)

            # Add conclusion slide
            self._add_conclusion_slide(prs)

            # Save presentation
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = os.path.join(self.output_dir, f'slide_deck_{timestamp}.pptx')

            prs.save(output_path)

            return output_path

        except Exception as e:
            raise SlideDeckError(f"Failed to create slide deck: {str(e)}")

    def _add_title_slide(self, prs: Presentation):
        """Add title slide to the presentation."""
        slide = prs.slides.add_slide(prs.slide_layouts[0])  # Title slide layout
        title = slide.shapes.title
        subtitle = slide.placeholders[1]

        title.text = self.title
        subtitle.text = f"{datetime.now().strftime('%B %d, %Y')}\n{self.author}"

        # Format title
        title.text_frame.paragraphs[0].font.size = Pt(44)
        title.text_frame.paragraphs[0].font.bold = True
        title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)

        # Format subtitle
        subtitle.text_frame.paragraphs[0].font.size = Pt(28)
        subtitle.text_frame.paragraphs[0].font.color.rgb = RGBColor(102, 102, 102)

    def _add_analysis_slide(self, prs: Presentation, category: str, data: Dict[str, Any]):
        """Add analysis slide for a specific category."""
        slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title and Content layout
        title = slide.shapes.title
        content = slide.placeholders[1]

        title.text = f"{category.capitalize()} Analysis"

        # Add bullet points for key findings
        tf = content.text_frame
        tf.text = "Key Findings:"

        for finding in data.get('key_findings', []):
            p = tf.add_paragraph()
            p.text = f"• {finding}"
            p.level = 1

        # Add summary
        if 'summary' in data:
            p = tf.add_paragraph()
            p.text = f"\nSummary: {data['summary']}"
            p.font.bold = True

    def _add_visualization_slide(self, prs: Presentation, viz: Dict[str, Any]):
        """Add visualization slide with chart or image."""
        slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title only layout
        title = slide.shapes.title

        title.text = viz.get('title', 'Visualization')

        # Add image if available
        if 'image_path' in viz and os.path.exists(viz['image_path']):
            left = Inches(1)
            top = Inches(1.5)
            height = Inches(5)
            slide.shapes.add_picture(viz['image_path'], left, top, height=height)

        # Add description
        if 'description' in viz:
            txBox = slide.shapes.add_textbox(Inches(1), Inches(7), Inches(8), Inches(1))
            tf = txBox.text_frame
            tf.text = viz['description']

            # Format text
            p = tf.paragraphs[0]
            p.font.size = Pt(18)
            p.font.color.rgb = RGBColor(75, 75, 75)
            p.alignment = PP_ALIGN.CENTER

    def _add_conclusion_slide(self, prs: Presentation):
        """Add conclusion slide to the presentation."""
        slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title and Content layout
        title = slide.shapes.title
        content = slide.placeholders[1]

        title.text = "Conclusion"

        tf = content.text_frame
        tf.text = "Key Takeaways:"

        # Add conclusion points
        conclusions = [
            "Forex market trends indicate...",
            "Stock market shows signs of...",
            "Crypto market is experiencing...",
            "Meme coins are showing strong momentum in...",
            "Prop firms are offering attractive bonuses in..."
        ]

        for point in conclusions:
            p = tf.add_paragraph()
            p.text = f"• {point}"
            p.level = 1

        # Add closing
        p = tf.add_paragraph()
        p.text = "\nPrepared by AI Insights Team"
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(102, 102, 102)
        p.alignment = PP_ALIGN.CENTER

    def save_slide_deck(self, slide_deck_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Save slide deck to a file.

        Args:
            slide_deck_data: Slide deck data dictionary
            output_path: Output file path

        Returns:
            Path where file was saved
        """
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.output_dir, f'slide_deck_{timestamp}.json')

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(slide_deck_data, f, indent=2, ensure_ascii=False)

        return output_path

    def get_slide_deck_summary(self, slide_deck_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary information about the slide deck.

        Args:
            slide_deck_data: Slide deck data dictionary

        Returns:
            Summary dictionary
        """
        return {
            "title": slide_deck_data.get('title', self.title),
            "author": slide_deck_data.get('author', self.author),
            "generated_at": slide_deck_data.get('generated_at', datetime.now().isoformat()),
            "slide_count": len(slide_deck_data.get('slides', [])),
            "categories_covered": len(slide_deck_data.get('categories', [])),
            "visualizations_included": len(slide_deck_data.get('visualizations', []))
        }

def main():
    """CLI interface for the slide deck tool."""
    if len(sys.argv) < 2:
        print("Usage: python create_slide_deck.py <analysis_file> <visualizations_file> [output_file]")
        print("Example: python create_slide_deck.py analysis.json visualizations.json slide_deck.pptx")
        return

    analysis_file = sys.argv[1]
    visualizations_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        # Load analysis data
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)

        # Load visualizations data
        with open(visualizations_file, 'r', encoding='utf-8') as f:
            visualizations_data = json.load(f)

        # Create slide deck
        generator = SlideDeckGenerator()
        slide_deck_path = generator.create_slide_deck(analysis_data, visualizations_data, output_file)

        print(f"Slide deck created successfully: {slide_deck_path}")

        # Print summary
        summary = generator.get_slide_deck_summary({
            'title': generator.title,
            'author': generator.author,
            'generated_at': datetime.now().isoformat(),
            'slides': [],
            'categories': list(analysis_data.keys()),
            'visualizations': visualizations_data
        })

        print("\n=== Slide Deck Summary ===")
        for key, value in summary.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    exit(main())