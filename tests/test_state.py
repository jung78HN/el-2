from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from game import QuizGame
from quiz import Quiz


class StateTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.state = Path(directory.name) / "state.json"
        self.backup = self.state.with_suffix(".json.bak")
        output = patch("sys.stdout", new_callable=StringIO)
        output.start()
        self.addCleanup(output.stop)

    def test_missing_state_uses_five_default_quizzes(self):
        game = QuizGame(self.state)
        game.load()

        self.assertEqual(len(game.quizzes), 5)
        self.assertIsNone(game.best_score)
        self.assertFalse(self.state.exists())

    def test_corrupt_state_restores_previous_valid_snapshot(self):
        game = QuizGame(self.state)
        game.quizzes.append(Quiz("테스트 문제", ["가", "나", "다", "라"], 1))
        self.assertTrue(game.save())
        first_snapshot = self.state.read_bytes()

        game = QuizGame(self.state)
        game.load()
        game.best_score, game.best_correct, game.best_total = 100, 6, 6
        self.assertTrue(game.save())
        self.assertEqual(self.backup.read_bytes(), first_snapshot)

        self.state.write_bytes(b"{broken")
        restored = QuizGame(self.state)
        restored.load()
        self.assertEqual(len(restored.quizzes), 6)
        self.assertIsNone(restored.best_score)
        self.assertEqual(self.state.read_bytes(), first_snapshot)
        self.assertEqual(self.backup.read_bytes(), first_snapshot)

    def test_corrupt_state_and_backup_use_defaults(self):
        self.state.write_bytes(b"{broken")
        self.backup.write_bytes(b"[]")

        game = QuizGame(self.state)
        game.load()

        self.assertEqual(len(game.quizzes), 5)
        self.assertFalse(game.dirty)
        self.assertEqual(self.backup.read_bytes(), b"[]")
        self.assertIn(b'"quizzes"', self.state.read_bytes())

    def test_failed_replace_keeps_state_and_is_retried_at_exit(self):
        game = QuizGame(self.state)
        self.assertTrue(game.save())
        first_snapshot = self.state.read_bytes()
        replace = Path.replace
        attempts = 0

        def fail_first_state_replace(source, target):
            nonlocal attempts
            if target == self.state:
                attempts += 1
                if attempts == 1:
                    self.assertEqual(self.state.read_bytes(), first_snapshot)
                    raise PermissionError("잠긴 상태 파일")
            return replace(source, target)

        game = QuizGame(self.state)
        with patch.object(Path, "replace", fail_first_state_replace), patch(
            "builtins.input", side_effect=["2", "테스트 문제", "가", "나", "다", "라", "1", "5"]
        ):
            game.run()

        self.assertEqual(attempts, 2)
        self.assertEqual(self.backup.read_bytes(), first_snapshot)
        self.assertIn("테스트 문제", self.state.read_text(encoding="utf-8"))
        self.assertFalse(game.dirty)
        self.assertEqual(list(self.state.parent.glob("*.tmp")), [])
