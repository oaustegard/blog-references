"""
verify_patch.py — Semi-formal patch verification via Claude sub-agent.

Sends a code diff to Claude with a structured reasoning template that forces
the model to trace function resolution, execution paths, and regression risks
before reaching a verdict.

Usage:
    from verify_patch import verify_patch
    result = verify_patch(patch=diff_text, context=file_contents, description="Fix XYZ")
    print(result["verdict"])  # CORRECT / LIKELY_CORRECT / CONCERNS / BUGGY

Requires:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Based on: "Agentic Code Reasoning" (Ugare & Chandra, Meta, 2026)
          https://arxiv.org/abs/2603.01896
"""

import os
import re
import time

try:
    import anthropic
except ImportError:
    raise ImportError("pip install anthropic")


_TEMPLATE = """Analyze this patch for correctness using semi-formal reasoning.

PREMISES:
P1: The patch modifies [what files/functions]
P2: The intended fix is [what it should do]
P3: Must not break [existing behavior]

FUNCTION RESOLUTION:
For each function call in the patch — trace which definition is actually invoked.
Check imports, module scope, class scope, builtins. Flag any name shadowing.

EXECUTION TRACE:
Before: [input] → [buggy behavior]
After:  [input] → [expected behavior]

REGRESSION CHECK:
For each touched code path: [preserved / broken] because [evidence]

EDGE CASES:
[Any unhandled scenarios]

At the end, output EXACTLY these three lines:
VERDICT: [CORRECT|LIKELY_CORRECT|CONCERNS|BUGGY]
CONFIDENCE: [high|medium|low]
SUMMARY: [one sentence]

---

Description: {description}

Patch:
{patch}

Context:
{context}"""


def verify_patch(
    patch: str,
    context: str = "",
    description: str = "",
    model: str = "claude-sonnet-4-6",
) -> dict:
    """Run semi-formal verification on a code patch.

    Args:
        patch: Diff text or before/after code
        context: Surrounding code, file contents, imports
        description: What the patch should do (commit msg, PR title)
        model: Claude model to use

    Returns:
        dict with keys: verdict, confidence, summary, analysis, elapsed_s
    """
    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var

    prompt = _TEMPLATE.format(
        patch=patch,
        context=context or "(no additional context provided)",
        description=description or "(no description provided)",
    )

    t0 = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=3000,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.time() - t0

    text = response.content[0].text

    verdict_m = re.search(r"VERDICT:\s*\*{0,2}([\w_]+)", text)
    conf_m = re.search(r"CONFIDENCE:\s*\*{0,2}(\w+)", text)
    summ_m = re.search(r"SUMMARY:\s*\*{0,2}(.+?)(?:\n|$)", text)

    return {
        "verdict": verdict_m.group(1) if verdict_m else "PARSE_FAIL",
        "confidence": conf_m.group(1) if conf_m else "unknown",
        "summary": summ_m.group(1).strip().strip("*") if summ_m else "(no summary)",
        "analysis": text,
        "elapsed_s": round(elapsed, 1),
        "model": model,
    }


if __name__ == "__main__":
    # Demo: test with the Django name-shadowing example from the paper
    result = verify_patch(
        patch='def y(self):\n    return format(self.data.year, "04d")[-2:]',
        context=(
            "File: django/utils/dateformat.py. Module-level function:\n"
            "def format(value, format_string):\n"
            '    df = DateFormat(value)\n'
            "    return df.format(format_string)\n"
            "y() is a method inside the DateFormat class."
        ),
        description="Fix 2-digit year formatting for dates before 1000 CE",
    )

    print(f"Verdict:    {result['verdict']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Summary:    {result['summary']}")
    print(f"Time:       {result['elapsed_s']}s")
