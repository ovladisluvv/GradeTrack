import logging
from pathlib import Path
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QTimer

from utils import load_config
from web import (
    auth_lk,
    scrape_grades,
    InvalidEmailError,
    InvalidPasswordError,
    AuthError,
    GradesPageLoadError
)
from services import analyze_from_html
from core import parse_grades, GradesAnalysisResult
from gui import TerminalView, WizardView

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class AuthWorker(QObject):
    """Runs the blocking login + scrape network I/O off the UI thread"""
    finished = pyqtSignal(str) # scraped grades HTML
    failed = pyqtSignal(str) # user-facing error message

    def __init__(self, login_url: str, grades_url: str, email: str, password: str):
        super().__init__()
        self._login_url = login_url
        self._grades_url = grades_url
        self._email = email
        self._password = password

    def run(self) -> None:
        try:
            session = auth_lk(login_url=self._login_url, email=self._email, password=self._password)
            html = scrape_grades(session=session, grades_url=self._grades_url)
            self.finished.emit(html)

        except InvalidEmailError:
            self.failed.emit("Неверный email. Проверьте данные и попробуйте снова")

        except InvalidPasswordError:
            self.failed.emit("Неверный пароль. Проверьте данные и попробуйте снова")

        except GradesPageLoadError:
            self.failed.emit("Не удалось загрузить страницу оценок. Попробуйте позже")

        except AuthError:
            self.failed.emit("Не удалось авторизоваться (страница входа недоступна или изменилась)")

        except Exception as e:
            logger.exception("Unexpected error during authentication/scraping")
            self.failed.emit(f"Непредвиденная ошибка при загрузке данных: {e}")


