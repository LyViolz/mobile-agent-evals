# Mobile Agent Evals

A small, reproducible harness for checking AI-generated Flutter fixes. It runs the same tests before and after a candidate patch in a temporary copy, checks that the patch stays in the allowed source area, and writes a machine-readable report. The included weekly reminder task demonstrates a real mobile edge case: scheduling after today's reminder time.

This project evaluates a patch produced by any coding agent. It does not call an LLM or require an API key.

## Run the sample

Requires Python 3.11+, Flutter and Git on `PATH`.

```sh
python3 -m src.mobile_agent_evals evaluate \
  --task examples/weekly_reminder.json \
  --patch examples/patches/weekly_reminder_fix.patch \
  --output-dir reports/weekly-reminder
```

The report records baseline and patched test/analyzer exit codes, duration, and a short log. A successful result means the patch fixed at least one failing baseline check and all patched checks pass. Open `reports/weekly-reminder/report.md` for a reviewable summary.

To evaluate a different Flutter task, create a fixture directory and a JSON task file with `fixture`, `allowed_paths`, and `checks`. Keep tests in the fixture and limit `allowed_paths` to implementation files. The harness copies the fixture to a temporary directory, runs `flutter pub get`, then executes the checks in order. Commands are local code execution; run only fixtures and patches you trust.

## Scope

The sample proves the evaluator's loop on one deterministic scheduling bug. It is not a claim that an AI agent solved the sample or that the tool validates every mobile behavior. Real applications still need device and integration testing.
