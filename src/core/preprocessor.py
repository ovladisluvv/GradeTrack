from pathlib import Path

from src.core.grade_info import GradeInfo


def is_in_diploma(
    subject: str,
    semester_num: int,
    faculty: str,
    study_program: str,
    department: str | None = None
) -> bool:
    """Check if the subject is included in the diploma for the given semester"""
    filename = f"sem{semester_num}.txt"
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    filepath = BASE_DIR / "data" / "in_diploma" / faculty / study_program

    if semester_num > 4 and department:
        filepath = filepath / department / filename
    else:
        filepath = filepath / filename

    with filepath.open("r", encoding="utf-8") as file:
        for diploma_subject in file:
            diploma_subject = diploma_subject.strip().lower()

            if subject.lower() in diploma_subject:
                return True

    return False


def preprocess_grades(
    grades_data: list[GradeInfo],
    faculty: str,
    study_program: str,
    department: str | None = None
) -> list[GradeInfo]:
    """Preprocess grades data by converting text grades to numeric values and filtering out non-passed and non-graded subjects"""
    grade_labels = {
        "отл": 5,
        "хор": 4,
        "удов": 3
    }

    processed_grades = []

    for grade_record in grades_data:
        grade_name = grade_record.grade_text.lower()

        if grade_name.startswith("не"):
            continue

        for label, numeric_grade in grade_labels.items():
            if label in grade_name:
                in_diploma = is_in_diploma(grade_record.subject, grade_record.semester, faculty, study_program, department)

                processed_grades.append(GradeInfo(
                    subject=grade_record.subject,
                    grade_text=grade_record.grade_text,
                    grade_num=numeric_grade,
                    in_diploma=in_diploma,
                    semester=grade_record.semester
                ))

                break

    return processed_grades
