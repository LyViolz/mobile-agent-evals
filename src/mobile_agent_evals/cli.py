"""Run reproducible baseline/patch checks for a Flutter coding task."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def run(command: list[str], cwd: Path, timeout: int) -> dict:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, timeout=timeout,
            check=False,
        )
        code = completed.returncode
        output = (completed.stdout + "\n" + completed.stderr).strip()
    except subprocess.TimeoutExpired as error:
        code = 124
        output = f"Timed out after {timeout}s: {error}"
    return {
        "command": command,
        "exit_code": code,
        "seconds": round(time.monotonic() - started, 2),
        "log_tail": output[-4000:],
    }


def touched_paths(patch_text: str) -> list[str]:
    paths = []
    for line in patch_text.splitlines():
        if line.startswith("diff --git a/"):
            parts = line.split(" ")
            if len(parts) != 4 or not parts[2].startswith("a/") or not parts[3].startswith("b/"):
                raise ValueError("Unsupported or malformed diff header")
            paths.extend([parts[2][2:], parts[3][2:]])
        if line.startswith("+++ b/"):
            paths.append(line[6:])
        elif line.startswith("--- a/"):
            paths.append(line[6:])
    return sorted(set(paths))


def validate_patch(patch_text: str, allowed_paths: list[str]) -> list[str]:
    paths = touched_paths(patch_text)
    if not paths:
        raise ValueError("Patch has no file changes")
    for path in paths:
        candidate = Path(path)
        if not path or candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"Unsafe patch path: {path}")
        if not any(path.startswith(prefix) for prefix in allowed_paths):
            raise ValueError(f"Patch path outside allowed_paths: {path}")
    return paths


def evaluate(task_path: Path, patch_path: Path) -> dict:
    task = json.loads(task_path.read_text(encoding="utf-8"))
    fixture = (task_path.parent / task["fixture"]).resolve()
    if not fixture.is_dir():
        raise ValueError(f"Fixture directory missing: {fixture}")
    checks = task["checks"]
    if not checks or not all(isinstance(check["command"], list) for check in checks):
        raise ValueError("checks must contain command arrays")
    patch = patch_path.read_text(encoding="utf-8")
    changed = validate_patch(patch, task["allowed_paths"])
    timeout = int(task.get("timeout_seconds", 180))

    with tempfile.TemporaryDirectory(prefix="mobile-agent-eval-") as directory:
        workspace = Path(directory) / "workspace"
        shutil.copytree(fixture, workspace, ignore=shutil.ignore_patterns(".dart_tool", "build"))
        setup = run(["flutter", "pub", "get"], workspace, timeout)
        if setup["exit_code"]:
            return {"task": task["id"], "passed": False, "setup": setup, "changed_paths": changed}

        baseline = {check["name"]: run(check["command"], workspace, timeout) for check in checks}
        apply_check = run(["git", "apply", "--check", str(patch_path.resolve())], workspace, timeout)
        if apply_check["exit_code"]:
            return {
                "task": task["id"], "passed": False, "setup": setup,
                "baseline": baseline, "apply_check": apply_check, "changed_paths": changed,
            }
        applied = run(["git", "apply", str(patch_path.resolve())], workspace, timeout)
        if applied["exit_code"]:
            return {
                "task": task["id"], "passed": False, "setup": setup,
                "baseline": baseline, "applied": applied, "changed_paths": changed,
            }
        candidate = {check["name"]: run(check["command"], workspace, timeout) for check in checks}
        was_failing = any(result["exit_code"] != 0 for result in baseline.values())
        now_passing = all(result["exit_code"] == 0 for result in candidate.values())
        return {
            "task": task["id"], "passed": was_failing and now_passing,
            "baseline_was_failing": was_failing, "candidate_now_passing": now_passing,
            "changed_paths": changed, "setup": setup, "baseline": baseline,
            "candidate": candidate,
        }


def report_markdown(result: dict) -> str:
    lines = [f"# {result['task']}", "", f"Result: {'PASS' if result['passed'] else 'FAIL'}", ""]
    lines.append("Changed paths: " + ", ".join(result["changed_paths"]))
    lines.append("")
    for stage in ("baseline", "candidate"):
        if stage not in result:
            continue
        lines.extend([f"## {stage.title()}", ""])
        for name, check in result[stage].items():
            lines.append(f"- {name}: exit {check['exit_code']}, {check['seconds']}s")
        lines.append("")
    return "\n".join(lines)


def summarize_suite(suite_id: str, results: list[dict]) -> dict:
    if not results:
        raise ValueError("Suite must contain at least one case")
    passed_count = sum(bool(result["passed"]) for result in results)
    return {
        "suite": suite_id,
        "passed": passed_count == len(results),
        "passed_count": passed_count,
        "total_count": len(results),
        "cases": results,
    }


def suite_markdown(result: dict) -> str:
    lines = [f"# {result['suite']}", "", f"Result: {result['passed_count']}/{result['total_count']} passed", "", "| Task | Result | Baseline failing | Candidate passing |", "| --- | --- | --- | --- |"]
    for case in result["cases"]:
        lines.append(
            f"| {case['task']} | {'PASS' if case['passed'] else 'FAIL'} | "
            f"{case.get('baseline_was_failing', False)} | {case.get('candidate_now_passing', False)} |"
        )
    return "\n".join(lines) + "\n"


def write_report(output_dir: Path, result: dict, markdown: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (output_dir / "report.md").write_text(markdown, encoding="utf-8")


def evaluate_suite(suite_path: Path) -> dict:
    manifest = json.loads(suite_path.read_text(encoding="utf-8"))
    cases = manifest["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("Suite must contain a non-empty cases array")
    results = []
    for case in cases:
        task_path = (suite_path.parent / case["task"]).resolve()
        patch_path = (suite_path.parent / case["patch"]).resolve()
        results.append(evaluate(task_path, patch_path))
    return summarize_suite(manifest["id"], results)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    eval_parser = subparsers.add_parser("evaluate")
    eval_parser.add_argument("--task", type=Path, required=True)
    eval_parser.add_argument("--patch", type=Path, required=True)
    eval_parser.add_argument("--output-dir", type=Path, required=True)
    suite_parser = subparsers.add_parser("suite")
    suite_parser.add_argument("--manifest", type=Path, required=True)
    suite_parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "evaluate":
        try:
            result = evaluate(args.task.resolve(), args.patch.resolve())
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            parser.error(str(error))
        write_report(args.output_dir, result, report_markdown(result))
        print(args.output_dir / "report.md")
        return 0 if result["passed"] else 1
    if args.command == "suite":
        try:
            result = evaluate_suite(args.manifest.resolve())
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            parser.error(str(error))
        write_report(args.output_dir, result, suite_markdown(result))
        print(args.output_dir / "report.md")
        return 0 if result["passed"] else 1
    return 2
