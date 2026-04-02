# Semi-Formal Reasoning Templates

Templates used in our replication experiments. Based on the certificate approach
from [Ugare & Chandra (2026)](https://arxiv.org/abs/2603.01896), adapted for
practical use.

## Patch Verification Template

Used in `verify_patch.py`. Forces the agent to check function resolution,
trace execution, and verify regressions before concluding.

```
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

VERDICT: [CORRECT|LIKELY_CORRECT|CONCERNS|BUGGY]
CONFIDENCE: [high|medium|low]
SUMMARY: [one sentence]
```

## Fault Localization Template

Used in the experiment harness. Forces divergence analysis and verification
that fixing the identified line would actually resolve the symptom.

```
PREMISES:
P1: The symptom is [what happens]
P2: The expected behavior is [what should happen]

CODE PATH TRACE:
For each relevant line:
  LINE [N]: [what it does] → [result for buggy input]

DIVERGENCE ANALYSIS:
For each candidate buggy line:
  CLAIM D[N]: At line [N], [code] produces [behavior]
              which contradicts P2 because [reason]
  VERIFICATION: Would fixing ONLY this line fix the symptom? [yes/no + why]

BUGGY LINES: [number(s)] — [reason]
```

## Patch Equivalence Template

From the paper's Appendix A (condensed). Forces per-test execution tracing
for both patches before concluding equivalence.

```
DEFINITIONS:
D1: Two patches are EQUIVALENT MODULO TESTS iff the test suite produces
    identical pass/fail outcomes for both patches.

PREMISES:
P1: Patch 1 modifies [file(s)] by [change]
P2: Patch 2 modifies [file(s)] by [change]
P3: The tests check [behavior]

FUNCTION RESOLUTION:
For EACH function call in each patch:
- Trace Python name resolution (local → enclosing → module → builtins)
- Check for module-level definitions that might shadow builtins

ANALYSIS OF TEST BEHAVIOR:
For each test:
  Claim 1: With Patch 1, test will [PASS/FAIL] because [execution trace]
  Claim 2: With Patch 2, test will [PASS/FAIL] because [execution trace]
  Comparison: [SAME/DIFFERENT]

COUNTEREXAMPLE (if different):
  Test [name] → different outcomes because [trace]

FORMAL CONCLUSION:
ANSWER: [YES patches are equivalent / NO they are not]
```

## Why These Work

The key insight from our experiments: these templates are **cognitive forcing
functions**. They don't improve the model's reasoning ability — they change
**what the model thinks about** before concluding.

Standard chain-of-thought lets the model pattern-match to a plausible answer.
The structured template inserts mandatory checkpoints that prevent premature
conclusions. "Which function is actually being called?" forces a scope check.
"Would fixing ONLY this line resolve it?" forces sufficiency verification.

The value scales with **reasoning distance** — how far the model must trace
from obvious code to actual cause. Locally-obvious bugs show no improvement.
Cross-scope, cross-file, and architectural bugs show dramatic gains.
