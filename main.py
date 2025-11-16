"""
Main entry point.

This script orchestrates the complete pipeline:
1. Load stories and taxonomy
2. Flag potentially problematic content
3. Tag stories with applicable reading skills
4. Generate HTML report for content specialists
"""
import json
import sys
import os
from pathlib import Path

from src.utils.data_loader import DataLoader
from src.utils.llm_client import LLMClient
from src.flagging.content_flagger import ContentFlagger
from src.tagging.skill_tagger import SkillTagger
from src.report.html_generator import HTMLReportGenerator

def main() -> int:
    """Main execution function.

    Returns:
        Exit code (0 for success)
    """

    print("=" * 80)
    print("STORY CURATOR - Automated Content Review System")
    print("=" * 80)

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    print("\nLoading data...")
    data_loader = DataLoader()
    llm_client = LLMClient()

    print(f"  Processing all {len(data_loader.stories)} stories")

    print(f"  Loaded {len(data_loader.skills)} skills")
    print()

    # Output paths
    output_dir = Path("output/machine_readable")
    output_dir.mkdir(parents=True, exist_ok=True)

    flagging_path = output_dir / "story_flagging.json"
    tagging_path = output_dir / "skill_tagging.json"

    print("STEP 1: Content Flagging")
    print("-" * 80)
    content_flagger = ContentFlagger(data_loader=data_loader, llm_client=llm_client)

    # Process all stories
    flagging_results = content_flagger.flag_all_stories()

    with open(flagging_path, 'w', encoding='utf-8') as f:
        json.dump(flagging_results, f, indent=2, ensure_ascii=False)

    print(f"Saved flagging results to: {flagging_path}\n")

    print("STEP 2: Skill Tagging")
    print("-" * 80)
    skill_tagger = SkillTagger(data_loader=data_loader, llm_client=llm_client)

    tagging_results = skill_tagger.tag_all_stories()

    with open(tagging_path, 'w', encoding='utf-8') as f:
        json.dump(tagging_results, f, indent=2, ensure_ascii=False)

    print(f"Saved tagging results to: {tagging_path}\n")

    print("STEP 3: HTML Report Generation")
    print("-" * 80)

    generator = HTMLReportGenerator(
        flagging_json_path=str(flagging_path),
        tagging_json_path=str(tagging_path),
        template_dir="templates"
    )

    if generator.load_data():
        html_path = "output/human_review/review_report.html"
        if generator.save_html(html_path):
            print(f"HTML report saved to: {html_path}\n")
        else:
            print("Failed to generate HTML report\n")

    print("=" * 80)
    print("Pipeline complete!")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
