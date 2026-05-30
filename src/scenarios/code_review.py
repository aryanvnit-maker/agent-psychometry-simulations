# Copyright (C) 2026 Aryan Shah
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
Code review scenarios for Phase B (real-world task coverage extension).

Each scenario presents a Python code diff with exactly 3 planted bugs.
Rubrics are scored against whether each specific bug was identified,
making evaluation close to objective (judge model checks named bug presence).

Bug taxonomy per scenario:
  - Bug A: Security / data-correctness (critical)
  - Bug B: Logic / algorithmic (moderate)
  - Bug C: Edge case / failure mode (subtle)

These are real-world bug patterns, not competitive programming puzzles.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CodeReviewScenario:
    scenario_id: str
    category: str
    brief: str     # code diff + task context injected as first message
    rubric: str    # binary per-bug rubric (30+30+20+20 = 100)
    planted_bugs: list[str]  # ground truth list for post-hoc verification


# ── CR01: Authentication Middleware ─────────────────────────────────────────
# Bug A: SQL injection in login query
# Bug B: Token expiry check uses wrong comparison (>= instead of >)
# Bug C: Missing rate limit check on failed attempts

CR01_AUTH = CodeReviewScenario(
    scenario_id="cr01_auth_middleware",
    category="security",
    brief=(
        "Review the following authentication middleware for a web API. "
        "The PR description says: 'Add JWT token validation and user login endpoint.' "
        "Identify all bugs, security issues, and logic errors.\n\n"
        "```python\n"
        "import jwt\n"
        "import time\n"
        "import sqlite3\n"
        "\n"
        "SECRET = 'super-secret-key'\n"
        "\n"
        "def login(username: str, password: str, db_path: str) -> str | None:\n"
        "    conn = sqlite3.connect(db_path)\n"
        "    cursor = conn.cursor()\n"
        "    # Check credentials\n"
        "    query = f\"SELECT id FROM users WHERE username='{username}' AND password='{password}'\"\n"
        "    cursor.execute(query)\n"
        "    row = cursor.fetchone()\n"
        "    conn.close()\n"
        "    if row is None:\n"
        "        return None\n"
        "    token = jwt.encode(\n"
        "        {'user_id': row[0], 'exp': int(time.time()) + 3600},\n"
        "        SECRET, algorithm='HS256'\n"
        "    )\n"
        "    return token\n"
        "\n"
        "def verify_token(token: str) -> int | None:\n"
        "    try:\n"
        "        payload = jwt.decode(token, SECRET, algorithms=['HS256'])\n"
        "        if payload['exp'] >= int(time.time()):  # check not expired\n"
        "            return payload['user_id']\n"
        "        return None\n"
        "    except jwt.InvalidTokenError:\n"
        "        return None\n"
        "```\n"
    ),
    rubric=(
        "Score the review output on the following:\n"
        "1. Did the review identify the SQL injection vulnerability in the login query? "
        "The f-string interpolation of username and password directly into the SQL query "
        "allows injection attacks. The fix is parameterised queries. (30 points)\n"
        "2. Did the review identify the off-by-one in the token expiry check? "
        "The condition 'payload[exp] >= int(time.time())' returns valid for an expired token "
        "where exp == current time. It should be strictly greater-than (>). (30 points)\n"
        "3. Did the review identify the missing rate-limit or failed-login tracking? "
        "There is no protection against brute-force login attempts — repeated calls with "
        "wrong passwords face no throttling. (20 points)\n"
        "4. Was the review specific and actionable — did it name what to fix, not just "
        "flag vague 'security concerns'? (20 points)\n\n"
        "Maximum score: 100."
    ),
    planted_bugs=[
        "SQL injection via f-string in login query",
        "Off-by-one in token expiry: >= should be >",
        "No rate limiting on failed login attempts",
    ],
)


# ── CR02: Data Pipeline ──────────────────────────────────────────────────────
# Bug A: Silent data loss — StopIteration swallowed, returns partial results
# Bug B: Off-by-one in batch slicing (skips last batch)
# Bug C: Mutable default argument in function signature

