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
Judge0 smoke test — run this to verify Judge0 can actually execute code.

Usage:
    python judge0_smoke_test.py
"""
import base64
import time
import requests

JUDGE0_URL = "http://localhost:2358"
PYTHON_LANG = 71  # Python 3.8

CODE = "print(42)\n"
STDIN = ""
EXPECTED = "42"


def enc(s):
    return base64.b64encode(s.encode()).decode()


def main():
    print(f"Judge0 URL: {JUDGE0_URL}")

    # 1. Health check
    print("\n1. Health check (/system_info)...")
    try:
        r = requests.get(f"{JUDGE0_URL}/system_info", timeout=5)
        print(f"   status={r.status_code}")
        if r.status_code == 200:
            info = r.json()
            print(f"   Judge0 version: {info.get('judge0_version', 'unknown')}")
    except Exception as e:
        print(f"   FAILED: {e}")
        return

    # 2. List languages to confirm Python 71 exists
    print("\n2. Languages check (/languages/71)...")
    try:
        r = requests.get(f"{JUDGE0_URL}/languages/71", timeout=5)
        print(f"   status={r.status_code}  body={r.text[:200]}")
    except Exception as e:
        print(f"   FAILED: {e}")

    # 3. Submit print(42)
    print(f"\n3. Submitting: {CODE!r}")
    payload = {
        "source_code":    enc(CODE),
        "language_id":    PYTHON_LANG,
        "stdin":          enc(STDIN),
        "cpu_time_limit": 5,
        "wall_time_limit": 7,
        "base64_encoded": True,
    }
    try:
        r = requests.post(
            f"{JUDGE0_URL}/submissions?base64_encoded=true&wait=false",
            json=payload,
            timeout=10,
        )
        print(f"   POST status={r.status_code}")
        print(f"   POST body={r.text[:500]}")
        if r.status_code not in (200, 201):
            print("   FAILED — Judge0 rejected submission")
            return
        token = r.json().get("token")
        if not token:
            print("   FAILED — no token in response")
            return
    except Exception as e:
        print(f"   FAILED: {e}")
        return

    # 4. Poll for result
    print(f"\n4. Polling token={token}...")
    for attempt in range(20):
        time.sleep(0.5)
        try:
            r = requests.get(
                f"{JUDGE0_URL}/submissions/{token}?base64_encoded=true"
                f"&fields=status_id,stdout,stderr,compile_output,time,memory",
                timeout=10,
            )
            data = r.json()
            status_id = data.get("status_id", 0)
            print(f"   attempt {attempt+1}: status_id={status_id}")
            if status_id not in (1, 2):
                stdout = base64.b64decode(data.get("stdout") or "").decode(errors="replace")
                stderr = base64.b64decode(data.get("stderr") or "").decode(errors="replace")
                co = base64.b64decode(data.get("compile_output") or "").decode(errors="replace")
                print(f"   stdout={stdout!r}")
                print(f"   stderr={stderr!r}")
                print(f"   compile_output={co!r}")
                if status_id == 3 and stdout.strip() == EXPECTED:
                    print("\n   PASS — Judge0 is working correctly")
                else:
                    print(f"\n   UNEXPECTED result (status={status_id}, expected stdout={EXPECTED!r})")
                return
        except Exception as e:
            print(f"   poll error: {e}")

    print("   TIMEOUT — submission never completed")


if __name__ == "__main__":
    main()
