#!/usr/bin/env python3
"""Quantifiable writing metrics for paper-polisher.

Reports sentence-length statistics (long-sentence ratio and examples),
paragraph structure, filler phrases, and AI-trace connector counts so the
human polisher can target fixes instead of re-reading everything.

Pure standard library, advisory by default. --strict exits 2 when the
long-sentence ratio exceeds 0.25 or the filler count exceeds 8.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?。！？])\s+")
WORD_RE = re.compile(r"[A-Za-z]+(?:['\u2019-][A-Za-z]+)?")
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
FILLERS = [
    "it is important to note", "it should be noted", "interestingly",
    "remarkably", "notably", "as mentioned above", "as discussed previously",
    "值得注意", "显而易见", "值得注意的是", "众所周知",
    "it is worth noting",
]
AI_CONNECTORS = [
    "moreover", "furthermore", "additionally", "however", "therefore",
    "nevertheless", "nonetheless", "thus", "hence", "in addition",
    "此外", "而且", "然而", "因此", "总之",
]
FILLER_RE = re.compile("|".join(sorted((re.escape(f) for f in FILLERS), key=len, reverse=True)),
                       re.IGNORECASE)
CONNECTOR_RE = re.compile(r"\b(" + "|".join(sorted(AI_CONNECTORS, key=len, reverse=True)) + r")\b", re.IGNORECASE)
CJK_CONNECTOR_RE = re.compile("|".join(re.escape(c) for c in ("此外", "而且", "然而", "因此", "总之")))


def _sentences(text: str) -> list[str]:
    out = []
    for chunk in SENTENCE_SPLIT_RE.split(text):
        chunk = chunk.strip()
        if chunk:
            out.append(chunk)
    return out


def _words(sentence: str) -> int:
    return len(WORD_RE.findall(sentence)) + len(CJK_RE.findall(sentence))


def analyze(text: str) -> dict:
    paragraphs = [p.strip() for p in text.splitlines() if p.strip()]
    sentences = _sentences(text)
    long_sentences = [s for s in sentences if _words(s) > 30]
    para_sentence_counts = [_sentences(p) and len(_sentences(p)) for p in paragraphs]
    filler_hits = FILLER_RE.findall(text.lower())
    connectors = CONNECTOR_RE.findall(text.lower()) + CJK_CONNECTOR_RE.findall(text)
    ratio = (len(long_sentences) / len(sentences)) if sentences else 0.0
    return {
        "characters": len(text),
        "paragraphs": len(paragraphs),
        "paragraph_sentence_counts": para_sentence_counts,
        "sentences": len(sentences),
        "mean_words_per_sentence": round(sum(map(_words, sentences)) / len(sentences), 2) if sentences else 0.0,
        "long_sentences_over_30_words": len(long_sentences),
        "long_sentence_ratio": round(ratio, 3),
        "long_sentence_examples": long_sentences[:5],
        "filler_phrases": {f: filler_hits.count(f) for f in set(filler_hits)},
        "filler_total": len(filler_hits),
        "ai_connectors": {c: connectors.count(c) for c in set(connectors)},
        "ai_connector_total": len(connectors),
        "we_count": len(re.findall(r"\bwe\b", text, re.IGNORECASE)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="text file to analyze (default: stdin)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 2 when long-sentence ratio > 0.25 or filler total > 8")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.file:
        text = Path(a.file).read_text(encoding="utf-8-sig")
    else:
        text = sys.stdin.read()
    out = analyze(text)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if a.strict and (out["long_sentence_ratio"] > 0.25 or out["filler_total"] > 8):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
