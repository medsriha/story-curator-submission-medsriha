import pytest
from unittest.mock import Mock, MagicMock, patch
from src.flagging.content_flagger import ContentFlagger


class TestContentFlagger:
    def test_group_consecutive_flags(self):
        flagger = ContentFlagger(Mock(), Mock())
        flags_raw = [{
            "issue_type": "Violence",
            "severity_level": "Medium",
            "confidence": 0.8,
            "rationale": "Test",
            "tag_numbers": [1, 2, 3, 5, 6, 10]
        }]
        tagged_content = " ".join([f"<tag{i}>S{i}.</tag{i}>" for i in range(1, 11)])

        result = flagger._group_consecutive_flags(flags_raw, tagged_content)

        assert len(result) == 3
        assert result[0]["tag_numbers"] == [1, 2, 3]
        assert result[1]["tag_numbers"] == [5, 6]
        assert result[2]["tag_numbers"] == [10]

    def test_group_preserves_properties(self):
        flagger = ContentFlagger(Mock(), Mock())
        flags_raw = [{
            "issue_type": "Safety",
            "severity_level": "Critical",
            "confidence": 0.95,
            "rationale": "Test rationale",
            "tag_numbers": [1, 2]
        }]
        tagged_content = "<tag1>S1.</tag1> <tag2>S2.</tag2>"

        result = flagger._group_consecutive_flags(flags_raw, tagged_content)

        assert result[0]["issue_type"] == "Safety"
        assert result[0]["severity_level"] == "Critical"
        assert result[0]["confidence"] == 0.95
        assert "S1. S2." in result[0]["text_evidence"]

    @patch('src.flagging.content_flagger.ContentFlagger._check_category')
    def test_flag_story_structure(self, mock_check):
        mock_data_loader = Mock()
        mock_data_loader.get_story_with_tagged_sentences.return_value = {
            "story_id": "test_001",
            "story_title": "Test",
            "grade_level": 2,
            "tagged_content": "<tag1>Test.</tag1>"
        }
        mock_check.return_value = [{
            "issue_type": "Violence",
            "severity_level": "Medium",
            "confidence": 0.85,
            "rationale": "Test",
            "tag_numbers": [1]
        }]

        flagger = ContentFlagger(mock_data_loader, Mock())
        result = flagger.flag_story("test_001", max_workers=1)

        assert "story_id" in result
        assert "flags" in result
        assert "has_critical" in result
        assert len(result["flags"]) > 0
        assert result["flags"][0]["confidence"] == 0.85

    @patch('src.flagging.content_flagger.ContentFlagger._check_category')
    def test_confidence_defaults(self, mock_check):
        mock_data_loader = Mock()
        mock_data_loader.get_story_with_tagged_sentences.return_value = {
            "story_id": "test_001",
            "story_title": "Test",
            "grade_level": 2,
            "tagged_content": "<tag1>Test.</tag1>"
        }
        mock_check.return_value = [{
            "issue_type": "Test",
            "severity_level": "Low",
            "rationale": "Test",
            "tag_numbers": [1]
        }]

        flagger = ContentFlagger(mock_data_loader, Mock())
        result = flagger.flag_story("test_001", max_workers=1)

        assert result["flags"][0]["confidence"] == 0.5

    @patch('src.flagging.content_flagger.ContentFlagger._check_category')
    def test_critical_flag_detection(self, mock_check):
        mock_data_loader = Mock()
        mock_data_loader.get_story_with_tagged_sentences.return_value = {
            "story_id": "test_001",
            "story_title": "Test",
            "grade_level": 2,
            "tagged_content": "<tag1>Test.</tag1>"
        }
        mock_check.return_value = [{
            "issue_type": "Safety",
            "severity_level": "Critical",
            "confidence": 0.95,
            "rationale": "Test",
            "tag_numbers": [1]
        }]

        flagger = ContentFlagger(mock_data_loader, Mock())
        result = flagger.flag_story("test_001", max_workers=1)

        assert result["has_critical"] is True

    @patch('src.flagging.content_flagger.ContentFlagger._check_category')
    def test_flags_sorted_by_appearance(self, mock_check):
        mock_data_loader = Mock()
        mock_data_loader.get_story_with_tagged_sentences.return_value = {
            "story_id": "test_001",
            "story_title": "Test",
            "grade_level": 2,
            "tagged_content": "<tag1>S1.</tag1> <tag5>S5.</tag5> <tag3>S3.</tag3>"
        }

        def side_effect(*args, **kwargs):
            cat = kwargs.get('category')
            if cat == 'violence_harm':
                return [{"issue_type": "Violence", "severity_level": "High", "confidence": 0.9, "rationale": "Test", "tag_numbers": [5]}]
            elif cat == 'critical_safety':
                return [{"issue_type": "Safety", "severity_level": "Critical", "confidence": 0.95, "rationale": "Test", "tag_numbers": [1]}]
            elif cat == 'age_appropriateness':
                return [{"issue_type": "Age", "severity_level": "Medium", "confidence": 0.8, "rationale": "Test", "tag_numbers": [3]}]
            return []

        mock_check.side_effect = side_effect

        flagger = ContentFlagger(mock_data_loader, Mock())
        result = flagger.flag_story("test_001")

        assert len(result["flags"]) == 3
        assert result["flags"][0]["issue_type"] == "Safety"
        assert result["flags"][1]["issue_type"] == "Age"
        assert result["flags"][2]["issue_type"] == "Violence"
