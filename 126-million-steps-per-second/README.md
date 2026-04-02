# 126 Million Steps Per Second (But Why?) — Supplementary Material

Interactive execution traces and implementation code for [the blog post](../126-million-steps-per-second.html).

## Interactive Traces

Self-contained HTML pages showing step-by-step execution on the compiled transformer stack machine. Every step is a parabolic attention head operation — dot-product → argmax → value extraction on compiled weight matrices.

| Trace | Problem | Instructions | Steps | Result |
|-------|---------|-------------|-------|--------|
| [hungarian-trace.html](hungarian-trace.html) | Min-cost perfect matching (10×10) | 682 | 23,167 | Cost = 206 |
| [sudoku-trace.html](sudoku-trace.html) | Sudoku (constraint propagation search + verification) | 7,147 | 6,787 | 60/60 verified |

### Hungarian Algorithm

The full Kuhn-Munkres algorithm runs on the stack machine: dual potentials, augmenting path search, traceback. The 10×10 matrix has cost entries stored in heap memory at addresses 0–99, with potential arrays u[], v[], assignment p[], and working arrays at addresses 100–209.

The trace shows uneven iteration lengths (1,312 to 5,701 steps per row) because later augmenting paths must examine more already-assigned columns.

### Sudoku

Two phases: Norvig's constraint propagation (Python) finds the solution through 172 guesses and 162 backtracks, then the stack machine verifies every placement by loading all 20 peer cells from heap memory and comparing. 1,200 `I32.LOAD` operations and 1,200 `EQ` comparisons, each a parabolic attention head lookup.

## Implementation Code

The program generators that compile these algorithms to stack machine instructions:

- [`examples/hungarian.py`](https://github.com/oaustegard/llm-as-computer/blob/main/examples/hungarian.py) — Hungarian algorithm assembler + runner
- [`examples/sudoku.py`](https://github.com/oaustegard/llm-as-computer/blob/main/examples/sudoku.py) — Sudoku verifier assembler + runner

## Gotchas

Things we learned building these:

- **Stack discipline at jumps**: `JZ`/`JNZ` pop the condition value. Unconditional jumps need `PUSH 1; JNZ label` — that `PUSH 1` consumes a stack slot that gets popped by `JNZ`. Getting this wrong silently corrupts the stack depth.
- **`I32.STORE` operand order**: stack is `[..., addr, value]`, not `[..., value, addr]`. The Mojo executor reads `value = stack[sp]`, `addr = stack[sp-1]`.
- **Step limits**: the default 50K step limit was fine for demos but too low for real algorithms. Raised to 5M with `--max-steps` override ([PR #62](https://github.com/oaustegard/llm-as-computer/pull/62)).
- **Trace output throughput**: a 5M-step verbose trace produces ~100MB of stdout, causing subprocess timeouts even when execution is fast. Added `--quiet` flag.
- **Brute-force vs propagation**: the "AI Escargot" Sudoku needs ~31M backtracks without in-search constraint propagation. Norvig's full propagation reduces this to 162 backtracks. The stack machine can do brute-force peer checking but can't yet do elimination cascades during search — that's the gap between our approach and Percepta's implicit propagation.
