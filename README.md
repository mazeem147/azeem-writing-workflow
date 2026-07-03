# Azeem's Writing Workflow

A local Streamlit app that transforms voice memos into published Substack articles — with repurposed social content — grounded in your own notes and writing style.

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
5. **Publish** — Paste the Substack URL after publishing. The article is indexed for future reference.

Repurposed content (Tweet thread + LinkedIn post) is generated alongside the draft.

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

## Build status

| Issue | Stage | Status |
|---|---|---|
| 01 | App scaffold + sidebar navigation | ✅ Done |
| 02 | Transcribe stage | ✅ Done |
| 03 | Develop stage | ✅ Done |
| 04 | Voice input (mic component) | 🔲 Next |
| 05 | Plan stage | 🔲 Pending |
| 06 | Draft stage | 🔲 Pending |
| 07 | Repurposed content | 🔲 Pending |
| 08 | Publish stage | 🔲 Pending |
