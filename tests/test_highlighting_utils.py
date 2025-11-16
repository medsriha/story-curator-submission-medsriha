import pytest
from src.utils.highlighting_utils import HighlightingHelper


class TestHighlightingHelper:
    @pytest.mark.parametrize("skill_id,expected", [
        ("SKILL-DEC-001", "Decoding"),
        ("SKILL-COMP-005", "Comprehension"),
        ("SKILL-VOCAB-003", "Vocabulary"),
        ("SKILL-KNOW-002", "Knowledge"),
        ("SKILL-FLUENCY-001", "Fluency"),
        ("INVALID", "Unknown"),
        ("", "Unknown"),
    ])
    def test_extract_category(self, skill_id, expected):
        result = HighlightingHelper.extract_category_from_skill_id(skill_id)
        assert result == expected

    @pytest.mark.parametrize("confidence,expected", [
        (0.0, "low"),
        (0.59, "low"),
        (0.6, "medium"),
        (0.79, "medium"),
        (0.8, "high"),
        (1.0, "high"),
    ])
    def test_confidence_level(self, confidence, expected):
        assert HighlightingHelper.get_confidence_level(confidence) == expected

    def test_compare_severity(self):
        assert HighlightingHelper.compare_severity("Critical", "High") is True
        assert HighlightingHelper.compare_severity("High", "Medium") is True
        assert HighlightingHelper.compare_severity("Medium", "Low") is True
        assert HighlightingHelper.compare_severity("Low", "High") is False
        assert HighlightingHelper.compare_severity("High", "High") is False

    def test_generate_flag_html(self):
        sentence_mapping = [(1, "Test sentence.")]
        sentence_flags = {
            1: [{
                "severity": "Medium",
                "css_class": "flag-medium",
                "color": "#ffa726",
                "issue_type": "Test"
            }]
        }
        html = HighlightingHelper.generate_flag_html_simple(sentence_mapping, sentence_flags)
        assert "Test sentence." in html
        assert "#ffa726" in html
        assert "flag-medium" in html

    def test_generate_flag_html_multiple_flags(self):
        sentence_mapping = [(1, "Test.")]
        sentence_flags = {
            1: [
                {"severity": "High", "css_class": "flag-high", "color": "#ff6b6b", "issue_type": "A"},
                {"severity": "Medium", "css_class": "flag-medium", "color": "#ffa726", "issue_type": "B"}
            ]
        }
        html = HighlightingHelper.generate_flag_html_simple(sentence_mapping, sentence_flags)
        assert "#9e9e9e" in html
        assert "flag-multiple" in html

    def test_generate_skill_html(self):
        sentence_mapping = [(1, "Test.")]
        skill_tags = [{
            "skill_id": "SKILL-COMP-001",
            "skill_name": "Main Idea",
            "confidence": 0.9,
            "tag_numbers": [1]
        }]
        html = HighlightingHelper.generate_skill_html_simple(sentence_mapping, skill_tags)
        assert "Test." in html
        assert "#27ae60" in html
        assert "skill-comprehension" in html