CR02_PIPELINE = CodeReviewScenario(
    scenario_id="cr02_data_pipeline",
    category="data",
    brief=(
        "Review the following data pipeline that batches records for processing. "
        "PR description: 'Add batch processor for ETL pipeline.' "
        "Identify all bugs, data-correctness issues, and Python anti-patterns.\n\n"
        "```python\n"
        "from typing import Iterator\n"
        "\n"
        "def batch_records(\n"
        "    source: Iterator[dict],\n"
        "    batch_size: int = 100,\n"
        "    results: list = [],   # accumulate processed batches\n"
        ") -> list[list[dict]]:\n"
        "    batch: list[dict] = []\n"
        "    try:\n"
        "        while True:\n"
        "            record = next(source)\n"
        "            batch.append(record)\n"
        "            if len(batch) == batch_size:\n"
        "                results.append(batch)\n"
        "                batch = []\n"
        "    except StopIteration:\n"
        "        pass  # iterator exhausted — we're done\n"
        "    return results\n"
        "\n"
        "def process_all(source: Iterator[dict], batch_size: int = 100) -> int:\n"
        "    batches = batch_records(source, batch_size)\n"
        "    total = 0\n"
        "    for i in range(len(batches) - 1):  # process all batches\n"
        "        total += len(batches[i])\n"
        "    return total\n"
        "```\n"
    ),
    rubric=(
        "Score the review output on the following:\n"
        "1. Did the review identify the mutable default argument bug? "
        "'results: list = []' is evaluated once at function definition, not per call. "
        "Repeated calls accumulate into the same list. The fix is 'results=None' with "
        "'if results is None: results = []' inside the function. (30 points)\n"
        "2. Did the review identify the off-by-one in process_all? "
        "'range(len(batches) - 1)' skips the last batch, undercounting total records "
        "whenever the total count is not a multiple of batch_size. (30 points)\n"
        "3. Did the review identify that the final partial batch is silently dropped? "
        "When StopIteration is caught, the remaining 'batch' list (non-empty if total "
        "records is not a multiple of batch_size) is never appended to results. (20 points)\n"
        "4. Was the review specific and actionable — did it name line numbers or specific "
        "constructs, not just generic warnings? (20 points)\n\n"
        "Maximum score: 100."
    ),
    planted_bugs=[
        "Mutable default argument 'results: list = []'",
        "Off-by-one: range(len(batches) - 1) skips last batch",
        "Partial final batch silently dropped when StopIteration caught",
    ],
)


# ── CR03: API Rate Limiter ────────────────────────────────────────────────────
# Bug A: Race condition — check-then-act on shared counter without locking
# Bug B: Wrong time window (uses start time, not sliding window)
# Bug C: Missing cleanup — stale keys accumulate in memory forever

CR03_RATE_LIMITER = CodeReviewScenario(
    scenario_id="cr03_rate_limiter",
    category="concurrency",
    brief=(
        "Review the following in-memory rate limiter implementation. "
        "PR description: 'Add per-IP rate limiting: 100 requests per 60 seconds.' "
        "Identify all correctness issues, concurrency bugs, and resource leaks.\n\n"
        "```python\n"
        "import time\n"
        "from collections import defaultdict\n"
        "\n"
        "class RateLimiter:\n"
        "    def __init__(self, max_requests: int = 100, window_secs: int = 60):\n"
        "        self.max_requests = max_requests\n"
        "        self.window_secs  = window_secs\n"
        "        self.counters: dict[str, list[float]] = defaultdict(list)\n"
        "\n"
        "    def is_allowed(self, ip: str) -> bool:\n"
        "        now = time.time()\n"
        "        timestamps = self.counters[ip]\n"
        "        # Check if within window\n"
        "        if timestamps and now - timestamps[0] > self.window_secs:\n"
        "            self.counters[ip] = []   # reset — window has passed\n"
        "            timestamps = self.counters[ip]\n"
        "        if len(timestamps) >= self.max_requests:\n"
        "            return False\n"
        "        timestamps.append(now)\n"
        "        return True\n"
        "```\n"
    ),
    rubric=(
        "Score the review output on the following:\n"
        "1. Did the review identify the race condition? "
        "In a multi-threaded server, two concurrent requests for the same IP can both "
        "pass the 'len(timestamps) >= max_requests' check before either appends, "
        "allowing over-limit requests through. A lock (threading.Lock) per IP is required. (30 points)\n"
        "2. Did the review identify the broken window logic? "
        "The check 'now - timestamps[0] > window_secs' resets the counter only when the "
        "OLDEST request is outside the window, not when the window has fully elapsed. "
        "This is a fixed window starting from first request, not a sliding window. "
        "A sliding window keeps only timestamps within the last window_secs. (30 points)\n"
        "3. Did the review identify the memory leak? "
        "IPs that stop sending requests never have their counters cleaned up. "
        "Over time, self.counters accumulates stale entries for every IP that ever "
        "made a request. (20 points)\n"
        "4. Was the review specific and actionable? (20 points)\n\n"
        "Maximum score: 100."
    ),
    planted_bugs=[
        "Race condition: check-then-act without locking in concurrent context",
        "Fixed window from first request instead of sliding window",
        "Memory leak: stale IP counters never cleaned up",
    ],
)


# ── CR04: Payment Processing ──────────────────────────────────────────────────
# Bug A: Floating point used for money amounts (should use Decimal or integer cents)
# Bug B: No idempotency — duplicate payment if network retry occurs
# Bug C: Exception swallowed after charge — inventory not rolled back

