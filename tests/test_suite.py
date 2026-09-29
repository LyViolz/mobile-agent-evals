import unittest

from src.mobile_agent_evals.cli import summarize_suite, suite_markdown


class SuiteReportTests(unittest.TestCase):
    def test_mixed_outcomes_fail_the_suite_and_show_both_cases(self):
        result = summarize_suite("mobile-regressions", [
            {"task": "reminder", "passed": True, "baseline_was_failing": True, "candidate_now_passing": True},
            {"task": "restore", "passed": False, "baseline_was_failing": True, "candidate_now_passing": False},
        ])
        self.assertFalse(result["passed"])
        self.assertEqual((result["passed_count"], result["total_count"]), (1, 2))
        report = suite_markdown(result)
        self.assertIn("reminder | PASS", report)
        self.assertIn("restore | FAIL", report)

    def test_empty_suite_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            summarize_suite("empty", [])


if __name__ == "__main__":
    unittest.main()
