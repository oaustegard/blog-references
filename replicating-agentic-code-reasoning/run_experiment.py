"""
run_experiment.py — Fault localization experiment: standard vs semi-formal reasoning.

Runs N trials per bug per mode and reports accuracy.
Requires: pip install anthropic

This is the harness used to produce the results in the blog post.
The actual bugs tested were from private repos; substitute your own
bug scenarios in the BUGS list.
"""

import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

try:
    import anthropic
except ImportError:
    raise ImportError("pip install anthropic")

client = anthropic.Anthropic()

# ─── Configuration ───
MODEL = "claude-sonnet-4-6"
N_RUNS = 3
TEMPERATURE = 1.0

# ─── Prompt templates ───
STANDARD = """Identify the buggy line(s). Think step by step.
BUGGY LINES: [number(s)] — [reason]"""

SEMIFORMAL = """Use this structure:
PREMISES: P1: Symptom=[what happens] P2: Expected=[what should happen]
CODE PATH TRACE: For each relevant line: LINE [N]: [what it does] → [result for buggy input]
DIVERGENCE: CLAIM D[N]: Line [N] produces [X] contradicting P2 because [Y]. Would fixing ONLY this line fix it?
BUGGY LINES: [number(s)] — [reason]"""


def run_one(prompt: str) -> str:
    """Single API call."""
    resp = client.messages.create(
        model=MODEL, max_tokens=2048, temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def evaluate_bug(bug: dict) -> dict:
    """Run N trials of standard + semiformal on one bug."""
    numbered = "".join(
        f"{bug['start'] + i:4d}  {line}"
        for i, line in enumerate(bug["lines"])
    )
    base = (
        f"## Bug: {bug['desc']}\n"
        f"## Code ({bug['file']}, lines {bug['start']}-{bug['start']+len(bug['lines'])}):\n"
        f"```{bug['lang']}\n{numbered}```\n\n"
    )

    results = {}
    for mode, suffix in [("standard", STANDARD), ("semiformal", SEMIFORMAL)]:
        prompt = base + suffix
        hits = 0
        for run in range(N_RUNS):
            resp = run_one(prompt)
            mentioned = {int(m) for m in re.findall(r"\b(\d{3,4})\b", resp)}
            hit = any(
                any(abs(gt - m) <= 2 for m in mentioned)
                for gt in bug["gt"]
            )
            hits += hit
            print(f"  [{bug['id']:13s}] {mode:12s} #{run+1}: {'✓' if hit else '✗'}")
            time.sleep(0.5)
        results[mode] = hits / N_RUNS * 100

    return results


# ─── Define your bugs here ───
# Each bug needs: id, lang, file, desc, lines (list of code lines),
#                 start (first line number), gt (ground truth line numbers)
BUGS = [
    # Example structure — replace with your own bugs:
    # {
    #     "id": "my-bug",
    #     "lang": "python",
    #     "file": "module.py",
    #     "desc": "Function returns wrong value when input is negative",
    #     "lines": open("path/to/buggy_file.py").readlines()[50:80],
    #     "start": 51,
    #     "gt": [63],  # ground truth buggy line(s)
    # },
]

if not BUGS:
    print("No bugs defined. Edit the BUGS list in this file with your own scenarios.")
    print("See the blog post for examples of how to extract bugs from git history.")
    exit(0)

# ─── Run ───
print(f"Model: {MODEL} | N={N_RUNS} | temp={TEMPERATURE}")
print(f"{'='*60}\n")

all_results = {}
for bug in BUGS:
    all_results[bug["id"]] = evaluate_bug(bug)

# ─── Report ───
print(f"\n{'='*60}")
print(f"{'Bug':<18} {'Standard':>10} {'Semi-formal':>12} {'Delta':>8}")
print(f"{'-'*18} {'-'*10} {'-'*12} {'-'*8}")
for bug in BUGS:
    r = all_results[bug["id"]]
    delta = r["semiformal"] - r["standard"]
    print(f"{bug['id']:<18} {r['standard']:>9.0f}% {r['semiformal']:>11.0f}% {delta:>+7.0f}pp")
