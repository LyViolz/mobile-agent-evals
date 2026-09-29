# Mobile Agent Evals project notes

- The project is a local Python CLI with a minimal Flutter fixture. It evaluates patches; it does not generate them or call an LLM.
- Run the example with `python3 -m src.mobile_agent_evals evaluate --task examples/weekly_reminder.json --patch examples/patches/weekly_reminder_fix.patch --output-dir reports/weekly-reminder`.
- Run the complete sample suite with `python3 -m src.mobile_agent_evals suite --manifest examples/suite.json --output-dir reports/mobile-regressions`.
- Run the Python checks with `python3 -m unittest discover -s tests`.
- Keep patch evaluation inside temporary fixture copies. Do not alter real product repositories from this harness.
- The sample's baseline tests intentionally fail; the patched candidate should pass Flutter tests and analysis.
