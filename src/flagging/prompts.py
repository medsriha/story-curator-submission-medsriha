CONTENT_REVIEW_SYSTEM_PROMPT = """You are an expert children's content reviewer with deep knowledge of age-appropriate material, child development, and educational content standards"""


CONTENT_REVIEW_USER_PROMPT_TEMPLATE = """Review the following children's story for issues related to: {category_name}

TARGET AUDIENCE: {grade_name} ({grade_level})

RUBRIC TO APPLY:
{rubric}

STORY CONTENT (with numbered sentence tags):
{tagged_content}

INSTRUCTIONS:
1. Carefully read the story with its sentence tags (e.g., <tag1>, <tag2>, <tag3>)
2. Identify any content that matches the rubric criteria
3. For each issue, note which TAG NUMBERS contain the problematic content
4. Consider the target grade level ({grade_name}) when assessing severity
5. Provide your findings as a JSON object with a "flags" array

EXPECTED JSON FORMAT:
{{
  "flags": [
    {{
      "issue_type": "Category name (e.g., 'Violence & Physical Harm')",
      "severity_level": "Critical, High, Medium, or Low",
      "confidence": 0.0 to 1.0,
      "tag_numbers": 1,
      "rationale": "Why this is problematic for the target audience",
      "recommendation": "Remove, Revise, Add context, or Teacher guidance"
    }}
  ]
}}

IMPORTANT:
- If you find NO issues, return: {{"flags": []}}
- DO NOT include text_evidence - only tag numbers (we will extract the text later)
- Be specific about WHY the content is problematic for {grade_name} students
- Assign a confidence score (0.0 to 1.0) based on how certain you are this is actually problematic
  * 0.9-1.0: Very clear violation of rubric criteria
  * 0.7-0.9: Likely problematic, minor ambiguity
  * 0.5-0.7: Borderline case, context-dependent
  * Below 0.5: Low confidence, may be acceptable

Return ONLY valid JSON, no additional text."""


# Grade level name mapping
GRADE_LEVEL_NAMES = {
    0: "Kindergarten",
    1: "Grade 1",
    2: "Grade 2",
    3: "Grade 3",
    4: "Grade 4",
    5: "Grade 5",
    6: "Grade 6",
    7: "Grade 7",
    8: "Grade 8"
}


def build_content_review_prompt(
    category: str,
    rubric: str,
    tagged_content: str,
    grade_level: int
) -> str:
    """
    Build user prompt for content review.

    Args:
        category: Rubric category name (e.g., 'violence_harm')
        rubric: Rubric content for this category
        tagged_content: Story with sentence tags
        grade_level: Target grade level (0-8)

    Returns:
        Formatted prompt string
    """
    category_name = category.replace('_', ' ').title()
    grade_name = GRADE_LEVEL_NAMES.get(grade_level, f"Grade {grade_level}")

    return CONTENT_REVIEW_USER_PROMPT_TEMPLATE.format(
        category_name=category_name,
        grade_name=grade_name,
        grade_level=grade_level,
        rubric=rubric,
        tagged_content=tagged_content
    )


def get_system_prompt() -> str:
    """
    Get the system prompt for content review.

    Returns:
        System prompt string
    """
    return CONTENT_REVIEW_SYSTEM_PROMPT