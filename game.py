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

    def __init__(self):
        self.quizzes = default_quizzes()
        self.best_score = None
        self.best_correct = None
        self.best_total = None

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
            print("새로운 최고 점수입니다!")

    def add_quiz(self) -> None:
        print("\n새 퀴즈 등록")
        question = read_text("문제: ")
        choices = []
        for number in range(1, 5):
            choices.append(read_text(f"선택지 {number}: "))
        answer = read_number("정답 번호 (1-4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        print("퀴즈가 추가되었습니다.")

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