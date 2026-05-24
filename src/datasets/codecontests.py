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
CodeContests dataset loader.

Loads the DeepMind CodeContests dataset from HuggingFace and filters to
Codeforces problems in the difficulty sweet spot for KalibrBench-CP.

Difficulty filter: 2000–2500 Codeforces rating (Div. 1 C/D problems).
Python filter: problems must have at least one Python reference solution.
Test case filter: must have at least one private test case for evaluation.
"""
from __future__ import annotations
from dataclasses import dataclass, field


DIFFICULTY_MIN = 2000
DIFFICULTY_MAX = 2500
MIN_PRIVATE_TESTS = 1


@dataclass
class CPProblem:
    problem_id: str
    name: str
    description: str
    difficulty: int
    public_tests: list[dict]   # [{"input": str, "output": str}]
    private_tests: list[dict]  # [{"input": str, "output": str}] — used for evaluation only
    time_limit: float          # seconds
    source: str


def _parse_tests(raw_tests: dict) -> list[dict]:
    inputs = raw_tests.get("input", []) or []
    outputs = raw_tests.get("output", []) or []
    return [{"input": i, "output": o} for i, o in zip(inputs, outputs)]


def _has_python_solution(problem: dict) -> bool:
    solutions = problem.get("solutions", {})
    languages = solutions.get("language", []) or []
    return 3 in languages  # 3 = Python3 in CodeContests language enum


def load_problems(
    n: int = 100,
    difficulty_min: int = DIFFICULTY_MIN,
    difficulty_max: int = DIFFICULTY_MAX,
    split: str = "valid",
) -> list[CPProblem]:
    """Load and filter CodeContests problems.

    Args:
        n: Maximum number of problems to return.
        difficulty_min: Minimum Codeforces difficulty rating.
        difficulty_max: Maximum Codeforces difficulty rating.
        split: Dataset split — 'train', 'valid', or 'test'. Default 'valid' for calibration; reserve 'test' for final benchmark evaluation.

    Returns:
        List of CPProblem objects ready for use in experiments.
    """
    from datasets import load_dataset

    print(f"Loading CodeContests ({split} split)...")
    ds = load_dataset("deepmind/code_contests", split=split, trust_remote_code=True)
    print(f"Loaded {len(ds)} problems. Filtering...")

    problems = []
    for row in ds:
        # Source filter: Codeforces only
        if row.get("source") != 3:  # 3 = CODEFORCES in the dataset enum
            continue

        # Difficulty filter
        difficulty = row.get("difficulty", 0) or 0
        if not (difficulty_min <= difficulty <= difficulty_max):
            continue

        # Python solution filter
        if not _has_python_solution(row):
            continue

        # Private test cases filter
        private = _parse_tests(row.get("private_tests", {}))
        if len(private) < MIN_PRIVATE_TESTS:
            continue

        public = _parse_tests(row.get("public_tests", {}))

        time_limit_raw = row.get("time_limit", None)
        if time_limit_raw and hasattr(time_limit_raw, "seconds"):
            time_limit = float(time_limit_raw.seconds)
        else:
            time_limit = 5.0  # default 5 second limit

        problems.append(CPProblem(
            problem_id=row.get("name", "unknown").replace(" ", "_").lower(),
            name=row.get("name", "unknown"),
            description=row.get("description", ""),
            difficulty=difficulty,
            public_tests=public,
            private_tests=private,
            time_limit=min(time_limit, 10.0),  # cap at 10s for sandbox
            source="codeforces",
        ))

        if len(problems) >= n:
            break

    print(f"Filtered to {len(problems)} problems in difficulty range {difficulty_min}–{difficulty_max}.")
    return problems


def format_prompt(problem: CPProblem) -> str:
    """Format a CPProblem into an agent prompt including public test cases."""
    public_examples = ""
    if problem.public_tests:
        examples = []
        for i, tc in enumerate(problem.public_tests[:3], 1):  # show max 3 examples
            examples.append(f"Example {i}:\nInput:\n{tc['input']}\nOutput:\n{tc['output']}")
        public_examples = "\n\n" + "\n\n".join(examples)

    return (
        f"Problem: {problem.name}\n"
        f"Difficulty: {problem.difficulty} (Codeforces rating)\n"
        f"Time limit: {problem.time_limit} seconds\n\n"
        f"{problem.description}"
        f"{public_examples}\n\n"
        f"Output a complete Python solution. "
        f"Wrap your final solution in a ```python code block."
    )
