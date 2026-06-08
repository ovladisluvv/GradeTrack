class GradeInfo:
    def __init__(self, subject: str, grade_text: str, in_diploma: bool, semester: int, grade_num: float = 0.0):
        self.subject = subject
        self.grade_text = grade_text
        self.in_diploma = in_diploma
        self.semester = semester
        self.grade_num = grade_num