CR04_PAYMENT = CodeReviewScenario(
    scenario_id="cr04_payment",
    category="financial",
    brief=(
        "Review the following payment processing function. "
        "PR description: 'Integrate Stripe charge with inventory update.' "
        "Identify all correctness issues, financial bugs, and failure modes.\n\n"
        "```python\n"
        "import stripe\n"
        "\n"
        "def process_payment(user_id: str, amount_usd: float, item_id: str, db) -> dict:\n"
        "    # Deduct inventory first\n"
        "    db.execute('UPDATE inventory SET qty = qty - 1 WHERE item_id = ?', [item_id])\n"
        "    db.commit()\n"
        "\n"
        "    # Charge the card\n"
        "    try:\n"
        "        charge = stripe.Charge.create(\n"
        "            amount=int(amount_usd * 100),  # convert to cents\n"
        "            currency='usd',\n"
        "            customer=user_id,\n"
        "        )\n"
        "        return {'status': 'ok', 'charge_id': charge.id}\n"
        "    except stripe.error.StripeError as e:\n"
        "        return {'status': 'error', 'message': str(e)}\n"
        "```\n"
    ),
    rubric=(
        "Score the review output on the following:\n"
        "1. Did the review identify the floating point money bug? "
        "Multiplying a float amount_usd by 100 can produce rounding errors "
        "(e.g. 0.1 + 0.2 == 0.30000000000000004). Money should be handled as integer cents "
        "throughout or use Python's Decimal type. (30 points)\n"
        "2. Did the review identify the missing idempotency key? "
        "Without an idempotency_key in the Stripe call, a network retry will create a "
        "duplicate charge. Stripe supports idempotency_key to prevent this. (30 points)\n"
        "3. Did the review identify the inventory/payment consistency bug? "
        "Inventory is decremented and committed BEFORE the charge. If the charge fails, "
        "inventory has been reduced but no payment collected, and there is no rollback. "
        "The correct pattern is: charge first, then decrement inventory on success. (20 points)\n"
        "4. Was the review specific and actionable? (20 points)\n\n"
        "Maximum score: 100."
    ),
    planted_bugs=[
        "Floating point for money: amount_usd * 100 can have rounding errors",
        "No idempotency key: retry causes duplicate charge",
        "Inventory decremented before charge: no rollback on payment failure",
    ],
)


# ── CR05: Cache Implementation ────────────────────────────────────────────────
# Bug A: Cache never invalidated on write — stale reads after update
# Bug B: Cache key collision — different args with same repr can map to same key
# Bug C: Unbounded cache growth — no max size, memory leak for long-running service

CR05_CACHE = CodeReviewScenario(
    scenario_id="cr05_cache",
    category="performance",
    brief=(
        "Review the following function-level cache implementation used in a long-running service. "
        "PR description: 'Add memoization layer for expensive DB lookups.' "
        "Identify all correctness issues, cache bugs, and production concerns.\n\n"
        "```python\n"
        "import hashlib\n"
        "import json\n"
        "\n"
        "_cache: dict[str, object] = {}\n"
        "\n"
        "def cache_key(*args, **kwargs) -> str:\n"
        "    raw = json.dumps({'args': args, 'kwargs': kwargs})\n"
        "    return hashlib.md5(raw.encode()).hexdigest()\n"
        "\n"
        "def get_user(user_id: int, include_deleted: bool = False) -> dict | None:\n"
        "    key = cache_key(user_id, include_deleted)\n"
        "    if key in _cache:\n"
        "        return _cache[key]\n"
        "    result = db.query('SELECT * FROM users WHERE id = ?', [user_id])\n"
        "    _cache[key] = result\n"
        "    return result\n"
        "\n"
        "def update_user(user_id: int, data: dict) -> None:\n"
        "    db.execute('UPDATE users SET ... WHERE id = ?', [user_id])\n"
        "    db.commit()\n"
        "    # cache will refresh on next read\n"
        "```\n"
    ),
    rubric=(
        "Score the review output on the following:\n"
        "1. Did the review identify the cache invalidation bug? "
        "update_user modifies the database but does not invalidate the cache entry. "
        "The comment 'cache will refresh on next read' is incorrect — the cached value "
        "is returned indefinitely until process restart. The fix is to delete or update "
        "the cache key in update_user. (30 points)\n"
        "2. Did the review identify the potential cache key collision? "
        "json.dumps({'args': (1, 2), 'kwargs': {}}) == json.dumps({'args': [1, 2], 'kwargs': {}}) "
        "is False, but args with identical JSON representations (e.g. True vs 1 in some contexts, "
        "or different dict ordering) can collide. MD5 of JSON is fragile as a cache key "
        "for structured data. (30 points)\n"
        "3. Did the review identify the unbounded cache growth? "
        "_cache is a module-level dict with no max size, no TTL, and no eviction policy. "
        "In a long-running service serving many distinct user_ids, this is a memory leak. "
        "LRU cache (functools.lru_cache or cachetools.LRUCache) with a size limit is needed. (20 points)\n"
        "4. Was the review specific and actionable? (20 points)\n\n"
        "Maximum score: 100."
    ),
    planted_bugs=[
        "Cache not invalidated on write — stale reads after update_user",
        "Cache key via MD5(JSON) is fragile and can have collisions",
        "Unbounded cache growth — no max size or eviction policy",
    ],
)


ALL_CODE_REVIEW_SCENARIOS: dict[str, CodeReviewScenario] = {
    s.scenario_id: s for s in [
        CR01_AUTH,
        CR02_PIPELINE,
        CR03_RATE_LIMITER,
        CR04_PAYMENT,
        CR05_CACHE,
    ]
}
