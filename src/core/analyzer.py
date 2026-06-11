from .grade_modules import GradeInfo, DistinctionCheckResult


def get_avg_grade(grades_data: list[GradeInfo], retakes: int = 0, semesters_shown: int | None = None) -> tuple[float, float]:
    """
    Calculate average grade with and without retakes for the given grades data
    Retakes is the number of failed attempts counted as grade 2
    If semesters_shown is provided, only grades up to that semester will be considered in the calculation
    """
    if semesters_shown is None:
        grade_values = [grade.grade_num for grade in grades_data]
    else:
        grade_values = [grade.grade_num for grade in grades_data if grade.semester <= semesters_shown]

    if not grade_values:
        return 0.0, 0.0

    avg_grade = (sum(grade_values) + retakes * 2) / (len(grade_values) + retakes)
    avg_grade_wo_retake = sum(grade_values) / len(grade_values)

    return avg_grade, avg_grade_wo_retake


def get_diploma_grades_stats(grades_data: list[GradeInfo]) -> dict[int, int]:
    """Count diploma-included grades by grade value"""
    diploma_grades_stats = {
        3: 0,
        4: 0,
        5: 0
    }

    for grade_record in grades_data:
        if grade_record.in_diploma:
            diploma_grades_stats[grade_record.grade_num] += 1

    return diploma_grades_stats

    
def diploma_with_distinction_check(diploma_stats: dict[int, int], diploma_subjects_count: int) -> DistinctionCheckResult:
    """Check if the student can receive a diploma with distinction based on the diploma stats"""
    is_reachable = True
    grade4_limit = diploma_subjects_count // 4 # no more than 25% of "Хорошо" grades
    messages = []

    if diploma_stats[3] > 3:
        messages.append('В дипломе слишком много оценок "Удовлетворительно" для получения диплома с отличием')
        is_reachable = False
    elif diploma_stats[4] + diploma_stats[3] > grade4_limit + 3: # 3 subjects can be retaken
        messages.append(f'В дипломе слишком много оценок "Хорошо" для получения диплома с отличием')
        is_reachable = False
    else:
        messages.append("Возможно получить диплом с отличием!")

        retakes_needed = []

        if diploma_stats[3] > 0:
            retakes_needed.append(f'{diploma_stats[3]} оценок "Удовлетворительно"')

        if diploma_stats[4] > grade4_limit:
            retakes_needed.append(f'{diploma_stats[4] - grade4_limit} оценок "Хорошо"')

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
