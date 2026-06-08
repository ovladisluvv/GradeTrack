from core import GradeInfo


def get_avg_grade(grades_data: list[GradeInfo], semesteres_shown: int = 0, retakes: int = 0) -> tuple[float, float]:
    """Calculate average grade with and without retakes for the given grades data"""
    grade_values = [grade.grade_num for grade in grades_data if grade.semester <= semesteres_shown]
    avg_grade = (sum(grade_values) + retakes * 2) / (len(grade_values) + retakes) if grade_values else 0.0
    avg_grade_wo_retake = sum(grade_values) / len(grade_values) if grade_values else 0.0

    return avg_grade, avg_grade_wo_retake
