"""
Agent 5 - Run Script
Generates the PDF using the full Python path and saves it to the project folder.
"""
import sys, os, shutil

AGENT5_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AGENT5_DIR)

from data_loader import load_input_data
from plan_generator import generate_30_day_plan
from resource_validator import validate_schedule_links, print_validation_report
from pdf_generator import generate_pdf

TEMP_PDF  = os.path.join(os.environ.get("TEMP", os.environ.get("TMP", "C:\\Temp")),
                          "30_Days_Learning_Plan.pdf")
FINAL_PDF = os.path.join(AGENT5_DIR, "30_Days_Learning_Plan.pdf")

print("=== Agent 5 - 30-Day Personalized Learning Planner ===")
print()

print("[1/5] Loading input data...")
data = load_input_data()
print("      Skills found: " + str(len(data["missing_skills"])))

print("[2/5] Generating 30-day schedule...")
schedule = generate_30_day_plan(
    data["missing_skills"], data["skill_priority"], data["agent3_course_suggestions"]
)
print("      Days in schedule: " + str(len(schedule)))

print("[3/5] Validating resource links...")
warnings = validate_schedule_links(schedule)
print_validation_report(warnings)

print("[4/5] Generating PDF to: " + TEMP_PDF)
saved = generate_pdf(schedule, data["user_profile"], data["missing_skills"], TEMP_PDF)
sz = os.path.getsize(saved)
print("      PDF size: " + str(sz) + " bytes")

print("[5/5] Saving to project folder: " + FINAL_PDF)
try:
    shutil.copy2(saved, FINAL_PDF)
    print()
    print("SUCCESS! PDF saved to:")
    print("  " + FINAL_PDF)
except Exception as e:
    print("      Could not copy to project folder: " + str(e))
    FINAL_PDF = saved
    print()
    print("SUCCESS! PDF available at:")
    print("  " + FINAL_PDF)
