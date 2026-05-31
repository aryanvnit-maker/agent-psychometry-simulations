# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""GSM8K benchmark problems for Phase 6 objective benchmarks.

Each problem is a grade-school math word problem. Scoring is deterministic:
exact match on the final numerical answer. No LLM judge.
"""
from __future__ import annotations
import random
import re
from dataclasses import dataclass


@dataclass
class GSM8KProblem:
    problem_id: str
    question: str
    answer_text: str    # full reasoning + "#### N"
    answer_value: str   # just the number

    @property
    def brief(self) -> str:
        return (
            "Solve the following math problem step by step.\n\n"
            f"{self.question}\n\n"
            "Show your reasoning. End your final response with:\n"
            "#### [number]\n"
            "where [number] is your numerical answer (digits only, no units, no commas)."
        )


def _parse_answer(text: str) -> str:
    m = re.search(r"####\s*([\d,.-]+)", text)
    if m:
        return m.group(1).replace(",", "").strip()
    return ""


def load_problems(n: int = 100, seed: int = 42) -> list[GSM8KProblem]:
    from datasets import load_dataset
    ds = load_dataset("openai/gsm8k", "main", split="test")
    problems = []
    for i, p in enumerate(ds):
        ans = _parse_answer(p["answer"])
        if ans:
            problems.append(GSM8KProblem(
                problem_id=f"gsm8k_{i:04d}",
                question=p["question"],
                answer_text=p["answer"],
                answer_value=ans,
            ))
    rng = random.Random(seed)
    rng.shuffle(problems)
    return problems[:n]


def extract_answer(text: str) -> str:
    """Extract final numerical answer from agent output."""
    # Preferred: #### N format
    m = re.search(r"####\s*([\d,.-]+)", text)
    if m:
        return m.group(1).replace(",", "").strip()

    # "The answer is N" / "Answer: N"
    m = re.search(r"(?:[Tt]he\s+)?[Aa]nswer\s*(?:is\s*)?[:\s]\$?\s*([\d,.-]+)", text)
    if m:
        return m.group(1).replace(",", "").strip()

    # Last standalone number in the text
    numbers = re.findall(r"\b\d+(?:\.\d+)?\b", text)
    return numbers[-1] if numbers else ""


def answers_match(predicted: str, ground_truth: str) -> bool:
    """Compare two answer strings numerically when possible."""
    try:
        return abs(float(predicted) - float(ground_truth)) < 1e-6
    except (ValueError, TypeError):
        return predicted.strip() == ground_truth.strip()
