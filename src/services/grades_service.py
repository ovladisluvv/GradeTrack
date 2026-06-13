from pathlib import Path

from web import auth_lk, scrape_grades
from core import (
    GradeInfo,
    DiplomaSubjectsInfo,
    GradesAnalysisResult,
    parse_grades,
    preprocess_grades,
    get_avg_grade,
    get_diploma_grades_stats,
    diploma_with_distinction_check
)


def analyze_from_web(
    login_url: str,
    grades_url: str,
    email: str,
    password: str,
    faculty: str,
    study_program: str,
    department: str | None = None,
    retakes: int = 0,
    semesters_shown: int | None = None
) -> GradesAnalysisResult:
    """Start the analysis of grades from the web"""
    session = auth_lk(login_url=login_url, email=email, password=password)

    html_content = scrape_grades(session=session, grades_url=grades_url)

    result = analyze_from_html(
        html_content=html_content,
        faculty=faculty,
        study_program=study_program,
        department=department,
        retakes=retakes,
        semesters_shown=semesters_shown
    )

    return result


def analyze_from_html(
    html_content: str,
    faculty: str,
    study_program: str,
    department: str | None = None,
    retakes: int = 0,
    semesters_shown: int | None = None
) -> GradesAnalysisResult:
    """Analyze grades from loaded HTML. Is useful for tests"""
    diploma_subjects = DiplomaSubjectsInfo()

    raw_grades = parse_grades(html_content)

    processed_grades = preprocess_grades(
        grades_data=raw_grades,
        diploma_subjects=diploma_subjects,
        faculty=faculty,
        study_program=study_program,
        department=department
    )

    avg_grade, avg_grade_wo_retake = get_avg_grade(grades_data=processed_grades, retakes=retakes, semesters_shown=semesters_shown)

    diploma_stats = get_diploma_grades_stats(processed_grades)
    diploma_subjects_count = diploma_subjects.count_subjects(faculty=faculty, study_program=study_program, department=department)

    distinction = diploma_with_distinction_check(diploma_stats=diploma_stats, diploma_subjects_count=diploma_subjects_count)

    result = GradesAnalysisResult(
        grades=processed_grades,
        avg_grade=avg_grade,
        avg_grade_wo_retake=avg_grade_wo_retake,
        diploma_stats=diploma_stats,
        distinction=distinction
    )

    return result
