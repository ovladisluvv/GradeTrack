class GradeInfo:
    """Data class for storing information about a single grade record"""
    def __init__(self, subject: str, grade_text: str, in_diploma: bool, semester: int, grade_num: int = 0):
        self.subject = subject
        self.grade_text = grade_text
        self.in_diploma = in_diploma
        self.semester = semester
        self.grade_num = grade_num


class DistinctionCheckResult:
    """Data class for storing the result of checking if diploma with distinction is reachable"""
    def __init__(self, is_reachable: bool, grade4_limit: int, messages: list[str]):
        self.is_reachable = is_reachable
        self.grade4_limit = grade4_limit
        self.messages = messages


class GradesAnalysisResult:
    """Data class for storing the result of grades analysis for orchestration module"""
    def __init__(
        self,
        grades: list[GradeInfo],
        avg_grade: float,
        avg_grade_wo_retake: float,
        avg_diploma_grade: float,
        diploma_grade_counts: dict[int, int],
        distinction: DistinctionCheckResult
    ):
        self.grades = grades
        self.avg_grade = avg_grade
        self.avg_grade_wo_retake = avg_grade_wo_retake
        self.avg_diploma_grade = avg_diploma_grade
        self.diploma_grade_counts = diploma_grade_counts
        self.distinction = distinction
