# Memory in the Age of AI Agents — Document Map

arXiv: 2512.13564 (107 pages, Dec 2025)
Authors: Yuyang Hu et al. (40+ authors; Fudan/Renmin/Sakana/Oxford consortium)

Generated via `mapping-documents` skill. Four artifacts:

| File | Purpose |
|------|---------|
| `2512_13564_MAP.md` | Section map with typed claims, symbols, dependencies (page-anchored) |
| `2512_13564.symbols.json` | 126 symbol definitions (where defined, where used) |
| `2512_13564.anchors.json` | 283 typed claims (definition/result/method/claim/caveat/open-question) |
| `2512_13564_USAGE.md` | Snippet for CLAUDE.md / project instructions |

## Core framework (for quick reference)

**Forms–Functions–Dynamics** triangle:
- **Forms**: token-level (1D flat / 2D planar / 3D hierarchical) | parametric (internal/external) | latent (generate/reuse/transform)
- **Functions**: factual | experiential | working
- **Dynamics**: formation (F) | evolution (E) | retrieval (R) — operators over memory state M_t

## Quick queries

```bash
# All caveats
python3 -c "import json; [print(f'p.{c[\"page\"]} {c[\"text\"]}') for c in json.load(open('2512_13564.anchors.json')) if c['type']=='caveat']"

# All open questions
python3 -c "import json; [print(f'p.{c[\"page\"]} {c[\"text\"]}') for c in json.load(open('2512_13564.anchors.json')) if c['type']=='open-question']"

# Symbol lookup
python3 -c "import json; [print(s) for s in json.load(open('2512_13564.symbols.json')) if 'TERM' in s['symbol'].lower()]"
```

Mapped via /mnt/skills/user/mapping-documents on 2026-04-17.
