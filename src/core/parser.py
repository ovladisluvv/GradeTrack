from bs4 import BeautifulSoup


def parse_grades(html_content: str) -> list[list[dict[str, str]]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    grades_data = [[], [], [], [], [], [], [], [], [], [], [], [], []]
    grade_rows = soup.select('tr[data-key]')

    for row in grade_rows:
        tds = row.find_all('td')

        if len(tds) < 3:
            continue

        semester_td = tds[0]
        subject_td = tds[1]
        grade_td = tds[2]

        semester = int(semester_td.get_text(strip=True))

        subject_span = subject_td.find('span', class_='text-success')

        if subject_span:
            subject = subject_span.get_text(strip=True)
            is_diploma_subject = True
        else:
            subject_node = subject_td.find(string=True, recursive=False)
            subject = subject_node.strip() if subject_node else None
            is_diploma_subject = False

        grade = grade_td.get_text(strip=True)

        grades_data[semester - 1].append({
            "subject": subject,
            "grade": grade,
            "in_diploma": is_diploma_subject
        })

    return grades_data
