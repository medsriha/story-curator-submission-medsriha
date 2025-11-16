from src.utils.text_processor import TextProcessor


class TestSentenceSplitting:

    def test_basic_sentence_split(self):
        text = "Hello world. How are you? I am fine."
        sentences = TextProcessor.split_into_sentences(text)
        assert len(sentences) == 3
        assert sentences[0] == "Hello world."
        assert sentences[1] == "How are you?"
        assert sentences[2] == "I am fine."

    def test_empty_text(self):
        sentences = TextProcessor.split_into_sentences("")
        assert len(sentences) == 0

    def test_single_sentence(self):
        text = "This is a single sentence."
        sentences = TextProcessor.split_into_sentences(text)
        assert len(sentences) == 1


class TestSentenceTagging:
    """Tests for sentence tagging functionality"""

    def test_basic_tagging(self):
        text = "Hello world. How are you?"
        tagged = TextProcessor.tag_sentences(text)
        assert "<tag1>Hello world.</tag1>" in tagged
        assert "<tag2>How are you?</tag2>" in tagged

    def test_tag_numbering(self):
        text = "First. Second. Third."
        tagged = TextProcessor.tag_sentences(text)
        assert "<tag1>" in tagged
        assert "<tag2>" in tagged
        assert "<tag3>" in tagged


class TestSentenceExtraction:
    """Tests for sentence extraction by tag."""

    def test_extract_by_tag(self):
        text = "First sentence. Second sentence. Third sentence."
        tagged = TextProcessor.tag_sentences(text)

        first = TextProcessor.extract_sentence_by_tag(tagged, 1)
        second = TextProcessor.extract_sentence_by_tag(tagged, 2)
        third = TextProcessor.extract_sentence_by_tag(tagged, 3)

        assert "First sentence." in first
        assert "Second sentence." in second
        assert "Third sentence." in third

    def test_extract_nonexistent_tag(self):
        text = "Only one sentence."
        tagged = TextProcessor.tag_sentences(text)
        result = TextProcessor.extract_sentence_by_tag(tagged, 99)
        assert result == ""


class TestConsecutiveGrouping:
    """Tests for consecutive number grouping utilities."""

    def test_normalize_tag_numbers_with_int(self):
        result = TextProcessor.normalize_tag_numbers(5)
        assert result == [5]

    def test_normalize_tag_numbers_with_list(self):
        result = TextProcessor.normalize_tag_numbers([3, 1, 2])
        assert result == [1, 2, 3]

    def test_normalize_tag_numbers_with_empty_list(self):
        result = TextProcessor.normalize_tag_numbers([])
        assert result == []

    def test_normalize_tag_numbers_with_invalid(self):
        result = TextProcessor.normalize_tag_numbers("invalid")
        assert result == []

    def test_group_consecutive_numbers_simple(self):
        numbers = [1, 2, 3, 5, 6, 10]
        result = TextProcessor.group_consecutive_numbers(numbers)
        assert result == [[1, 2, 3], [5, 6], [10]]

    def test_group_consecutive_numbers_all_consecutive(self):
        numbers = [1, 2, 3, 4, 5]
        result = TextProcessor.group_consecutive_numbers(numbers)
        assert result == [[1, 2, 3, 4, 5]]

    def test_group_consecutive_numbers_none_consecutive(self):
        numbers = [1, 3, 5, 7]
        result = TextProcessor.group_consecutive_numbers(numbers)
        assert result == [[1], [3], [5], [7]]

    def test_group_consecutive_numbers_empty(self):
        result = TextProcessor.group_consecutive_numbers([])
        assert result == []

    def test_extract_sentences_for_tags(self):
        text = "First. Second. Third."
        tagged = TextProcessor.tag_sentences(text)
        result = TextProcessor.extract_sentences_for_tags(tagged, [1, 3])
        assert "First." in result
        assert "Third." in result
        assert "Second." not in result

    def test_extract_sentences_for_tags_consecutive(self):
        text = "First. Second. Third."
        tagged = TextProcessor.tag_sentences(text)
        result = TextProcessor.extract_sentences_for_tags(tagged, [1, 2, 3])
        assert result == "First. Second. Third."