import re
from typing import Any, List, Tuple
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)


class TextProcessor:
    """Handles text preprocessing and sentence tagging."""

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Split text into sentences using NLTK's sentence tokenizer.

        Args:
            text: Input text to split

        Returns:
            List of sentences
        """
        if not text or not text.strip():
            return []

        sentences = nltk.sent_tokenize(text)

        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    @staticmethod
    def tag_sentences(text: str, tag_prefix: str = "tag") -> str:
        """Add XML-style tags to each sentence for identification.
        Args:
            text: Input text to tag
            tag_prefix: Prefix for tags (default: "tag")

        Returns:
            Text with tagged sentences
        """
        sentences = TextProcessor.split_into_sentences(text)

        tagged_sentences = []
        for i, sentence in enumerate(sentences, start=1):
            tagged = f"<{tag_prefix}{i}>{sentence}</{tag_prefix}{i}>"
            tagged_sentences.append(tagged)

        return " ".join(tagged_sentences)

    @staticmethod
    def extract_sentence_by_tag(text: str, tag_number: int) -> str:
        """Extract a specific sentence by its tag number.

        Args:
            text: Tagged text
            tag_number: Tag number to extract

        Returns:
            Sentence content without tags, or empty string if not found
        """
        pattern = f'<tag{tag_number}>(.*?)</tag{tag_number}>'
        match = re.search(pattern, text)
        return match.group(1) if match else ""

    @staticmethod
    def get_sentence_mapping(text: str) -> List[Tuple[int, str]]:
        """Get a mapping of tag numbers to sentences.

        Args:
            text: Input text (will be tagged if not already)

        Returns:
            List of tuples (tag_number, sentence_text)
        """
        # Check if already tagged
        if not re.search(r'<tag\d+>', text):
            text = TextProcessor.tag_sentences(text)

        mapping = []
        pattern = r'<tag(\d+)>(.*?)</tag\1>'
        matches = re.finditer(pattern, text)

        for match in matches:
            tag_num = int(match.group(1))
            sentence_text = match.group(2)
            mapping.append((tag_num, sentence_text))

        return mapping

    @staticmethod
    def normalize_tag_numbers(tag_numbers: Any) -> List[int]:
        """Normalize tag_numbers to always be a sorted list.

        Args:
            tag_numbers: Either an integer or list of integers

        Returns:
            Sorted list of tag numbers
        """
        if isinstance(tag_numbers, int):
            return [tag_numbers]
        elif isinstance(tag_numbers, list):
            return sorted(tag_numbers)
        else:
            return []

    @staticmethod
    def group_consecutive_numbers(numbers: List[int]) -> List[List[int]]:
        """Group consecutive numbers into separate lists.

        Args:
            numbers: List of integers (should be sorted)

        Returns:
            List of lists, where each inner list contains consecutive numbers

        Example:
            [1, 2, 3, 5, 6, 10] -> [[1, 2, 3], [5, 6], [10]]
        """
        if not numbers:
            return []

        groups = []
        current_group = [numbers[0]]

        for i in range(1, len(numbers)):
            if numbers[i] == current_group[-1] + 1:
                # Consecutive - add to current group
                current_group.append(numbers[i])
            else:
                # Not consecutive - start new group
                groups.append(current_group)
                current_group = [numbers[i]]

        # Add the last group
        groups.append(current_group)

        return groups

    @staticmethod
    def extract_sentences_for_tags(
        tagged_content: str,
        tag_numbers: List[int]
    ) -> str:
        """Extract and join sentences for given tag numbers.

        Args:
            tagged_content: Story content with sentence tags
            tag_numbers: List of tag numbers to extract

        Returns:
            Joined sentences as a single paragraph
        """
        sentences = []
        for tag_num in tag_numbers:
            sentence = TextProcessor.extract_sentence_by_tag(tagged_content, tag_num)
            if sentence:
                sentences.append(sentence)

        return " ".join(sentences)
