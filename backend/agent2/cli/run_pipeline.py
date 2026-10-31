"""
CLI Entry Point — AI Career Guidance Platform
Run the full 5-agent pipeline from the terminal.

Usage:
    python cli/run_pipeline.py --resume path/to/resume.txt --jd path/to/jd.txt
    python cli/run_pipeline.py --resume resume.pdf --jd jd.txt --user-id my-user-123
"""

import argparse
import sys
import uuid
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="AI Career Guidance Platform — Full Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/run_pipeline.py --resume resume.txt --jd jd.txt
  python cli/run_pipeline.py --resume resume.pdf --jd jd.txt --user-id abc-123
  python cli/run_pipeline.py --resume resume.txt --jd jd.txt --plan 3_month
        """,
    )
    parser.add_argument("--resume", required=True, help="Path to resume file (.txt or .pdf)")
    parser.add_argument("--jd", required=True, help="Path to job description file (.txt)")
    parser.add_argument("--user-id", default=None, help="User UUID (auto-generated if not provided)")
    parser.add_argument(
        "--plan",
        choices=["30_day", "3_month", "6_month"],
        default="30_day",
        help="Learning plan duration (default: 30_day)",
    )
    parser.add_argument("--skip-interview", action="store_true", help="Skip Module 4 mock interview")

    args = parser.parse_args()

    # Validate inputs
    resume_path = Path(args.resume)
    if not resume_path.exists():
        print(f"❌ Error: Resume file not found: {resume_path}")
        sys.exit(1)

    jd_path = Path(args.jd)
    if not jd_path.exists():
        print(f"❌ Error: JD file not found: {jd_path}")
        sys.exit(1)

    user_id = args.user_id or str(uuid.uuid4())
    jd_text = jd_path.read_text(encoding="utf-8")

    print(f"\n📋 Starting pipeline for user: {user_id}")
    print(f"   Resume: {resume_path}")
    print(f"   JD: {jd_path}")
    print(f"   Plan type: {args.plan}")

    run_pipeline(
        resume_path=str(resume_path),
        jd_text=jd_text,
        user_id=user_id,
    )


if __name__ == "__main__":
    main()
