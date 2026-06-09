from core import GradeInfo, DiplomaSubjectsInfo


GRADE_LABELS = {
    "отл": 5,
    "хор": 4,
    "удов": 3
}


def get_numeric_grade(grade_text: str) -> int | None:
    """Convert text grade to numeric value based on the defined grade labels"""
    grade_name = grade_text.lower()

    if grade_name.startswith("не"):
        return None

    for label, numeric_grade in GRADE_LABELS.items():
        if label in grade_name:
            return numeric_grade

    return None


def preprocess_grades(
    grades_data: list[GradeInfo],
    diploma_subjects: DiplomaSubjectsInfo,
    faculty: str,
    study_program: str,
    department: str | None = None
) -> list[GradeInfo]:
    """Preprocess grades data by converting text grades to numeric values and filtering out non-passed and non-graded subjects"""
    processed_grades = []

    for grade_record in grades_data:
        numeric_grade = get_numeric_grade(grade_record.grade_text)

        if numeric_grade is None:
            continue

        in_diploma = diploma_subjects.is_in_diploma(
            subject=grade_record.subject,
            semester=grade_record.semester,
            faculty=faculty,
            study_program=study_program,
            department=department
        )

        processed_grades.append(GradeInfo(
            subject=grade_record.subject,
            grade_text=grade_record.grade_text,
            grade_num=numeric_grade,
            in_diploma=in_diploma,
            semester=grade_record.semester
        ))

    return processed_grades
