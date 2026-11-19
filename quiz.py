class Quiz:
    """문제 하나와 네 개의 선택지를 관리한다."""

    def __init__(self, question: str, choices: list[str], answer: int):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 비어 있지 않은 문자열이어야 합니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 정확히 네 개여야 합니다.")
        if any(not isinstance(choice, str) or not choice.strip() for choice in choices):
            raise ValueError("선택지는 비어 있지 않은 문자열이어야 합니다.")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답 번호는 1~4 사이의 정수여야 합니다.")

        self.question = question
        self.choices = choices.copy()
        self.answer = answer

    def display(self, number: int) -> None:
        print(f"\n[문제 {number}] {self.question}")
        for index, choice in enumerate(self.choices, start=1):
            print(f"  {index}. {choice}")

    def is_correct(self, guess: int) -> bool:
        return guess == self.answer