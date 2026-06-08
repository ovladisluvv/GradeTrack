from pathlib import Path


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
    grades_data: list[list[dict[str, str]]],
    faculty: str,
    study_program: str,
    department: str | None = None
) -> list[list[dict[str, str | int]]]:
    """Preprocess grades data by converting text grades to numeric values and filtering out non-passed and non-graded subjects"""
    grade_labels = {
        "отл": 5,
        "хор": 4,
        "удов": 3
    }

    processed_grades = []

    for semester_num, semester_grades in enumerate(grades_data, start=1):
        semester_processed = []

        for grade_record in semester_grades:
            grade_value = grade_record['grade'].lower()

            if grade_value.startswith("не"):
                continue

            for label, numeric_grade in grade_labels.items():
                if label in grade_value:
                    in_diploma = is_in_diploma(grade_record['subject'], semester_num, faculty, study_program, department)

                    semester_processed.append({
                        "subject": grade_record['subject'],
                        "grade": numeric_grade,
                        "in_diploma": in_diploma
                    })

                    break

        processed_grades.append(semester_processed)

    return processed_grades
