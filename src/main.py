from pathlib import Path

from web import auth_lk, scrape_grades
from utils import load_config
from services import analyze_from_html


def main():
    BASE_DIR = Path(__file__).resolve().parent.parent
    grades_path = BASE_DIR / "data" / "grades.html"
    config = load_config(BASE_DIR / "config" / "config.yaml")

    if grades_path.exists():
        grades_html_data = grades_path.read_text(encoding="utf-8")
    else:
        session = auth_lk(
            config["login_url"],
            config["user_email"],
            config["user_password"]
        )

        if not session:
            return

        grades_html_data = scrape_grades(session, config["grades_url"])

        if not grades_html_data:
            return
    
        grades_path.parent.mkdir(parents=True, exist_ok=True)
        grades_path.write_text(grades_html_data, encoding="utf-8")

    result = analyze_from_html(grades_html_data, config["faculty"], config["study_program"], config["department"], config["retakes"], config["semesters_shown"])

    print(f"Средний балл с учетом пересдач: {result.avg_grade:.2f}")
    print(f"Средний балл без учета пересдач: {result.avg_grade_wo_retake:.2f}")

    grade_labels = {
        3: "Удовлетворительно",
        4: "Хорошо",
        5: "Отлично"
    }

    print(f"\nВ дипломе:")
    for key, value in result.diploma_grade_counts.items():
        print(f"  {grade_labels[key]}: {value}")

    print(f"\nСредний балл диплома: {result.avg_diploma_grade:.2f}")
    print(f"Порог оценок \"Хорошо\" для диплома с отличием: {result.distinction.grade4_limit}\n")

    for message in result.distinction.messages:
        print(message)


if __name__ == "__main__":
    main()
