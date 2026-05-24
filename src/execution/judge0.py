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
Judge0 self-hosted API wrapper.

Submits code + test cases to the local Judge0 instance and returns
structured pass/fail results. Judge0 must be running at JUDGE0_URL
(default: http://localhost:2358).

Status IDs (Judge0 CE):
    1  = In Queue
    2  = Processing
    3  = Accepted
    4  = Wrong Answer
    5  = Time Limit Exceeded
    6  = Compilation Error
    7  = Runtime Error (SIGSEGV)
    11 = Runtime Error (other)
    13 = Internal Error
"""
from __future__ import annotations
import base64
import os
import time
import requests

JUDGE0_URL   = os.getenv("JUDGE0_URL", "http://localhost:2358")
PYTHON_LANG  = 71   # Python 3.8 in Judge0 CE
POLL_INTERVAL = 0.5  # seconds between status checks
MAX_POLLS     = 30   # 15 seconds max wait per submission

COMPILATION_ERROR_ID = 6
ACCEPTED_ID          = 3


def _encode(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def _decode(s: str | None) -> str:
    if not s:
        return ""
    return base64.b64decode(s).decode(errors="replace")


def _submit(code: str, stdin: str, time_limit: float) -> dict:
    payload = {
        "source_code": _encode(code),
        "language_id": PYTHON_LANG,
        "stdin":        _encode(stdin),
        "cpu_time_limit": time_limit,
        "wall_time_limit": time_limit + 2,
        "base64_encoded": True,
    }
    resp = requests.post(
        f"{JUDGE0_URL}/submissions?base64_encoded=true&wait=false",
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _poll(token: str) -> dict:
    for _ in range(MAX_POLLS):
        resp = requests.get(
            f"{JUDGE0_URL}/submissions/{token}?base64_encoded=true&fields=status_id,stdout,stderr,compile_output,time,memory",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        status_id = data.get("status_id", 0)
        if status_id not in (1, 2):  # not queued or processing
            return data
        time.sleep(POLL_INTERVAL)
    return {"status_id": 13, "stdout": None, "stderr": None, "compile_output": None}


def run_test_case(code: str, stdin: str, expected_output: str, time_limit: float = 5.0) -> dict:
    """Run code against a single test case. Returns result dict."""
    try:
        submission = _submit(code, stdin, time_limit)
        token = submission.get("token")
        if not token:
            return {"passed": False, "status_id": 13, "error": "No token returned"}

        result = _poll(token)
        status_id = result.get("status_id", 0)

        stdout = _decode(result.get("stdout"))
        stderr = _decode(result.get("stderr"))
        compile_output = _decode(result.get("compile_output"))

        passed = (
            status_id == ACCEPTED_ID
            and stdout.strip() == expected_output.strip()
        )

        return {
            "passed":            passed,
            "status_id":         status_id,
            "compilation_error": status_id == COMPILATION_ERROR_ID,
            "stdout":            stdout,
            "stderr":            stderr or compile_output,
            "time":              result.get("time"),
        }
    except Exception as e:
        return {"passed": False, "status_id": -1, "error": str(e), "compilation_error": False}


def evaluate(
    code: str,
    test_cases: list[dict],
    time_limit: float = 5.0,
    max_test_cases: int = 20,
) -> dict:
    """Run code against all test cases. Returns aggregated result.

    Args:
        code: Python source code string.
        test_cases: List of {"input": str, "output": str} dicts.
        time_limit: Per-test-case CPU time limit in seconds.
        max_test_cases: Cap to avoid excessive API calls on large test suites.

    Returns:
        {
            "passed": bool,           # all test cases passed
            "compilation_error": bool,
            "tests_passed": int,
            "tests_total": int,
            "pass_rate": float,
        }
    """
    if not code or not code.strip():
        return {
            "passed": False,
            "compilation_error": False,
            "tests_passed": 0,
            "tests_total": len(test_cases),
            "pass_rate": 0.0,
        }

    cases = test_cases[:max_test_cases]
    results = []

    for tc in cases:
        r = run_test_case(code, tc["input"], tc["output"], time_limit)
        results.append(r)
        # Short-circuit on compilation error — all subsequent cases will also fail
        if r.get("compilation_error"):
            break

    compilation_error = any(r.get("compilation_error") for r in results)
    tests_passed = sum(1 for r in results if r.get("passed"))
    tests_total = len(cases)

    return {
        "passed":            tests_passed == tests_total and tests_total > 0,
        "compilation_error": compilation_error,
        "tests_passed":      tests_passed,
        "tests_total":       tests_total,
        "pass_rate":         tests_passed / tests_total if tests_total > 0 else 0.0,
    }


def health_check() -> bool:
    """Return True if Judge0 is reachable and responding."""
    try:
        resp = requests.get(f"{JUDGE0_URL}/system_info", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False
