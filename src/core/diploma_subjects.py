from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class DiplomaSubjectsInfo:
    """
    Reads diploma-inclusion subjects from data/in_diploma

    Expected structure:
        data/in_diploma/<faculty>/<study_program>/sem1.txt
        data/in_diploma/<faculty>/<study_program>/sem2.txt
        ...
        data/in_diploma/<faculty>/<study_program>/<department>/sem5.txt
        ...
    """
    def __init__(self, max_semesters: int = 13):
        self.diploma_subjects_dir = BASE_DIR / "data" / "in_diploma"  # Path to the directory containing diploma subjects
        self.max_semesters = max_semesters  # There's an extra semester for state exams and graduation thesis defense

    def get_semester_file_path(
        self,
        faculty: str,
        study_program: str,
        semester: int,
        department: str | None = None
    ) -> Path:
        """Construct the file path for the given semester and student info"""
        if semester < 1:
            raise ValueError("Semester number has to be >= 1")

        filename = f"sem{semester}.txt"
        filepath = self.diploma_subjects_dir / faculty / study_program

        if semester > 4:
            if not department:
                raise ValueError("Department is required for semesters greater than 4")

            filepath = filepath / department

        return filepath / filename

    def get_subjects_for_semester(
        self,
        faculty: str,
        study_program: str,
        semester: int,
        department: str | None = None
    ) -> list[str]:
        """Get the list of subjects included in the diploma for the given semester and student info"""
        filepath = self.get_semester_file_path(
            faculty=faculty,
            study_program=study_program,
            semester=semester,
            department=department
        )

        if not filepath.exists():
            return []

        with filepath.open("r", encoding="utf-8") as file:
            return [line.strip().lower() for line in file if line.strip()]

    def is_in_diploma(
        self,
        subject: str,
        semester: int,
        faculty: str,
        study_program: str,
        department: str | None = None
    ) -> bool:
        diploma_subjects = self.get_subjects_for_semester(
            faculty=faculty,
            study_program=study_program,
            semester=semester,
            department=department
        )

        return any(diploma_subject in subject.lower() for diploma_subject in diploma_subjects)

    def count_subjects(
        self,
        faculty: str,
        study_program: str,
        department: str | None = None,
    ) -> int:
        subject_count = 0

        for semester in range(1, self.max_semesters + 1):
            if semester > 4 and not department:
                break

            subjects = self.get_subjects_for_semester(
                faculty=faculty,
                study_program=study_program,
                semester=semester,
                department=department
            )

            subject_count += len(subjects)

        return subject_count
