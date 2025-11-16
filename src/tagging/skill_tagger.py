import json
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ..utils.data_loader import DataLoader
from ..utils.llm_client import LLMClient
from ..utils.text_processor import TextProcessor
from ..utils.highlighting_utils import HighlightingHelper
from .prompts import build_skill_tagging_prompt, get_system_prompt


class SkillTagger:
    """Tags stories with applicable reading skills using LLM."""

    def __init__(self, data_loader: DataLoader, llm_client: LLMClient):
        """
        Initialize skill tagger.

        Args:
            data_loader: DataLoader instance with skills taxonomy and stories
            llm_client: LLMClient instance for API calls
        """
        self.data_loader = data_loader
        self.llm_client = llm_client

    def _group_consecutive_tags(
        self,
        skill_tags_raw: List[Dict[str, Any]],
        tagged_content: str
    ) -> List[Dict[str, Any]]:
        """
        Group consecutive sentences with the same skill properties into paragraphs.

        Args:
            skill_tags_raw: List of skill tags from LLM
            tagged_content: Story content with sentence tags

        Returns:
            List of grouped tags with paragraph evidence
        """
        tags = []

        for skill_tag in skill_tags_raw:
            skill_id = skill_tag.get("skill_id", "")
            skill_name = skill_tag.get("skill_name", "")
            confidence = skill_tag.get("confidence", 0.0)
            rationale = skill_tag.get("rationale", "")

            tag_numbers = TextProcessor.normalize_tag_numbers(skill_tag.get("tag_numbers", []))

            if not tag_numbers:
                continue

            groups = TextProcessor.group_consecutive_numbers(tag_numbers)

            for group in groups:
                paragraph = TextProcessor.extract_sentences_for_tags(tagged_content, group)

                if paragraph:
                    tags.append({
                        "sentence_evidence": paragraph,
                        "skill_id": skill_id,
                        "skill_name": skill_name,
                        "rationale": rationale,
                        "confidence": confidence,
                        "tag_numbers": group
                    })

        return tags

    def tag_story(self, story_id: str) -> Dict[str, Any]:
        """
        Tag a story with applicable reading skills.

        Args:
            story_id: The story identifier

        Returns:
            Dictionary with story metadata and skill tags
        """
        story = self.data_loader.get_story_with_tagged_sentences(story_id)

        tagged_content = story['tagged_content']
        grade_level = story['grade_level']
        story_title = story['story_title']

        skill_tags_raw = self._identify_skills(
            tagged_content=tagged_content,
            grade_level=grade_level
        )

        sentence_mapping = TextProcessor.get_sentence_mapping(tagged_content)

        tags = self._group_consecutive_tags(skill_tags_raw, tagged_content)

        tags.sort(key=lambda t: t.get("tag_numbers", [float('inf')])[0])

        highlighted_text = HighlightingHelper.generate_skill_html_simple(
            sentence_mapping,
            tags
        )

        final_tags = []
        for tag in tags:
            final_tag = {
                "sentence_evidence": tag["sentence_evidence"],
                "skill_id": tag["skill_id"],
                "skill_name": tag["skill_name"],
                "rationale": tag["rationale"],
                "confidence": tag["confidence"]
            }
            final_tags.append(final_tag)

        result = {
            "story_id": story_id,
            "story_title": story_title,
            "grade_level": grade_level,
            "tags": final_tags,
            "highlighted_text": highlighted_text
        }

        return result

    def _identify_skills(
        self,
        tagged_content: str,
        grade_level: int
    ) -> List[Dict[str, Any]]:
        """
        Identify applicable skills for a story using LLM.

        Args:
            tagged_content: Story with sentence tags
            grade_level: Target grade level

        Returns:
            List of skill tags with confidence scores
        """
        user_prompt = build_skill_tagging_prompt(
            skills_df=self.data_loader.skills,
            tagged_content=tagged_content,
            grade_level=grade_level
        )

        try:
            response = self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=get_system_prompt(),
                temperature=0.0,
                max_tokens=4069,
                json_mode=True
            )

            try:
                result = json.loads(response)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse LLM response: {e}")
                result = {}

            skill_tags = result.get("skill_tags", [])

            valid_skill_ids = set(self.data_loader.skills['skill_id'].tolist())
            validated_tags = []

            for tag in skill_tags:
                skill_id = tag.get("skill_id")
                if skill_id in valid_skill_ids:
                    confidence = tag.get("confidence", 0.0)
                    tag["confidence"] = max(0.0, min(1.0, float(confidence)))
                    validated_tags.append(tag)
                else:
                    print(f"Warning: Invalid skill_id '{skill_id}' returned by LLM")

            return validated_tags

        except Exception as e:
            print(f"Warning: Error identifying skills: {e}")
            return []

    def tag_all_stories(
        self,
        max_workers: Optional[int] = 5
    ) -> List[Dict[str, Any]]:
        """
        Tag all stories in the dataset using multithreading.

        Args:
            max_workers: Maximum number of concurrent threads (default: 5)

        Returns:
            List of skill tagging results for all stories
        """
        story_ids = self.data_loader.stories['story_id'].tolist()
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_story = {
                executor.submit(self.tag_story, story_id): story_id
                for story_id in story_ids
            }

            with tqdm(total=len(story_ids), desc="Tagging stories with skills") as pbar:
                for future in as_completed(future_to_story):
                    story_id = future_to_story[future]
                    try:
                        result = future.result()
                        results[story_id] = result
                    except Exception as e:
                        print(f"\nError tagging story {story_id}: {e}")
                        results[story_id] = {
                            "story_id": story_id,
                            "error": str(e),
                            "skill_tags": []
                        }
                    pbar.update(1)

        return [results[story_id] for story_id in story_ids]
