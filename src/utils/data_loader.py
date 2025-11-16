import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from .text_processor import TextProcessor


class DataLoader:
    """Loads and provides access to project data files."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.stories = self.load_stories()
        self.skills = self.load_skills()
        self.rubric = self.load_rubric()

    def load_stories(self) -> pd.DataFrame:
        """Load stories dataset from CSV.

        Returns:
            DataFrame with columns: story_id, story_title, story_content, grade_level
        """
        stories_path = self.data_dir / "stories.csv"
        self.stories = pd.read_csv(stories_path)
        # Grade level are integers from 0 -> 8
        self.stories['grade_level'] = self.stories['grade_level'].astype(int)
        return self.stories

    def load_skills(self) -> pd.DataFrame:
        """Load skills taxonomy from CSV.

        Returns:
            DataFrame with columns: skill_id, skill_name, skill_category, skill_description
        """
        skills_path = self.data_dir / "skills.csv"
        self.skills = pd.read_csv(skills_path)
        return self.skills

    def load_rubric(self) -> Dict[str, str]:
        """Load content review rubrics from modular markdown files.

        Returns:
            Dictionary mapping rubric category names to their content.
            Categories: critical_safety, violence_harm, etc.
        """
        rubrics_dir = self.data_dir / "rubrics"
        rubric_dict = {}

        rubric_categories = [
            "critical_safety",
            "violence_harm",
            "age_appropriateness",
            "cultural_sensitivity",
            "emotional_safety",
            "technical_issues",
            "physical_safety"
        ]

        for category in rubric_categories:
            rubric_path = rubrics_dir / f"{category}.md"
            if rubric_path.exists():
                with open(rubric_path, 'r', encoding='utf-8') as f:
                    rubric_dict[category] = f.read()
            else:
                print(f"Warning: Rubric file not found: {rubric_path}")

        self.rubric = rubric_dict
        return self.rubric

    def get_rubric_category(self, category: str) -> str:
        """Get a specific rubric category.

        Args:
            category: Rubric category name
        Returns:
            String containing the rubric content for that category

        Raises:
            KeyError: If the category doesn't exist
        """
        if category not in self.rubric:
            available = ', '.join(self.rubric.keys())
            raise KeyError(f"Rubric category '{category}' not found. Available: {available}")
        return self.rubric[category]

    def get_rubric_categories(self) -> List[str]:
        """Get list of all available rubric categories.

        Returns:
            List of rubric category names
        """
        return list(self.rubric.keys())

    def get_story_by_id(self, story_id: str) -> Dict[str, Any]:
        """Get a specific story by ID.

        Args:
            story_id: The story identifier

        Returns:
            Dictionary containing story data
        """
        story_row = self.stories[self.stories['story_id'] == story_id]

        if story_row.empty:
            raise ValueError(f"Story with ID {story_id} not found")

        return story_row.iloc[0].to_dict()

    def get_stories_by_grade(self, grade_level: int) -> pd.DataFrame:
        """Filter stories by grade level.

        Args:
            grade_level: Target grade level (e.g., '0', '1', '2', etc.)

        Returns:
            DataFrame of stories at the specified grade level
        """
        return self.stories[self.stories['grade_level'] == grade_level]

    def get_story_with_tagged_sentences(self, story_id: str) -> Dict[str, Any]:
        """Get a story with sentence-tagged content.

        Args:
            story_id: The story identifier

        Returns:
            Dictionary with story data including 'tagged_content' field
        """
        story = self.get_story_by_id(story_id)
        story['tagged_content'] = TextProcessor.tag_sentences(story['story_content'])
        return story
