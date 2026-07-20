#!/usr/bin/env python3
# Copyright (c) 2026 Aryan Shah
#
# Part of the FLF Epistemic Case Study Competition submission (the epistemic-
# assessment layer). Licensed under the MIT License: see LICENSE-FLF-CODE and
# SUBMISSION_MANIFEST.md. This file is NOT part of the proprietary Kalibr
# engine, which is governed by LICENSE.

"""
Phase E — Ingestion Layer: URL or file → structured claims JSON.

First step in the FLF epistemic pipeline:
    Ingestion → Structure → Assessment

Fetches an article (e.g., ACX post, LessWrong, academic preprint) and
extracts attributed factual claims as structured JSON.

Output:
    {
        "source_url":   "<url>",
        "source_title": "<title>",
        "fetched_at":   "<ISO timestamp>",
        "claims": [
            {
                "claim": "<specific falsifiable claim>",
                "claim_type": "empirical | mechanistic | probabilistic | normative",
                "attributed_to": "<author, study, or institution>",
                "confidence_expressed": "high | medium | low | none",
                "quote": "<verbatim supporting quote, max 100 words>"
            }
        ]
    }

Usage:
    python phases/phase_e/ingest.py --url <article_url>
    python phases/phase_e/ingest.py --url <url> --out results/claims_covid_v1.json
    python phases/phase_e/ingest.py --file local_article.txt --source-title "My Article"

Requirements:
    pip install requests   (for URL fetching)
    GEMINI_API_KEY or ANTHROPIC_API_KEY in .env
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(override=True)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


CLAIMS_SCHEMA = """{
  "source_url": "<url>",
  "source_title": "<title>",
  "fetched_at": "<ISO 8601 timestamp>",
  "claims": [
    {
      "claim": "<specific falsifiable claim — one sentence>",
      "claim_type": "empirical | mechanistic | probabilistic | normative",
      "attributed_to": "<author, study name, or institution cited>",
      "confidence_expressed": "high | medium | low | none",
      "quote": "<verbatim supporting quote, max 100 words>"
    }
  ]
}"""

EXTRACTION_PROMPT = """\
You are an epistemic claim extractor. Identify all specific factual claims in
the article below and return them as a structured JSON object.

Rules:
- Extract CLAIMS only — not opinions, recommendations, or rhetorical questions
- Each claim must be a single falsifiable sentence
- claim_type: empirical (observed facts/data), mechanistic (causal mechanisms),
  probabilistic (probabilities/likelihoods), normative (what is correct/preferable)
- attributed_to: who makes or cites this claim (author name, study, institution)
- confidence_expressed: the confidence the SOURCE expresses, not yours
- quote: 1-2 verbatim sentences that support the claim extraction

Output format:
{schema}

ARTICLE SOURCE: {url}
ARTICLE TITLE: {title}

ARTICLE CONTENT:
{content}

Output ONLY the JSON — no prose before or after.
"""

MAX_CONTENT_CHARS = 12_000


def _strip_html(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>",  " ", text,  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"')
    return re.sub(r"\s+", " ", text).strip()


def _extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else "Unknown"


def fetch_content(url: str) -> tuple[str, str]:
    if not _REQUESTS_AVAILABLE:
        raise ImportError("requests not installed. Run: pip install requests")
    resp = requests.get(url, timeout=15, headers={"User-Agent": "epistemic-ingest/1.0"})
    resp.raise_for_status()
    html  = resp.text
    title = _extract_title(html)
    text  = _strip_html(html)
    return text, title


def call_extraction_model(content: str, url: str, title: str) -> str:
    truncated = content[:MAX_CONTENT_CHARS]
    if len(content) > MAX_CONTENT_CHARS:
        truncated += f"\n\n[... truncated at {MAX_CONTENT_CHARS} chars ...]"

    prompt = EXTRACTION_PROMPT.format(
        schema=CLAIMS_SCHEMA, url=url, title=title, content=truncated,
    )

    provider = os.getenv("MODEL_PROVIDER", "gemini")

    if provider == "gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        model  = os.getenv("MODEL", "gemini-2.5-flash")
        resp   = client.models.generate_content(
            model=model,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=8192),
        )
        return resp.text or ""

    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        model  = os.getenv("MODEL", "claude-haiku-4-5-20251001")
        resp   = client.messages.create(
            model=model, max_tokens=8192,
            messages=[{"role": "user", "content": prompt}], temperature=0.0,
        )
        return resp.content[0].text if resp.content else ""

    elif provider in ("openai", "xai"):
        from openai import OpenAI
        client = (OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
                  if provider == "xai" else OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        model  = os.getenv("MODEL", "gpt-4o-mini")
        resp   = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
            temperature=0.0, max_tokens=8192,
        )
        return resp.choices[0].message.content or ""

    else:
        raise ValueError(f"Unknown MODEL_PROVIDER: {provider}")


def parse_claims_output(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in extraction output")
    return json.loads(text[start:end])


def ingest(
    url: str | None = None,
    file_path: Path | None = None,
    source_title: str | None = None,
    out: Path | None = None,
) -> dict:
    if file_path is not None:
        content = file_path.read_text()
        url     = url or f"file://{file_path.resolve()}"
        title   = source_title or file_path.stem
    elif url is not None:
        print(f"Fetching: {url}")
        content, title = fetch_content(url)
        if source_title:
            title = source_title
        print(f"Title:    {title}")
        print(f"Content:  {len(content)} chars → truncated to {MAX_CONTENT_CHARS}")
    else:
        raise ValueError("Provide --url or --file")

    print("Extracting claims...")
    raw    = call_extraction_model(content, url, title)
    result = parse_claims_output(raw)

    result["source_url"]   = url
    result["source_title"] = title
    result["fetched_at"]   = datetime.now(timezone.utc).isoformat()

    n_claims = len(result.get("claims", []))
    print(f"Extracted {n_claims} claims.")

    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2))
        print(f"Saved: {out}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Ingest article → structured claims JSON")
    parser.add_argument("--url",          type=str,  default=None)
    parser.add_argument("--file",         type=Path, default=None, dest="file_path")
    parser.add_argument("--source-title", type=str,  default=None)
    parser.add_argument("--out",          type=Path, default=None,
                        help="Output path (default: print to stdout)")
    args = parser.parse_args()

    if args.url is None and args.file_path is None:
        parser.error("Provide --url or --file")

    result = ingest(url=args.url, file_path=args.file_path,
                    source_title=args.source_title, out=args.out)
    if args.out is None:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
