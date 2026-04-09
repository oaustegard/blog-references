# Framing Resistance in Medical QA

Reference materials for [This Treatment Works, Right? Testing Framing Resistance in Medical QA](https://muninn.austegard.com/blog/this-treatment-works-right.html).

A rapid replication of [Yun et al. (2026)](https://arxiv.org/abs/2503.21210) at ~5% scale, testing whether a framing-resistant system prompt mitigates LLM sensitivity to question phrasing in medical evidence review.

## Design

- **20 medical reviews**, effectiveness question type
- **4 conditions**: {positive, negative} framing × {baseline, framing-resistant prompt}
- **Models**: Claude Haiku 4.5, Sonnet 4, Opus 4, Gemini 3 Pro
- **Judges**: Haiku and Opus independently score evidence direction (HIGHER/LOWER/NEUTRAL)
- **260 total responses** (with reduced Opus runs due to cost)

## Files

| File | Description |
|------|-------------|
| `experiment_runner.py` | Full experiment pipeline: question generation, model calls, LLM-as-judge scoring |
| `framing_resistant_prompt.txt` | The framing-resistant system prompt tested as intervention |
| `results_summary.json` | All 260 scored responses with model, condition, framing, and judge verdicts |
| `experiment_reviews.json` | The 20 Cochrane-style review abstracts used as evidence |
| `sonnet_example_responses.json` | Example Sonnet responses showing framing sensitivity in action |

## Key Findings

- **Sonnet**: Contradictory flip rate dropped from 10% → 5% with the resistant prompt (Opus judge)
- **Haiku**: Framing sensitivity *increased* with the prompt — metacognitive load exceeded capability
- **Opus and Gemini 3 Pro**: Already robust; no contradictory flips in either condition
- Model capability determines whether metacognitive prompting helps or hurts

## Running

The experiment runner expects Claude and Gemini API access via environment variables and skill imports from a [Muninn](https://github.com/oaustegard/muninn.austegard.com) session. It is provided for transparency, not as a turnkey script.
