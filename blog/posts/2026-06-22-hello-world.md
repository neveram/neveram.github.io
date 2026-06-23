---
title: Hello, World
date: 2026-06-22
excerpt: Why I'm starting this blog and what I'll write about. LLM data pipelines, inference engineering, and the parts of ML infra that are harder than they look.
---

# Hello, World

I built this blog to write down the things I learn while shipping LLM data
pipelines and inference systems at scale. Not tutorials. Not hype. The actual
sharp edges. The kind that cost a week and don't show up in the README.

## What I'll write about

- **Pre-training data**: dedup that doesn't lie, multi-modal pipelines, the
  unglamorous work of safety filtering at petabyte scale.
- **Post-training**: synthetic data generation, eval harnesses, the question
  every ablation eventually asks ("did the data move the model, or did we
  just retrain it?").
- **Inference**: vLLM internals, KV cache layout, the tradeoffs nobody puts
  in the README.
- **Agents**: MCP, planner/executor loops, why most agent harnesses don't
  survive contact with real codebases.

If you're working in this area and want to compare notes, my email is in the
footer.

## A note on style

I'm going to keep posts short. If I can't explain it in a thousand words I
probably don't understand it yet.
