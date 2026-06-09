class GradeInfo:
    """Data class to store information about a single grade record"""
    def __init__(self, subject: str, grade_text: str, in_diploma: bool, semester: int, grade_num: int = 0):
        self.subject = subject
        self.grade_text = grade_text
        self.in_diploma = in_diploma
        self.semester = semester
        self.grade_num = grade_num


class DistinctionCheckResult:
    """Data class to store the result of checking if diploma with distinction is reachable"""
    def __init__(self, is_reachable: bool, grade5_percentage: float, messages: list[str]):
        self.is_reachable = is_reachable
        self.grade5_percentage = grade5_percentage
        self.messages = messages
