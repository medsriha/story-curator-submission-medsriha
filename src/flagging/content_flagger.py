import json
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ..utils.data_loader import DataLoader
from ..utils.llm_client import LLMClient
from ..utils.text_processor import TextProcessor
from ..utils.highlighting_utils import HighlightingHelper
from .prompts import build_content_review_prompt, get_system_prompt


class ContentFlagger:
    """Flags potentially problematic content in children's stories using LLM."""

    CATEGORIES_TO_CHECK = [
        "critical_safety",
        "violence_harm",
        "age_appropriateness",
        "cultural_sensitivity",
        "emotional_safety",
        "technical_issues",
        "physical_safety"
    ]

    def __init__(self, data_loader: DataLoader, llm_client: LLMClient):
        """
        Initialize content flagger.

        Args:
            data_loader: DataLoader instance with rubrics and stories
            llm_client: LLMClient instance for API calls
        """
        self.data_loader = data_loader
        self.llm_client = llm_client

    def _group_consecutive_flags(
        self,
        flags_raw: List[Dict[str, Any]],
        tagged_content: str
    ) -> List[Dict[str, Any]]:
        """
        Group consecutive sentences with the same flag properties into paragraphs.

        Args:
            flags_raw: List of flags from LLM
            tagged_content: Story content with sentence tags

        Returns:
            List of grouped flags with paragraph evidence
        """
        grouped_flags = []

        for flag in flags_raw:
            issue_type = flag.get("issue_type", "Unknown")
            severity = flag.get("severity_level", "Low")
            confidence = flag.get("confidence", 0.5)
            rationale = flag.get("rationale", "")

            # Normalize and group tag numbers
            tag_numbers = TextProcessor.normalize_tag_numbers(flag.get("tag_numbers", []))

            if not tag_numbers:
                continue

            groups = TextProcessor.group_consecutive_numbers(tag_numbers)

            # Create a flag entry for each group
            for group in groups:
                paragraph = TextProcessor.extract_sentences_for_tags(tagged_content, group)

                if paragraph:
                    grouped_flags.append({
                        "issue_type": issue_type,
                        "severity_level": severity,
                        "confidence": confidence,
                        "text_evidence": paragraph,
                        "rationale": rationale,
                        "tag_numbers": group  # Keep for highlighting
                    })

        return grouped_flags

    def flag_story(self, story_id: str, max_workers: Optional[int] = 7) -> Dict[str, Any]:
        """
        Flag potentially problematic content in a story.

        Args:
            story_id: The story identifier
            max_workers: Maximum number of parallel category checks (default: 7, one per category)
        Returns:
            Dictionary with story metadata, flags, and highlighting info
        """

        story = self.data_loader.get_story_with_tagged_sentences(story_id)

        tagged_content = story['tagged_content']
        grade_level = story['grade_level']
        story_title = story['story_title']

        all_flags_raw = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_category = {
                executor.submit(
                    self._check_category,
                    category=category,
                    tagged_content=tagged_content,
                    grade_level=grade_level
                ): category
                for category in self.CATEGORIES_TO_CHECK
            }
            for future in as_completed(future_to_category):
                category = future_to_category[future]
                try:
                    flags = future.result()
                    all_flags_raw.extend(flags)
                except Exception as e:
                    print(f"Warning: Error checking category {category} for story {story_id}: {e}")

        sentence_mapping = TextProcessor.get_sentence_mapping(tagged_content)

        grouped_flags = self._group_consecutive_flags(all_flags_raw, tagged_content)

        grouped_flags.sort(key=lambda f: f.get("tag_numbers", [float('inf')])[0])

        sentence_flags = {}
        flags = []

        for flag in grouped_flags:
            severity = flag.get("severity_level", "Low")
            issue_type = flag.get("issue_type", "Unknown")
            rationale = flag.get("rationale", "")
            confidence = flag.get("confidence", 0.5)
            text_evidence = flag.get("text_evidence", "")
            tag_numbers = flag.get("tag_numbers", [])

            css_class = HighlightingHelper.SEVERITY_CSS_CLASSES.get(severity, "flag-low")
            color = HighlightingHelper.SEVERITY_COLORS.get(severity, "#fff59d")

            flag_entry = {
                "severity": severity,
                "css_class": css_class,
                "color": color,
                "issue_type": issue_type,
                "text_evidence": text_evidence,
                "rationale": rationale,
                "confidence": confidence
            }

            flags.append(flag_entry)

            for tag_num in tag_numbers:
                if tag_num not in sentence_flags:
                    sentence_flags[tag_num] = []
                sentence_flags[tag_num].append(flag_entry)

        highlighted_text = HighlightingHelper.generate_flag_html_simple(
            sentence_mapping,
            sentence_flags
        )

        has_critical = any(f["severity"] == "Critical" for f in flags)

        result = {
            "story_id": story_id,
            "story_title": story_title,
            "grade_level": grade_level,
            "flag_count": len(flags),
            "has_critical": has_critical,
            "highlighted_text": highlighted_text,
            "flags": flags
        }

        return result

    def _check_category(
        self,
        category: str,
        tagged_content: str,
        grade_level: int
    ) -> List[Dict[str, Any]]:
        """
        Check a story against a specific rubric category.

        Args:
            category: Rubric category name
            tagged_content: Story with sentence tags
            grade_level: Target grade level

        Returns:
            List of flags found for this category
        """

        rubric = self.data_loader.get_rubric_category(category)

        user_prompt = build_content_review_prompt(
            category=category,
            rubric=rubric,
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

            if response:
                try:
                    result = json.loads(response)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse LLM response for {category}: {e}")
                    result = {}

            flags = result.get("flags", [])

            for flag in flags:
                
                tag_nums = TextProcessor.normalize_tag_numbers(flag.get("tag_numbers", []))

                text_evidence_parts = []
                for tag_num in tag_nums:
                    sentence = TextProcessor.extract_sentence_by_tag(tagged_content, tag_num)
                    if sentence:
                        text_evidence_parts.append(sentence)

                flag["text_evidence"] = text_evidence_parts

            return flags

        except Exception as e:
            print(f"Warning: Error checking {category}: {e}")
            return []

    def flag_all_stories(
        self,
        max_workers: Optional[int] = 5
    ) -> List[Dict[str, Any]]:
        """
        Flag all stories in the dataset using multithreading.

        Args:
            max_workers: Maximum number of concurrent threads (default: 5)

        Returns:
            List of flag results for all stories
        """
        story_ids = self.data_loader.stories['story_id'].tolist()
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_story = {
                executor.submit(self.flag_story, story_id): story_id
                for story_id in story_ids
            }

            with tqdm(total=len(story_ids), desc="Flagging stories") as pbar:
                for future in as_completed(future_to_story):
                    story_id = future_to_story[future]
                    try:
                        result = future.result()
                        results[story_id] = result
                    except Exception as e:
                        print(f"\nError flagging story {story_id}: {e}")
                        results[story_id] = {
                            "story_id": story_id,
                            "error": str(e),
                            "highlighting": {},
                            "flag_count": 0,
                            "has_critical": False
                        }
                    pbar.update(1)
        return [results[story_id] for story_id in story_ids]