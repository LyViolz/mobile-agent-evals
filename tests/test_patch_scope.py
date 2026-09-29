import unittest

from src.mobile_agent_evals.cli import validate_patch


class PatchScopeTests(unittest.TestCase):
    def test_rejects_a_patch_that_edits_the_tests(self):
        patch = "diff --git a/test/check.dart b/test/check.dart\n--- a/test/check.dart\n+++ b/test/check.dart\n"
        with self.assertRaisesRegex(ValueError, "outside allowed_paths"):
            validate_patch(patch, ["lib/"])

    def test_rejects_parent_directory_escape(self):
        patch = "diff --git a/lib/../../outside b/lib/../../outside\n--- a/lib/../../outside\n+++ b/lib/../../outside\n"
        with self.assertRaisesRegex(ValueError, "Unsafe patch path"):
            validate_patch(patch, ["lib/"])


if __name__ == "__main__":
    unittest.main()
