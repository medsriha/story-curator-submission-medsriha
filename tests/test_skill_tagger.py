import pytest
from unittest.mock import Mock, MagicMock, patch
from src.tagging.skill_tagger import SkillTagger


class TestSkillTagger:
    def test_group_consecutive_tags(self):
        tagger = SkillTagger(Mock(), Mock())
        skill_tags_raw = [{
            "skill_id": "SKILL-COMP-001",
            "skill_name": "Main Idea",
            "confidence": 0.9,
            "rationale": "Test",
            "tag_numbers": [1, 2, 3, 5, 6, 10]
        }]
        tagged_content = " ".join([f"<tag{i}>S{i}.</tag{i}>" for i in range(1, 11)])

        result = tagger._group_consecutive_tags(skill_tags_raw, tagged_content)

        assert len(result) == 3
        assert result[0]["tag_numbers"] == [1, 2, 3]
        assert result[1]["tag_numbers"] == [5, 6]
        assert result[2]["tag_numbers"] == [10]

    def test_group_preserves_properties(self):
        tagger = SkillTagger(Mock(), Mock())
        skill_tags_raw = [{
            "skill_id": "SKILL-VOCAB-003",
            "skill_name": "Word Meaning",
            "confidence": 0.85,
            "rationale": "Test rationale",
            "tag_numbers": [1, 2]
        }]
        tagged_content = "<tag1>S1.</tag1> <tag2>S2.</tag2>"

        result = tagger._group_consecutive_tags(skill_tags_raw, tagged_content)

        assert result[0]["skill_id"] == "SKILL-VOCAB-003"
        assert result[0]["confidence"] == 0.85
        assert "S1. S2." in result[0]["sentence_evidence"]

    @patch('src.tagging.skill_tagger.SkillTagger._identify_skills')
    def test_tag_story_structure(self, mock_identify):
        mock_data_loader = Mock()
        mock_data_loader.get_story_with_tagged_sentences.return_value = {
            "story_id": "test_001",
            "story_title": "Test",
            "grade_level": 2,
            "tagged_content": "<tag1>Test.</tag1>"
        }
        mock_identify.return_value = [{
            "skill_id": "SKILL-COMP-001",
            "skill_name": "Main Idea",
            "confidence": 0.9,
            "rationale": "Test",
            "tag_numbers": [1]
        }]

        tagger = SkillTagger(mock_data_loader, Mock())
        result = tagger.tag_story("test_001")

        assert "story_id" in result
        assert "tags" in result
        assert "highlighted_text" in result
        assert len(result["tags"]) > 0

    @patch('src.tagging.skill_tagger.SkillTagger._identify_skills')
    def test_tags_sorted_by_appearance(self, mock_identify):
        mock_data_loader = Mock()
        mock_data_loader.get_story_with_tagged_sentences.return_value = {
            "story_id": "test_001",
            "story_title": "Test",
            "grade_level": 2,
            "tagged_content": "<tag1>S1.</tag1> <tag5>S5.</tag5> <tag3>S3.</tag3>"
        }
        mock_identify.return_value = [
            {"skill_id": "SKILL-COMP-003", "skill_name": "C", "confidence": 0.8, "rationale": "Test", "tag_numbers": [5]},
            {"skill_id": "SKILL-COMP-001", "skill_name": "A", "confidence": 0.9, "rationale": "Test", "tag_numbers": [1]},
            {"skill_id": "SKILL-COMP-002", "skill_name": "B", "confidence": 0.85, "rationale": "Test", "tag_numbers": [3]}
        ]

        tagger = SkillTagger(mock_data_loader, Mock())
        result = tagger.tag_story("test_001")

        assert result["tags"][0]["skill_name"] == "A"
        assert result["tags"][1]["skill_name"] == "B"
        assert result["tags"][2]["skill_name"] == "C"
