# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""HumanEval benchmark problems for Phase 6 objective benchmarks.

Each problem is a Python function to complete. Scoring is deterministic:
execute the test suite, return pass (1) or fail (0). No LLM judge.
"""
from __future__ import annotations
import random
import re
import subprocess
import tempfile
import os
from dataclasses import dataclass


@dataclass
class HumanEvalProblem:
    task_id: str
    prompt: str         # function signature + docstring
    entry_point: str    # function name to call in tests
    test: str           # test code defining check(candidate)
    canonical_solution: str

    @property
    def brief(self) -> str:
        return (
            "Complete the following Python function. "
            "Your response MUST contain a complete, runnable Python function definition.\n\n"
            f"{self.prompt}"
        )


def load_problems(n: int = 50, seed: int = 42) -> list[HumanEvalProblem]:
    from datasets import load_dataset
    ds = load_dataset("openai/openai_humaneval", split="test")
    problems = [
        HumanEvalProblem(
            task_id=p["task_id"],
            prompt=p["prompt"],
            entry_point=p["entry_point"],
            test=p["test"],
            canonical_solution=p["canonical_solution"],
        )
        for p in ds
    ]
    rng = random.Random(seed)
    rng.shuffle(problems)
    return problems[:n]


def extract_code(text: str, entry_point: str) -> str | None:
    """Extract Python function from agent output. Returns None if not found."""
    # Try ```python ... ``` blocks first — take last block containing the function
    blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    if not blocks:
        blocks = re.findall(r"```\n(.*?)```", text, re.DOTALL)
    for block in reversed(blocks):
        if f"def {entry_point}" in block:
            return block.strip()
    if blocks:
        return blocks[-1].strip()

    # Fall back to extracting function definition directly from text
    lines = text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"\s*def {re.escape(entry_point)}\s*\(", line):
            start = i
            break
    if start is None:
        return None

    result = []
    base_indent = len(lines[start]) - len(lines[start].lstrip())
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            result.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        if result and indent <= base_indent and stripped and not stripped.startswith("#"):
            # Hit a new top-level definition — stop
            if stripped.startswith("def ") or stripped.startswith("class "):
                break
        result.append(line)
    return "\n".join(result).strip() if result else None


def check_solution(solution_code: str, problem: HumanEvalProblem, timeout: int = 10) -> bool:
    """Execute solution against the problem's test suite. Returns True iff all tests pass."""
    if not solution_code or not solution_code.strip():
        return False

    full_code = f"{solution_code}\n\n{problem.test}\n\ncheck({problem.entry_point})\n"

    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write(full_code)
        tmp_path = f.name

    try:
        import sys as _sys
        result = subprocess.run(
            [_sys.executable, tmp_path],  # sys.executable ensures correct Python version
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
