import pytest
from pathlib import Path
from src.utils.data_loader import DataLoader


class TestDataLoader:
    def test_init(self):
        loader = DataLoader()
        assert loader.data_dir == Path("data")
        assert loader.stories is not None
        assert loader.skills is not None
        assert loader.rubric is not None

    def test_stories_loaded(self):
        loader = DataLoader()
        assert len(loader.stories) > 0
        assert 'story_id' in loader.stories.columns
        assert 'grade_level' in loader.stories.columns
        assert loader.stories['grade_level'].dtype in ['int64', 'int32']

    def test_skills_loaded(self):
        loader = DataLoader()
        assert len(loader.skills) == 50
        required = ['skill_id', 'skill_name', 'skill_description']
        for col in required:
            assert col in loader.skills.columns

    def test_rubric_loaded(self):
        loader = DataLoader()
        expected = ["critical_safety", "violence_harm", "age_appropriateness",
                    "cultural_sensitivity", "emotional_safety", "technical_issues", "physical_safety"]
        for category in expected:
            assert category in loader.rubric
            assert len(loader.rubric[category]) > 0

    def test_get_story_by_id(self):
        loader = DataLoader()
        story_id = loader.stories['story_id'].iloc[0]
        story = loader.get_story_by_id(story_id)
        assert story['story_id'] == story_id
        assert 'story_title' in story

    def test_get_nonexistent_story(self):
        loader = DataLoader()
        with pytest.raises(ValueError):
            loader.get_story_by_id("fake_id")

    def test_get_stories_by_grade(self):
        loader = DataLoader()
        grade_0 = loader.get_stories_by_grade(0)
        assert all(grade_0['grade_level'] == 0)

    def test_get_invalid_rubric_category(self):
        loader = DataLoader()
        with pytest.raises(KeyError):
            loader.get_rubric_category("invalid")

    def test_get_story_with_tagged_sentences(self):
        loader = DataLoader()
        story_id = loader.stories['story_id'].iloc[0]
        story = loader.get_story_with_tagged_sentences(story_id)
        assert 'tagged_content' in story
        assert '<tag' in story['tagged_content']
