#!/usr/bin/env python3
"""
Quick smoke test for Phase 9 — one call per condition, no judge scoring.
Run this before the full experiment to confirm API keys and model names work.

Usage:
    python phases/phase9/test_connections.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

TASK = "A startup has $500k left. They can extend runway 12 months by cutting the sales team, or burn it in 6 months going all-in on growth. What should they do?"

def test_kalibr_chain():
    print("── Test 1: kalibr-chain (grok-4.20-0309-reasoning, 2 calls) ──")
    from kalibr import chain
    try:
        result = chain(task=TASK)
        print(f"  ✓ Output ({len(result.output)} chars):")
        print(f"  {result.output[:300]}...")
        print(f"  Turns: {result.turn_count} | Tokens: {sum(result.token_usage.values())}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback; traceback.print_exc()

def test_grok_panel():
    print("\n── Test 2: grok-panel (grok-4.20-multi-agent-0309, 1 API call) ──")
    from openai import OpenAI
    panel_model = os.getenv("GROK_PANEL_MODEL", "grok-4.20-multi-agent-0309")
    api_key     = os.getenv("XAI_API_KEY")
    if not api_key:
        print("  ✗ FAILED: XAI_API_KEY not set")
        return
    try:
        client   = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        response = client.responses.create(
            model=panel_model,
            input=[{"role": "user", "content": TASK}],
            temperature=0.0,
        )
        output = response.output_text or ""
        print(f"  ✓ Output ({len(output)} chars):")
        print(f"  {output[:300]}...")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    provider = os.getenv("MODEL_PROVIDER", "gemini")
    model    = os.getenv("MODEL", "gemini-2.5-flash")
    panel    = os.getenv("GROK_PANEL_MODEL", "grok-4.20-multi-agent-0309")
    print(f"MODEL_PROVIDER : {provider}")
    print(f"MODEL          : {model}")
    print(f"GROK_PANEL_MODEL: {panel}")
    print(f"XAI_API_KEY    : {'set' if os.getenv('XAI_API_KEY') else 'NOT SET'}")
    print()
    test_kalibr_chain()
    test_grok_panel()
    print("\nIf both show ✓, run the full experiment:")
    print("  python phases/phase9/run_phase9.py --reps 10")
