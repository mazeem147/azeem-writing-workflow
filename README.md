# Azeem's Writing Workflow

A local Streamlit app that transforms voice memos into published LinkedIn articles — with repurposed social content — grounded in your own notes and writing style.

## The problem

Ideas arrive in conversation. Writing them down kills the energy. This tool captures the moment, develops it through AI dialogue, and drafts in your voice — not a generic one.

## The workflow

```
Transcribe → Develop → Plan → Draft → Publish
```

1. **Transcribe** — Upload a voice memo. Whisper transcribes it; Claude cleans it and flags uncertain words for review.
2. **Develop** — Claude reads your transcript and opens a dialogue, asking targeted questions to draw out your full position. You answer until you're ready.
3. **Plan** — A structured writing plan is extracted from your conversation, with relevant past notes surfaced from your personal knowledge base.
4. **Draft** — Sections are generated one by one in your voice, using a style fingerprint built from your best past writing.
5. **Publish** — An approval checklist gates the final step. Paste the LinkedIn article URL after publishing, and the full article is chunked and indexed into a `published_articles` collection in your knowledge base, so future development sessions can surface it as a source.

Repurposed content is generated alongside the draft: a **Tweet Thread** (8-12 tweets, native Twitter attention structure), a **LinkedIn Article** (600-900 words, the full argument — the primary publishable form, permanent and Google-indexed), and a **LinkedIn Feed Post** (150-200 words, engineered to earn comments in the first hour, links to the Article).

LinkedIn is the primary publishing surface. Substack was the original destination and is deferred — not part of the current workflow.

## Stack

- [Streamlit](https://streamlit.io) — UI
- [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text) — audio transcription
- [Claude via OpenRouter](https://openrouter.ai) — conversation, cleaning, drafting
- [ChromaDB](https://www.trychroma.com) — local vector store for past notes and published articles

## Setup

**Requirements:** Python 3.9+

```bash
cd Code
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:

```
OPENAI_API_KEY=...
OPENROUTER_API_KEY=...
```

Then run:

```bash
.venv/bin/streamlit run app.py
```

## Project docs

| File | Purpose |
|---|---|
| `PRD.md` | Full product requirements and user stories |
| `CONTEXT.md` | Domain glossary (Trigger, Juice, Capture, Brain Dump, etc.) |
| `Code/WORKING_CONTEXT.md` | Running build log — what's done, key decisions, what's next |
| `issues/` | Per-issue specs for each workflow stage |
| `Code/handoff-issue-NN.md` | End-of-session handoff for the next issue to implement |

## Build status

All five stages are built and working end to end. LinkedIn migration (issues 09-11) is in progress: the domain docs and Repurposed Content stage are done; the Publish stage still needs to be repointed from Substack to a LinkedIn article URL.

| Issue | Stage | Status |
|---|---|---|
| 01 | App scaffold + sidebar navigation | ✅ Done |
| 02 | Transcribe stage | ✅ Done |
| 03 | Develop stage | ✅ Done |
| 04 | Voice input (mic component) | ✅ Done |
| 05 | Plan stage | ✅ Done |
| 06 | Draft stage | ✅ Done |
| 07 | Repurposed content (Tweet Thread + Substack-teaser LinkedIn Post) | ✅ Done, superseded by 10 |
| 08 | Publish stage (Substack) | ✅ Done, being repointed by 11 |
| 09 | Swap Substack→LinkedIn vocabulary in domain docs | ✅ Done |
| 10 | Repurposed content: LinkedIn Article + LinkedIn Feed Post | ✅ Done |
| 11 | Publish stage: repoint to LinkedIn URL | ⏳ Next |