class StateManager(QObject):
    """Controller driving the wizard view, orchestrating the terminal, the button panel and data processing"""
    DEPARTMENT_NONE_ID = "dep_none"
    BACK_ID = "__back__"
    BACK_LABEL = "← Назад"

    # Offline test account: skips the network and reads a bundled local HTML file
    TEST_EMAIL = "test"
    TEST_PASSWORD = "test"
    TEST_GRADES_FILE = "test_grades.html"

    def __init__(self, terminal_view: TerminalView, wizard_view: WizardView, parent=None):
        super().__init__(parent)
        self.terminal = terminal_view
        self.wizard = wizard_view

        self.current_state = "INIT"

        self.login_url = ""
        self.grades_url = ""
        self.faculties: dict = {}
        self.programs: dict = {}
        self.departments: dict = {}
        self._config_ok = False

        self.email = ""
        self.password = ""
        self.selected_faculty = ""
        self.selected_program = ""
        self.selected_department: str | None = None
        self.retakes = 0

        self.raw_html = ""
        self.max_completed_semester = 0

        self._auth_thread: QThread | None = None
        self._auth_worker: AuthWorker | None = None

        self._load_configuration()

        self.wizard.option_selected.connect(self.handle_option_selection)
        self.terminal.line_entered.connect(self.handle_line_entered)

    def start(self) -> None:
        """Prints the banner and starts the wizard from the login prompt"""
        self.terminal.clear_screen()
        self.wizard.clear_options()
        self.terminal.print_line("GradeTrack", "bright", heading=True)
        self.terminal.print_line("Система анализа успеваемости студента\n", "primary")

        if not self._config_ok:
            self.terminal.print_line(
                "ОШИБКА: не удалось загрузить config/config.yaml или "
                "data/university_structure.yaml. Проверьте файлы конфигурации",
                "error",
            )
            self.terminal.set_input_enabled(False)
            return

        self._prompt_login()

    def handle_line_entered(self, text: str) -> None:
        """Dispatcher for console-input submissions, keyed on the current state"""
        if self.current_state == "INPUT_LOGIN":
            self.email = text
            self._prompt_password()

        elif self.current_state == "INPUT_PASSWORD":
            self.password = text
            self._start_auth()

        elif self.current_state == "INPUT_RETAKES":
            try:
                value = int(text)

            except ValueError:
                self.terminal.print_line("Введите целое неотрицательное число", "error")
                self._prompt_retakes()
                return

            self.retakes = max(0, value)
            self.transition_to_action_selection()

    def transition_to_faculty_selection(self) -> None:
        """Starts the wizard at the faculty selection stage"""
        self.current_state = "SELECT_FACULTY"
        self.terminal.set_input_enabled(False)
        self.terminal.print_line("\n[ЭТАП 1] Выберите факультет", "info", heading=True)

        self.wizard.set_options(self.faculties, columns=1)
        self.wizard.set_loading_state(False)

    def transition_to_program_selection(self) -> None:
        """Transitions the wizard to the program selection stage"""
        self.current_state = "SELECT_PROGRAM"
        self.terminal.set_input_enabled(False)
        self.terminal.print_line("\n[ЭТАП 2] Выберите программу обучения", "info", heading=True)

        available = self.programs.get(self.selected_faculty, {})
        self.wizard.set_options(self._options_with_back(available), columns=1)
        self.wizard.set_loading_state(False)

    def transition_to_department_selection(self) -> None:
        """Transitions the wizard to the department selection stage"""
        self.current_state = "SELECT_DEPARTMENT"
        self.terminal.set_input_enabled(False)
        self.terminal.print_line("\n[ЭТАП 3] Выберите кафедру", "info", heading=True)

        available = self.departments.get(self.selected_faculty, {}).get(self.selected_program, {})
        options = {opt_id: label for opt_id, label in sorted(available.items(), key=lambda kv: kv[1])}

        if self.max_completed_semester < 4 or not available:
            options[self.DEPARTMENT_NONE_ID] = "Нет кафедры"

        self.wizard.set_options(self._options_with_back(options), columns=2)
        self.wizard.set_loading_state(False)

    def transition_to_action_selection(self) -> None:
        """Transitions the wizard to the action selection stage"""
        self.current_state = "SELECT_ACTION"
        self.terminal.set_input_enabled(False)
        self.terminal.print_line("\n[ЭТАП 5] Что рассчитать", "info", heading=True)

        actions = {
            "action_avg": "Средний балл",
            "action_diploma": "Красный диплом",
        }

        self.wizard.set_options(self._options_with_back(actions), columns=2)
        self.wizard.set_loading_state(False)

    def transition_to_semester_selection(self) -> None:
        """Transitions the wizard to the semester selection stage"""
        self.current_state = "SELECT_SEMESTERS"
        self.terminal.set_input_enabled(False)
        self.terminal.print_line("\nЗа сколько семестров показать средний балл?", "info")

        options = {}
        for sem in range(1, self.max_completed_semester + 1):
            options[f"sem_{sem}"] = f"За {sem} сем."
        options["sem_all"] = "За все семестры"

        self.wizard.set_options(self._options_with_back(options), columns=2 if len(options) > 4 else 3)
        self.wizard.set_loading_state(False)

    def handle_option_selection(self, option_id: str, option_text: str) -> None:
        """Dispatcher for wizard button selections, keyed on the current state"""
        if option_id == self.BACK_ID:
            self._go_back()
            return

        self.terminal.print_line(f"> {option_text}", "primary", typewriter=False)

        if self.current_state == "SELECT_FACULTY":
            self.selected_faculty = option_id
            self.transition_to_program_selection()

        elif self.current_state == "SELECT_PROGRAM":
            self.selected_program = option_id
            self.transition_to_department_selection()

        elif self.current_state == "SELECT_DEPARTMENT":
            self.selected_department = None if option_id == self.DEPARTMENT_NONE_ID else option_id
            self._prompt_retakes()

        elif self.current_state == "SELECT_ACTION":
            if option_id == "action_avg":
                self.transition_to_semester_selection()
            elif option_id == "action_diploma":
                self.show_diploma_stats()

        elif self.current_state == "SELECT_SEMESTERS":
            self.show_average_grades(option_id)

    def show_average_grades(self, semester_id: str) -> None:
        """Runs the average grade analysis for the selected semester range and prints results"""
        if semester_id == "sem_all":
            sem_filter = 0
            period = "за весь период обучения"
        else:
            sem_filter = int(semester_id.split("_")[1])
            period = f"за {sem_filter} сем."

        result = self._run_analysis(semesters_shown=sem_filter)

        if result is None:
            self._loop_back_to_actions()
            return

        is_all = semester_id == "sem_all"

        self.terminal.print_line(f"\nСредний балл ({period})", "bright", heading=True)

        if is_all:
            self.terminal.print_kv("С учетом пересдач: ", f"{result.avg_grade:.2f}")

        self.terminal.print_kv("Без учета пересдач: ", f"{result.avg_grade_wo_retake:.2f}")

        if is_all:
            self.terminal.print_kv("Средний балл диплома: ", f"{result.avg_diploma_grade:.2f}")

        self._loop_back_to_actions()
    
    def show_diploma_stats(self) -> None:
        """Runs the diploma analysis and prints results"""
        result = self._run_analysis(semesters_shown=0)

        if result is None:
            self._loop_back_to_actions()
            return

        self.terminal.print_line("\nСтатистика красного диплома", "bright", heading=True)

        counts = result.diploma_grade_counts
        self.terminal.print_line("Оценки в дипломе:", "primary")
        self.terminal.print_kv("    Отлично: ", counts.get(5, 0))
        self.terminal.print_kv("    Хорошо: ", counts.get(4, 0))
        self.terminal.print_kv("    Удовлетворительно: ", counts.get(3, 0))

        if self.selected_department is not None:
            self.terminal.print_kv(
                "\nМаксимально допустимое число четверок для получения красного диплома: ",
                result.distinction.grade4_limit,
            )
        else:
            self.terminal.print_line(
                "Максимальное число четверок скрыто (выберите кафедру для точного расчета)",
                "info",
            )

        self.terminal.print_line("\nВердикт:", "info")
        for msg in result.distinction.messages:
            msg_type = "error" if "слишком много" in msg.lower() else "primary"
            self.terminal.print_line(f"- {msg}", msg_type)

        self._loop_back_to_actions()

    def _options_with_back(self, options: dict) -> dict:
        """Returns a copy of options with a trailing back button"""
        opts = dict(options)
        opts[self.BACK_ID] = self.BACK_LABEL

        return opts

    def _load_configuration(self) -> None:
        """Loads URLs from config.yaml and menu structures from university_structure.yaml"""
        try:
            config = load_config(BASE_DIR / "config" / "config.yaml")
            self.login_url = config["login_url"]
            self.grades_url = config["grades_url"]

            structure = load_config(BASE_DIR / "data" / "university_structure.yaml")
            self.faculties = structure.get("faculties", {})
            self.programs = structure.get("programs", {})
            self.departments = structure.get("departments", {})

            self._config_ok = bool(self.login_url and self.grades_url and self.faculties)

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._config_ok = False

    def _run_analysis(self, semesters_shown: int) -> GradesAnalysisResult | None:
        """Runs the core analysis with the current selections; returns result or None"""
        try:
            return analyze_from_html(
                html_content=self.raw_html,
                faculty=self.selected_faculty,
                study_program=self.selected_program,
                department=self.selected_department,
                retakes=self.retakes,
                semesters_shown=semesters_shown,
            )

        except Exception as e:
            self.terminal.print_line(f"\nОшибка расчета: {e}", "error")
            return None

    def _prompt_login(self) -> None:
        """Prompts the user to enter their email for login"""
        self.current_state = "INPUT_LOGIN"
        self.wizard.clear_options()
        self.terminal.request_input("Введите email для входа в ЛК:")

    def _prompt_password(self) -> None:
        """Prompts the user to enter their password for login"""
        self.current_state = "INPUT_PASSWORD"
        self.terminal.request_input("Введите пароль:", password=True)

    def _prompt_retakes(self) -> None:
        """Prompts the user to enter the number of retakes"""
        self.current_state = "INPUT_RETAKES"
        self.wizard.set_options({self.BACK_ID: self.BACK_LABEL}, columns=1)
        self.wizard.set_loading_state(False)
        self.terminal.print_line("\n[ЭТАП 4] Введите число пересдач", "info", heading=True)
        self.terminal.request_input("(0, если пересдач не было):", numeric=True)

    def _start_auth(self) -> None:
        """Starts the authentication and grades scraping in a background thread"""
        self.current_state = "AUTH"
        self.terminal.set_input_enabled(False)
        self.wizard.clear_options()

        if self.email == self.TEST_EMAIL and self.password == self.TEST_PASSWORD:
            self._load_local_test_grades()
            return

        self.terminal.print_line("\nАвторизация и загрузка данных...", "info")

        self._auth_thread = QThread(self)
        self._auth_worker = AuthWorker(self.login_url, self.grades_url, self.email, self.password)
        self._auth_worker.moveToThread(self._auth_thread)

        self._auth_thread.started.connect(self._auth_worker.run)
        self._auth_worker.finished.connect(self._on_auth_finished)
        self._auth_worker.failed.connect(self._on_auth_failed)

        self._auth_worker.finished.connect(self._auth_thread.quit)
        self._auth_worker.failed.connect(self._auth_thread.quit)
        self._auth_thread.finished.connect(self._cleanup_auth_thread)

        self._auth_thread.start()

    def _cleanup_auth_thread(self) -> None:
        """Cleans up the auth thread and worker after completion"""
        if self._auth_worker is not None:
            self._auth_worker.deleteLater()
            self._auth_worker = None

        if self._auth_thread is not None:
            self._auth_thread.deleteLater()
            self._auth_thread = None

    def _load_local_test_grades(self) -> None:
        """Loads grades HTML from the bundled local test file (offline test account)"""
        self.terminal.print_line("\nТестовый режим: загрузка локальных данных...", "info")
        path = BASE_DIR / "data" / self.TEST_GRADES_FILE

        try:
            html = path.read_text(encoding="utf-8")

        except OSError as e:
            self.terminal.print_line(
                f"Не удалось прочитать локальный файл {self.TEST_GRADES_FILE}: {e}", "error"
            )
            self._prompt_login()
            return

        self._on_auth_finished(html)

    def _on_auth_finished(self, html: str) -> None:
        """Handles the successful completion of the auth + scrape process"""
        self.raw_html = html

        try:
            grades = parse_grades(html)
            semesters = [g.semester for g in grades]
            self.max_completed_semester = max(semesters) if semesters else 0

        except Exception as e:
            self.terminal.print_line(f"Ошибка разбора страницы оценок: {e}", "error")
            self._prompt_login()
            return

        if self.max_completed_semester == 0:
            self.terminal.print_line("В загруженных данных не найдено оценок", "error")
            self._prompt_login()
            return

        self.terminal.print_kv(
            "Данные загружены. Обнаружено семестров с оценками: ",
            self.max_completed_semester,
        )
        self.transition_to_faculty_selection()

    def _on_auth_failed(self, message: str) -> None:
        """Handles the failure of the auth + scrape process"""
        self.terminal.print_line(message, "error")
        self._prompt_login()

    def _go_back(self) -> None:
        """Returns to the selection of the previous step, based on the current state"""
        st = self.current_state
        if st == "SELECT_PROGRAM":
            self.transition_to_faculty_selection()
        elif st == "SELECT_DEPARTMENT":
            self.transition_to_program_selection()
        elif st == "INPUT_RETAKES":
            self.transition_to_department_selection()
        elif st == "SELECT_ACTION":
            self._prompt_retakes()
        elif st == "SELECT_SEMESTERS":
            self.transition_to_action_selection()

    def _loop_back_to_actions(self) -> None:
        """Returns to the action menu so the user can run another calculation"""
        QTimer.singleShot(600, self.transition_to_action_selection)
