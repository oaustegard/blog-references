# Replicating "Agentic Code Reasoning"

Artifacts from the blog post: [Replicating "Agentic Code Reasoning" — and Shipping a Tool From It](https://muninn.austegard.com/blog/replicating-agentic-code-reasoning.html)

## Paper

**Agentic Code Reasoning** — Shubham Ugare, Satish Chandra (Meta, 2026)
- [arXiv:2603.01896](https://arxiv.org/abs/2603.01896)
- Key claim: Semi-formal structured reasoning templates improve LLM code analysis accuracy by 5–12pp over standard chain-of-thought, without executing code.

## What We Did

1. **Reviewed** the paper's methodology and results
2. **Replicated** the core finding using Claude sub-agents on the paper's Django example (0% → 100% on patch equivalence with name shadowing)
3. **Validated** on 3 real bugs from our own repos with zero training contamination (+11pp on fault localization)
4. **Shipped** a `verify_patch` utility that runs semi-formal analysis on code diffs, with outcome tracking for calibration

## Artifacts

| File | Description |
|------|-------------|
| `verify_patch.py` | The verification utility — runs semi-formal analysis on a patch via Claude sub-agent |
| `run_experiment.py` | The fault localization experiment harness (3 bugs × 2 modes × N runs) |
| `semiformal_templates.md` | The semi-formal reasoning templates used in our experiments |

## Key Finding

Semi-formal templates are **cognitive forcing functions**. They change *what the agent considers* before concluding, not just how it formats the answer. The value concentrates on bugs that require non-local reasoning — scope issues, name shadowing, cross-file dependencies.

**Model-tier effect** (postscript finding): Template value is model-capability-dependent. On CVE-2026-29000 (pac4j-jwt, CVSS 10.0), Haiku 4.5 gained +20pp with templates (80%→100%) while Sonnet 4.6 lost 20pp (100%→80%). Practical implication: Haiku + template ≈ Sonnet standard at ~1/10th cost.

## Skill

The templates are packaged as a reusable Claude skill: [`reasoning-semiformally`](https://github.com/oaustegard/claude-skills/tree/main/reasoning-semiformally). Includes model-tier guidance and a decision framework for when to apply.

## Results

| Experiment | Standard | Semi-formal | Delta |
|---|---|---|---|
| Django repo, patch equivalence (N=3) | 0% | 100% | +100pp |
| Own repos, fault localization (N=9) | 89% | 100% | +11pp |
| CVE-2026-29000, Haiku 4.5 (N=5) | 80% | 100% | +20pp |
| CVE-2026-29000, Sonnet 4.6 (N=5) | 100% | 80% | −20pp |

## Usage

```python
from verify_patch import verify_patch

result = verify_patch(
    patch="<your diff here>",
    context="<surrounding code for reference>",
    description="What the patch should do",
)

print(result["verdict"])     # CORRECT / LIKELY_CORRECT / CONCERNS / BUGGY
print(result["confidence"])  # high / medium / low
print(result["summary"])     # One-sentence assessment
```

Requires the [Anthropic Python SDK](https://github.com/anthropics/anthropic-python) and a valid API key.
