from .grade_models import GradeInfo, DistinctionCheckResult


def get_avg_grade(grades_data: list[GradeInfo], retakes: int = 0, semesters_shown: int | None = None) -> tuple[float, float]:
    """
    Calculate average grade with and without retakes for the given grades data
    Retakes is the number of failed attempts counted as grade 2
    If semesters_shown is provided, only grades up to that semester will be considered in the calculation
    """
    if retakes < 0:
        raise ValueError("Ошибка: Число пересдач не может быть отрицательным")

    if semesters_shown is None:
        grade_values = [grade.grade_num for grade in grades_data]
    else:
        grade_values = [grade.grade_num for grade in grades_data if grade.semester <= semesters_shown]

    if not grade_values:
        return 0.0, 0.0

    avg_grade = (sum(grade_values) + retakes * 2) / (len(grade_values) + retakes)
    avg_grade_wo_retake = sum(grade_values) / len(grade_values)

    return avg_grade, avg_grade_wo_retake


def get_diploma_grades_stats(grades_data: list[GradeInfo]) -> tuple[dict[int, int], float]:
    """Count diploma-included grades by grade value"""
    diploma_grade_counts = {
        3: 0,
        4: 0,
        5: 0
    }

    for grade_record in grades_data:
        if grade_record.in_diploma:
            diploma_grade_counts[grade_record.grade_num] += 1

    avg_diploma_grade = (3 * diploma_grade_counts[3] + 4 * diploma_grade_counts[4] + 5 * diploma_grade_counts[5]) / sum(diploma_grade_counts.values()) if sum(diploma_grade_counts.values()) > 0 else 0.0

    return diploma_grade_counts, avg_diploma_grade


def diploma_with_distinction_check(diploma_grade_counts: dict[int, int], diploma_subjects_count: int) -> DistinctionCheckResult:
    """Check if the student can receive a diploma with distinction based on the diploma stats"""
    is_reachable = True
    grade4_limit = diploma_subjects_count // 4  # No more than 25% of "Хорошо" grades
    messages = []

    grade3_count = diploma_grade_counts[3]
    grade4_count = diploma_grade_counts[4]
    max_retakes_allowed = 3

    if grade3_count > max_retakes_allowed:
        messages.append('В дипломе слишком много оценок "Удовлетворительно" для получения диплома с отличием')
        is_reachable = False
    elif grade4_count + grade3_count > grade4_limit + max_retakes_allowed:  # max_retakes_allowed subjects can be retaken
        messages.append(f'В дипломе слишком много оценок "Хорошо" для получения диплома с отличием')
        is_reachable = False
    else:
        messages.append("Возможно получить диплом с отличием!")

        retakes_needed = []

        if grade3_count > 0:
            retakes_needed.append(f'{grade3_count} оценок "Удовлетворительно"')

        if grade4_count > grade4_limit:
            retakes_needed.append(f'{grade4_count - grade4_limit} оценок "Хорошо"')

        if retakes_needed:
            message = "Для его получения необходимо пересдать "
            message += " и ".join(retakes_needed)
            messages.append(message)

    result = DistinctionCheckResult(
        is_reachable=is_reachable,
        grade4_limit=grade4_limit,
        messages=messages
    )

    return result
