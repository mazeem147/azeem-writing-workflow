---
title: OpenRouter as the single inference provider
status: accepted
date: 2026-07-03
---

## Context

The tool makes multiple LLM calls across the pipeline: transcript cleaning, Seeder Question generation, Writing Plan extraction, Style Fingerprint extraction, Draft section generation, and Repurposed Content generation. A provider decision is needed.

## Decision

All LLM calls are routed through OpenRouter using its OpenAI-compatible API. A single `OPENROUTER_API_KEY` environment variable is the only credential required. The model used per call is configurable via a string identifier (e.g. `anthropic/claude-sonnet-4-5`, `openai/gpt-4o`) without changing client code.

## Alternatives rejected

- **Direct Anthropic API**: locks all calls to Anthropic models; separate SDK from any OpenAI-compatible calls.
- **Direct OpenAI API**: same lock-in problem in the other direction.
- **Multiple providers directly**: requires managing multiple API keys and SDKs; adds complexity with no benefit at this scale.

## Consequences

- One API key, one base URL (`https://openrouter.ai/api/v1`), one SDK (OpenAI Python client with `base_url` override).
- Model can be swapped per call type without changing the client — useful for cost optimisation (cheaper model for cleaning, stronger model for Draft generation).
- Whisper transcription is handled separately via the `openai` Python client pointed at OpenAI directly (OpenRouter does not proxy audio transcription endpoints). This is the only call that does not go through OpenRouter.
