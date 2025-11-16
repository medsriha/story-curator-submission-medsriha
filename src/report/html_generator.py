import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import Counter
from jinja2 import Environment, FileSystemLoader, select_autoescape


class HTMLReportGenerator:
    """Generates interactive HTML reports for story content review."""

    # Category colors for display
    CATEGORY_COLORS = {
        'Decoding': '#3498db',
        'Comprehension': '#27ae60',
        'Vocabulary': '#e74c3c',
        'Knowledge': '#f39c12',
        'Fluency': '#9b59b6'
    }

    # Category mapping for skill IDs
    CATEGORY_MAP = {
        'DEC': 'Decoding',
        'COMP': 'Comprehension',
        'VOCAB': 'Vocabulary',
        'KNOW': 'Knowledge',
        'FLUENCY': 'Fluency'
    }

    def __init__(self,
                 flagging_json_path: str = "output/machine_readable/story_flagging.json",
                 tagging_json_path: str = "output/machine_readable/skill_tagging.json",
                 template_dir: str = "templates"):
        """
        Initialize the HTML report generator.

        Args:
            flagging_json_path: Path to story flagging JSON file (single story or array)
            tagging_json_path: Path to skill tagging JSON file (single story or array)
            template_dir: Directory containing Jinja2 templates
        """
        self.flagging_json_path = Path(flagging_json_path)
        self.tagging_json_path = Path(tagging_json_path)
        self.template_dir = Path(template_dir)

        self.flagging_data = []
        self.tagging_data = []

        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # Add custom filters
        self.jinja_env.filters['extract_category'] = self._extract_category_from_skill_id
        self.jinja_env.filters['confidence_level'] = self._get_confidence_level

    def load_data(self) -> bool:
        """
        Load all required data from JSON files.
        Supports both single story objects and arrays of stories.

        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            # Load flagging data
            if self.flagging_json_path.exists():
                with open(self.flagging_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Normalize to array
                    if isinstance(data, list):
                        self.flagging_data = data
                    else:
                        self.flagging_data = [data]
            else:
                print(f"Warning: Flagging file not found at {self.flagging_json_path}")
                self.flagging_data = []

            # Load tagging data
            if self.tagging_json_path.exists():
                with open(self.tagging_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Normalize to array
                    if isinstance(data, list):
                        self.tagging_data = data
                    else:
                        self.tagging_data = [data]
            else:
                print(f"Warning: Tagging file not found at {self.tagging_json_path}")
                self.tagging_data = []

            return True

        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def generate_html(self) -> str:
        """
        Generate complete self-contained HTML page.

        Returns:
            Complete HTML string with embedded CSS and JavaScript
        """
        stories = self._merge_story_data()

        context = self._prepare_context(stories)

        css_content = self._load_template_file('styles.css')
        js_content = self._load_template_file('scripts.js')

        template = self.jinja_env.get_template('review_report.html')
        html = template.render(**context)

        html = html.replace('<link rel="stylesheet" href="styles.css">', f'<style>\n{css_content}\n    </style>')
        html = html.replace('<script src="scripts.js"></script>', f'<script>\n{js_content}\n    </script>')

        return html

    def _merge_story_data(self) -> List[Dict[str, Any]]:
        """
        Merge flagging and tagging data by story_id.

        Returns:
            List of stories with both flagging and tagging data
        """
        flagging_by_id = {s.get('story_id'): s for s in self.flagging_data}
        tagging_by_id = {s.get('story_id'): s for s in self.tagging_data}

        all_story_ids = set(flagging_by_id.keys()) | set(tagging_by_id.keys())

        stories = []
        for story_id in all_story_ids:
            flagging = flagging_by_id.get(story_id)
            tagging = tagging_by_id.get(story_id)

            base_data = flagging or tagging or {}

            story = {
                'story_id': story_id,
                'story_title': base_data.get('story_title', 'Unknown'),
                'grade_level': base_data.get('grade_level', 'N/A'),
                'flagging': flagging,
                'tagging': tagging
            }

            if flagging:
                story['flag_count'] = flagging.get('flag_count', len(flagging.get('flags', [])))
                story['has_critical'] = flagging.get('has_critical', False)
            else:
                story['flag_count'] = 0
                story['has_critical'] = False

            if tagging:
                tags = tagging.get('tags', [])
                story['skill_count'] = len(tags)
                story['category_counts'] = self._calculate_category_counts(tags)
            else:
                story['skill_count'] = 0
                story['category_counts'] = {cat: 0 for cat in self.CATEGORY_MAP.values()}

            stories.append(story)

        # Sort by story title
        stories.sort(key=lambda s: s.get('story_title', ''))

        return stories

    def _load_template_file(self, filename: str) -> str:
        """Load a template file as a string."""
        file_path = self.template_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def _prepare_context(self, stories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepare template context with all necessary data.

        Args:
            stories: List of merged story data

        Returns:
            Dictionary with template variables
        """
        context = {
            'stories': stories,
            'category_colors': self.CATEGORY_COLORS,
            'total_stories': len(stories),
            'total_flags': sum(s.get('flag_count', 0) for s in stories),
            'total_skills': sum(s.get('skill_count', 0) for s in stories),
            'has_any_critical': any(s.get('has_critical', False) for s in stories)
        }

        return context

    def _calculate_category_counts(self, tags: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calculate how many times each category appears in tags.

        Args:
            tags: List of skill tags

        Returns:
            Dictionary mapping category name to count
        """
        categories = [
            self._extract_category_from_skill_id(tag.get('skill_id', ''))
            for tag in tags
        ]

        counts = Counter(categories)

        result = {cat: 0 for cat in self.CATEGORY_MAP.values()}
        result.update(counts)

        return result

    def _extract_category_from_skill_id(self, skill_id: str) -> str:
        """
        Extract category name from skill ID.

        Args:
            skill_id: Skill identifier (e.g., "SKILL-COMP-003")

        Returns:
            Category name (e.g., "Comprehension")
        """
        parts = skill_id.split('-')
        if len(parts) >= 2:
            cat_code = parts[1]
            return self.CATEGORY_MAP.get(cat_code, 'Unknown')
        return 'Unknown'

    def _get_confidence_level(self, confidence: float) -> str:
        """
        Convert confidence score to level.

        Args:
            confidence: Confidence score (0.0 - 1.0)

        Returns:
            Level string: "high", "medium", or "low"
        """
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        else:
            return "low"

    def save_html(self, output_path: str = "output/human_review/review_report.html") -> bool:
        """
        Save generated HTML to file.

        Args:
            output_path: Path where HTML file should be saved

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            html_content = self.generate_html()

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"HTML report saved to: {output_file}")
            return True

        except Exception as e:
            print(f"Error saving HTML: {e}")
            return False


def main() -> None:
    """Main function to generate HTML report."""
    generator = HTMLReportGenerator()

    if not generator.load_data():
        print("Failed to load data")
        return

    if generator.save_html():
        print("HTML report generated successfully!")
    else:
        print("Failed to generate HTML report")


if __name__ == "__main__":
    main()
