# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Local subprocess executor — drop-in replacement for the Judge0 API wrapper.

Runs Python code in a subprocess with wall-time timeout and output comparison.
Same public interface as the original Judge0 wrapper; all callers unchanged.

Status IDs (mirrors Judge0 CE convention):
    3  = Accepted
    4  = Wrong Answer
    5  = Time Limit Exceeded
    6  = Compilation Error  (SyntaxError / IndentationError / TabError)
    11 = Runtime Error
   -1  = Internal / unexpected exception
"""
from __future__ import annotations
import os
import subprocess
import sys
import tempfile


_COMPILATION_ERRORS = ("SyntaxError", "IndentationError", "TabError")

COMPILATION_ERROR_ID = 6
ACCEPTED_ID          = 3


def run_test_case(code: str, stdin: str, expected_output: str, time_limit: float = 5.0) -> dict:
    """Run code against a single test case. Returns result dict."""
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp = f.name

        result = subprocess.run(
            [sys.executable, tmp],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=time_limit + 2,
        )

        stdout = result.stdout
        stderr = result.stderr

        compilation_error = result.returncode != 0 and any(
            e in stderr for e in _COMPILATION_ERRORS
        )

        if result.returncode == 0:
            passed    = stdout.strip() == expected_output.strip()
            status_id = ACCEPTED_ID if passed else 4
        elif compilation_error:
            passed    = False
            status_id = COMPILATION_ERROR_ID
        else:
            passed    = False
            status_id = 11

        return {
            "passed":            passed,
            "status_id":         status_id,
            "compilation_error": compilation_error,
            "stdout":            stdout,
            "stderr":            stderr,
            "time":              None,
        }

    except subprocess.TimeoutExpired:
        return {
            "passed":            False,
            "status_id":         5,
            "compilation_error": False,
            "stdout":            "",
            "stderr":            "Time limit exceeded",
            "time":              None,
        }
    except Exception as e:
        return {"passed": False, "status_id": -1, "error": str(e), "compilation_error": False}
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def evaluate(
    code: str,
    test_cases: list[dict],
    time_limit: float = 5.0,
    max_test_cases: int = 20,
) -> dict:
    """Run code against all test cases. Returns aggregated result."""
    if not code or not code.strip():
        return {
            "passed":            False,
            "compilation_error": False,
            "tests_passed":      0,
            "tests_total":       len(test_cases),
            "pass_rate":         0.0,
        }

    cases   = test_cases[:max_test_cases]
    results = []

    for tc in cases:
        r = run_test_case(code, tc["input"], tc["output"], time_limit)
        results.append(r)
        if r.get("compilation_error"):
            break

    compilation_error = any(r.get("compilation_error") for r in results)
    tests_passed      = sum(1 for r in results if r.get("passed"))
    tests_total       = len(cases)

    return {
        "passed":            tests_passed == tests_total and tests_total > 0,
        "compilation_error": compilation_error,
        "tests_passed":      tests_passed,
        "tests_total":       tests_total,
        "pass_rate":         tests_passed / tests_total if tests_total > 0 else 0.0,
    }


def health_check() -> bool:
    """Always returns True — no external service required."""
    return True
