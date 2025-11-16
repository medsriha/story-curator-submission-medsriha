from typing import Dict, List, Any, Tuple


class HighlightingHelper:
    """
    Helper class for generating highlighting metadata and HTML.
    """

    # Color schemes for different highlighting types
    SEVERITY_COLORS = {
        "Critical": "#d32f2f",   # Dark red
        "High": "#ff6b6b",       # Light red
        "Medium": "#ffa726",     # Orange
        "Low": "#fff59d"         # Light yellow
    }

    CONFIDENCE_COLORS = {
        "high": "#4caf50",
        "medium": "#ff9800",
        "low": "#f44336"
    }

    # Category colors for skill highlighting
    CATEGORY_HIGHLIGHT_COLORS = {
        "Decoding": "#3498db",      # Blue
        "Comprehension": "#27ae60",  # Green
        "Vocabulary": "#e74c3c",     # Red
        "Knowledge": "#f39c12",      # Orange
        "Fluency": "#9b59b6",        # Purple
        "Unknown": "#95a5a6"         # Gray
    }

    SEVERITY_CSS_CLASSES = {
        "Critical": "flag-critical",
        "High": "flag-high",
        "Medium": "flag-medium",
        "Low": "flag-low"
    }

    CONFIDENCE_CSS_CLASSES = {
        "high": "skill-high-confidence",
        "medium": "skill-medium-confidence",
        "low": "skill-low-confidence"
    }

    CATEGORY_CSS_CLASSES = {
        "Decoding": "skill-decoding",
        "Comprehension": "skill-comprehension",
        "Vocabulary": "skill-vocabulary",
        "Knowledge": "skill-knowledge",
        "Fluency": "skill-fluency",
        "Unknown": "skill-unknown"
    }

    CATEGORY_MAP = {
        "DEC": "Decoding",
        "COMP": "Comprehension",
        "VOCAB": "Vocabulary",
        "KNOW": "Knowledge",
        "FLUENCY": "Fluency"
    }

    @staticmethod
    def extract_category_from_skill_id(skill_id: str) -> str:
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
            return HighlightingHelper.CATEGORY_MAP.get(cat_code, "Unknown")
        return "Unknown"

    @staticmethod
    def get_confidence_level(confidence: float) -> str:
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

    @staticmethod
    def compare_severity(sev1: str, sev2: str) -> bool:
        """
        Check if sev1 is higher severity than sev2.

        Args:
            sev1: First severity level
            sev2: Second severity level

        Returns:
            True if sev1 > sev2
        """
        severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        return severity_order.get(sev1, 0) > severity_order.get(sev2, 0)

    @staticmethod
    def generate_flag_html_simple(
        sentence_mapping: List[Tuple[int, str]],
        sentence_flags: Dict[int, List[Dict[str, Any]]]
    ) -> str:
        """
        Generate simplified HTML with flagged sentences highlighted.
        Uses gray color when a sentence has multiple flags.

        Args:
            sentence_mapping: List of (tag_number, text) tuples
            sentence_flags: Dictionary mapping tag_num to list of flag info dicts

        Returns:
            HTML string with flagged sentences wrapped in colored spans
        """
        html_parts = []
        for tag_num, text in sentence_mapping:
            if tag_num in sentence_flags:
                flags_list = sentence_flags[tag_num]

                if len(flags_list) > 1:
                    # Multiple flags - use gray
                    color = "#9e9e9e"
                    css_class = "flag-multiple"

                    issues = [f"{f['severity']}: {f['issue_type']}" for f in flags_list]
                    title = "Multiple issues - " + "; ".join(issues)
                else:
                    flag_info = flags_list[0]
                    color = flag_info["color"]
                    css_class = flag_info["css_class"]
                    severity = flag_info["severity"]
                    issue = flag_info["issue_type"]
                    title = f"{severity}: {issue}"

                html_parts.append(
                    f'<span class="{css_class}" '
                    f'style="background-color: {color}; padding: 2px 4px; border-radius: 3px;" '
                    f'title="{title}">{text}</span>'
                )
            else:
                html_parts.append(text)

        return " ".join(html_parts)

    @staticmethod
    def generate_skill_html_simple(
        sentence_mapping: List[Tuple[int, str]],
        skill_tags: List[Dict[str, Any]]
    ) -> str:
        """
        Generate simplified HTML with skill-tagged sentences highlighted.
        Uses category-based color coding for single skills.
        Uses gray color when a sentence has multiple skills.

        Args:
            sentence_mapping: List of (tag_number, text) tuples
            skill_tags: List of skill tags with tag_numbers, skill_id, and confidence

        Returns:
            HTML string with skill-tagged sentences wrapped in colored spans
        """
        tag_skills = {}
        for skill_tag in skill_tags:
            skill_id = skill_tag.get("skill_id", "")
            skill_name = skill_tag.get("skill_name", "")
            confidence = skill_tag.get("confidence", 0.0)
            tag_numbers = skill_tag.get("tag_numbers", [])

            category = HighlightingHelper.extract_category_from_skill_id(skill_id)

            for tag_num in tag_numbers:
                if tag_num not in tag_skills:
                    tag_skills[tag_num] = []
                tag_skills[tag_num].append({
                    "category": category,
                    "confidence": confidence,
                    "skill_name": skill_name,
                    "skill_id": skill_id
                })

        html_parts = []
        for tag_num, text in sentence_mapping:
            if tag_num in tag_skills:
                skills_list = tag_skills[tag_num]

                if len(skills_list) > 1:
                    # Multiple skills - use gray
                    color = "#9e9e9e"
                    css_class = "skill-multiple"

                    skill_labels = [f"{s['category']}: {s['skill_name']}" for s in skills_list]
                    title = "Multiple skills - " + "; ".join(skill_labels)
                else:
                    # Single skill - use category color
                    skill = skills_list[0]
                    category = skill["category"]
                    confidence = skill["confidence"]
                    skill_name = skill["skill_name"]

                    color = HighlightingHelper.CATEGORY_HIGHLIGHT_COLORS.get(category, "#95a5a6")
                    css_class = HighlightingHelper.CATEGORY_CSS_CLASSES.get(category, "skill-unknown")
                    title = f"{category}: {skill_name} (confidence: {confidence:.2f})"

                html_parts.append(
                    f'<span class="{css_class}" '
                    f'style="background-color: {color}; padding: 2px 4px; border-radius: 3px;" '
                    f'title="{title}">{text}</span>'
                )
            else:
                html_parts.append(text)

        return " ".join(html_parts)