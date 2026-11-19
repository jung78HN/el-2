from questions import default_quizzes


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


class QuizGame:
    """메뉴와 퀴즈 게임의 진행을 관리한다."""

    def __init__(self):
        self.quizzes = default_quizzes()

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

                print("이 메뉴는 준비 중입니다.")
        except (KeyboardInterrupt, EOFError):
            print("\n입력이 중단되었습니다.")
        print("태양계 퀴즈를 종료합니다.")


if __name__ == "__main__":
    QuizGame().run()