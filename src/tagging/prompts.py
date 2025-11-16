import pandas as pd


SKILL_TAGGING_SYSTEM_PROMPT = """You are an expert reading specialist with deep knowledge of literacy skills, reading development, and educational standards for children. You excel at analyzing stories to identify which reading skills they can help develop."""


SKILL_TAGGING_USER_PROMPT_TEMPLATE = """Analyze the following children's story to identify which reading skills it demonstrates or teaches.

TARGET AUDIENCE: {grade_name} ({grade_level})

SKILLS TAXONOMY:
{skills_list}

STORY CONTENT (with numbered sentence tags):
{tagged_content}

INSTRUCTIONS:
1. Carefully read the story with its sentence tags (e.g., <tag1>, <tag2>, <tag3>)
2. Identify which skills from the taxonomy are clearly demonstrated or taught in this story
3. For each skill you identify:
   - Assign a confidence score (0.0 to 1.0) based on how strongly the skill is present
   - Note which TAG NUMBERS contain evidence of this skill
   - Provide a brief explanation of why this skill applies
4. Consider the target grade level ({grade_name}) when evaluating appropriateness
5. Only include skills with confidence >= 0.5
6. Prioritize quality over quantity - include only skills that are genuinely present

CONFIDENCE SCORING GUIDELINES:
- 0.9-1.0: Skill is a primary focus or clearly demonstrated multiple times
- 0.7-0.8: Skill is clearly present with good evidence
- 0.5-0.6: Skill is present but not a major focus

EXPECTED JSON FORMAT:
{{
  "skill_tags": [
    {{
      "skill_id": "SKILL-XXX-###",
      "skill_name": "Skill name from taxonomy",
      "confidence": 0.85,
      "tag_numbers": [1, 5, 7],
      "rationale": "Brief explanation of why this skill applies and how it's demonstrated"
    }}
  ]
}}

EXAMPLE OUTPUT:
{{
  "skill_tags": [
    {{
      "skill_id": "SKILL-COMP-003",
      "skill_name": "Character Analysis",
      "confidence": 0.9,
      "tag_numbers": [3, 7, 12, 15],
      "rationale": "Story provides detailed descriptions of character traits, motivations, and how the protagonist changes throughout the narrative"
    }},
    {{
      "skill_id": "SKILL-VOCAB-003",
      "skill_name": "Figurative Language",
      "confidence": 0.7,
      "tag_numbers": [8, 14],
      "rationale": "Contains multiple similes and metaphors that students can identify and interpret"
    }}
  ]
}}

IMPORTANT:
- Return ONLY skills from the provided taxonomy (use exact skill_id and skill_name)
- DO NOT include text_evidence - only tag numbers (we will extract text later)
- Be selective - only include skills with strong evidence (confidence >= 0.5)
- Consider grade-appropriateness when assigning skills
- If no clear skills are present, return: {{"skill_tags": []}}

Return ONLY valid JSON, no additional text."""

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


def format_skills_for_prompt(skills_df: pd.DataFrame) -> str:
    """
    Format skills DataFrame into a readable list for the prompt.

    Args:
        skills_df: DataFrame with skill_id, skill_name, skill_description

    Returns:
        Formatted string of skills for the prompt
    """
    skills_text = []

    # Group by category (based on skill_id prefix)
    categories = {
        "DEC": "Decoding Skills",
        "COMP": "Comprehension Skills",
        "VOCAB": "Vocabulary Skills",
        "KNOW": "Knowledge & Content Skills",
        "FLUENCY": "Fluency Skills"
    }

    for prefix, category_name in categories.items():
        category_skills = skills_df[skills_df['skill_id'].str.contains(f"SKILL-{prefix}")]

        if not category_skills.empty:
            skills_text.append(f"\n## {category_name}")
            for _, skill in category_skills.iterrows():
                skills_text.append(
                    f"- {skill['skill_id']}: {skill['skill_name']}\n"
                    f"  {skill['skill_description']}"
                )

    return "\n".join(skills_text)


def build_skill_tagging_prompt(
    skills_df: pd.DataFrame,
    tagged_content: str,
    grade_level: int
) -> str:
    """
    Build user prompt for skill tagging.

    Args:
        skills_df: DataFrame with skills taxonomy
        tagged_content: Story with sentence tags
        grade_level: Target grade level (0-8)

    Returns:
        Formatted prompt string
    """
    grade_name = GRADE_LEVEL_NAMES.get(grade_level, f"Grade {grade_level}")
    skills_list = format_skills_for_prompt(skills_df)

    return SKILL_TAGGING_USER_PROMPT_TEMPLATE.format(
        grade_name=grade_name,
        grade_level=grade_level,
        skills_list=skills_list,
        tagged_content=tagged_content
    )


def get_system_prompt() -> str:
    """
    Get the system prompt for skill tagging.

    Returns:
        System prompt string
    """
    return SKILL_TAGGING_SYSTEM_PROMPT
