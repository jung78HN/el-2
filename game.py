import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from questions import default_quizzes
from quiz import Quiz


def read_number(prompt: str, minimum: int, maximum: int) -> int:
    while True:
        try:
            number = int(input(prompt).strip())
        except ValueError:
            print(f"입력 오류. {minimum}~{maximum} 사이의 숫자를 입력하세요.")
            continue
        if minimum <= number <= maximum:
            return number
        print(f"범위 오류. {minimum}~{maximum} 사이의 숫자를 입력하세요.")


def read_text(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("내용을 입력하세요.")


class QuizGame:
    """메뉴와 퀴즈 게임의 진행을 관리한다."""

    def __init__(self, state_path: Path | None = None):
        self.quizzes = default_quizzes()
        self.best_score = None
        self.best_correct = None
        self.best_total = None
        self.state_path = state_path if state_path is not None else Path(__file__).with_name("state.json")
        self.backup_path = self.state_path.with_name(f"{self.state_path.name}.bak")
        self.last_saved = None
        self.can_save = True
        self.dirty = False

    @staticmethod
    def show_menu() -> None:
        print("\n========================================")
        print("              태양계 퀴즈")
        print("========================================")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("----------------------------------------")

    def run(self) -> None:
        try:
            self.load()
            while True:
                self.show_menu()
                choice = read_number("선택: ", 1, 5)
                if choice == 5:
                    break
                if choice == 1:
                    self.play()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_score()
        except (KeyboardInterrupt, EOFError):
            print("\n입력이 중단되었습니다.")
        finally:
            if self.dirty and self.can_save:
                self.save()
        print("태양계 퀴즈를 종료합니다.")

    def play(self) -> None:
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        total = len(self.quizzes)
        correct = 0
        print(f"\n퀴즈를 시작합니다. 총 {total}문제")
        for number, quiz in enumerate(self.quizzes, start=1):
            quiz.display(number)
            guess = read_number("정답 번호 (1-4): ", 1, 4)
            if quiz.is_correct(guess):
                print("정답입니다!")
                correct += 1
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번 {quiz.choices[quiz.answer - 1]}입니다.")

        score = correct * 100 // total
        print(f"\n결과: {total}문제 중 {correct}문제 정답 ({score}점)")
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_correct = correct
            self.best_total = total
            self.dirty = True
            print("새로운 최고 점수입니다!")
            self.save()

    def add_quiz(self) -> None:
        print("\n새 퀴즈 등록")
        question = read_text("문제: ")
        choices = []
        for number in range(1, 5):
            choices.append(read_text(f"선택지 {number}: "))
        answer = read_number("정답 번호 (1-4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        self.dirty = True
        if self.save():
            print("퀴즈가 추가되었습니다.")
        else:
            print("이번 실행에 퀴즈를 추가했습니다. 파일에 저장하지 못했습니다.")

    def list_quizzes(self) -> None:
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        print(f"\n등록된 퀴즈 목록 ({len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"  [{number}] {quiz.question}")

    def show_score(self) -> None:
        if self.best_score is None:
            print("아직 완료한 퀴즈가 없습니다.")
            return
        print(f"최고 점수: {self.best_score}점 ({self.best_total}문제 중 {self.best_correct}문제 정답)")

    def load(self) -> None:
        try:
            self.last_saved = self.load_snapshot(self.state_path)
        except FileNotFoundError:
            return
        except (KeyError, TypeError, ValueError, RecursionError):
            try:
                self.load_snapshot(self.backup_path)
            except (OSError, KeyError, TypeError, ValueError, RecursionError):
                print("저장 파일이 손상되었습니다. 기본 퀴즈로 복구합니다.")
            else:
                print("저장 파일이 손상되었습니다. 백업에서 복구합니다.")
            self.dirty = True
            self.save()
            return
        except OSError:
            print("저장 파일을 읽을 수 없어 기본 퀴즈를 사용합니다.")
            print("기존 파일을 보호하기 위해 이번 실행에서는 파일에 저장하지 않습니다.")
            self.can_save = False
            return

        print(f"저장된 데이터를 불러왔습니다. 퀴즈 {len(self.quizzes)}개")

    def load_snapshot(self, path: Path) -> bytes:
        contents = path.read_bytes()
        data = json.loads(contents.decode("utf-8"))
        items = data["quizzes"]
        if not isinstance(items, list):
            raise ValueError("퀴즈 목록이 유효하지 않습니다.")
        quizzes = [Quiz(**item) for item in items]
        score = data["best_score"]
        correct = data["best_correct"]
        total = data["best_total"]
        if score is None:
            if correct is not None or total is not None:
                raise ValueError("점수 기록이 일치하지 않습니다.")
        elif (
            any(type(value) is not int for value in (score, correct, total))
            or not 0 <= correct <= total
            or total == 0
            or score != correct * 100 // total
        ):
            raise ValueError("점수 기록이 유효하지 않습니다.")

        self.quizzes = quizzes
        self.best_score = score
        self.best_correct = correct
        self.best_total = total
        return contents

    def save(self) -> bool:
        if not self.can_save:
            return False

        data = {
            "quizzes": [
                {"question": quiz.question, "choices": quiz.choices, "answer": quiz.answer}
                for quiz in self.quizzes
            ],
            "best_score": self.best_score,
            "best_correct": self.best_correct,
            "best_total": self.best_total,
        }
        try:
            contents = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            if self.last_saved is not None:
                self.replace_file(self.backup_path, self.last_saved)
            self.replace_file(self.state_path, contents)
        except (OSError, UnicodeError):
            print("저장 파일에 기록하지 못했습니다.")
            return False

        self.last_saved = contents
        self.dirty = False
        return True

    @staticmethod
    def replace_file(path: Path, contents: bytes) -> None:
        temporary_path = None
        try:
            with NamedTemporaryFile(
                mode="wb",
                dir=path.parent,
                prefix=f"{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                file.write(contents)
            temporary_path.replace(path)
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass
