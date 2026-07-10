# Handoff: Azeem's Writing Workflow — ready to build Issue 05

**Session date:** 2026-07-05  
**Next task:** Implement Issue 05 — Plan stage (Writing Plan extraction + ChromaDB retrieval)

---

## What was done this session

### Issue 04 (completed this session)
Reusable voice/mic input component implemented.

**Files created/changed:**
- `components/__init__.py` — package init
- `components/voice_input.py` — `voice_input_widget(widget_key)`: renders a mic button via `audio-recorder-streamlit`; on stop, sends audio to Whisper (`translations` endpoint — always outputs English from Urdu/English mixed speech), writes transcription directly into `st.session_state[widget_key]`; MD5 hash prevents re-transcribing on every rerun
- `pages/develop.py` — replaced `st.form` (incompatible with reactive audio recorder) with bare `st.text_area(key="develop_response")` + `st.button`; `voice_input_widget("develop_response")` placed in column above text area; clears key on submit
- `requirements.txt` — added `audio-recorder-streamlit>=0.0.10`

**Key decisions:**
- `widget_key` passed to `voice_input_widget` must match `key=` on the paired `st.text_area` — Streamlit picks up programmatic changes to a widget's session state key on next rerun; `value=` on a keyed widget is only honoured on first mount
- Whisper `translations` endpoint used (not `transcriptions`) — always outputs English, handles Urdu/English code-switching correctly
- No language param set — Whisper auto-detects

**Bugs caught during session:**
- Original draft used `value=` on text_area without `key=` — voice transcription would not survive reruns; fixed to write directly into widget's session state key

Committed and pushed: commits `d467915`, `4f5737c`, `a8d85f1`, `e4f812f` on `main`.

---

## Repo layout

```
Azeem's Writing Workflow/
  CONTEXT.md                        ← domain glossary
  PRD.md                            ← full spec and user stories
  issues/
    01-app-scaffold.md              ✅ done
    02-transcribe-stage.md          ✅ done
    03-develop-stage.md             ✅ done
    04-voice-input.md               ✅ done (this session)
    05-plan-stage.md                ← NEXT
    06-draft-stage.md
    07-repurposed-content.md
    08-publish-stage.md
  Code/
    app.py                          ← entry point
    ui.py                           ← PALETTE, inject_css(), render_sidebar(), render_page_header()
    components/
      __init__.py
      voice_input.py                ✅ reusable mic component
    pages/
      transcribe.py                 ✅ full implementation
      develop.py                    ✅ full implementation + mic
      plan.py                       ← placeholder (next)
      draft.py                      ← placeholder
      publish.py                    ← placeholder
    requirements.txt
    .env.example                    ← OPENAI_API_KEY, OPENROUTER_API_KEY
    .env                            ← real keys (not committed)
    .claude/launch.json             ← preview server "Writing Workflow" on port 8502
    WORKING_CONTEXT.md              ← full build log of all issues
```

GitHub: https://github.com/mazeem147/azeem-writing-workflow

---

## Issue 05 spec summary

Full spec: `issues/05-plan-stage.md`

**What to build:**
- Extract a Writing Plan from the Brain Dump (full conversation from Develop stage) via Claude
- Simultaneously query ChromaDB for Content Notes (topical relevance) and Style Notes (prose exemplars)
- Show Writing Plan as collapsible/reorderable sections
- Show Content Notes per section
- User reviews and approves before moving to Draft

**Session state consumed:** `st.session_state.brain_dump` (list of `{"role": "ai"|"user", "text": str}`)  
**Session state produced:** `st.session_state.writing_plan` (structured section list), `st.session_state.content_notes`, `st.session_state.style_notes`

**Key constraint:** ChromaDB lives at `Notion Second Brain (Code)/data/chroma/` — a sibling directory to the Writing Workflow. The Second Brain app already has `embed_utils.py` and query patterns in `pages/chat.py` to follow.

---

## Patterns to follow

### LLM calls (OpenRouter)
```python
import httpx, os
resp = httpx.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
             "Content-Type": "application/json"},
    json={"model": "anthropic/claude-sonnet-4-5", "messages": [...]},
    timeout=60,
)
resp.raise_for_status()
return resp.json()["choices"][0]["message"]["content"].strip()
```

### Voice input (already built)
To drop the mic component into any future page:
```python
from components.voice_input import voice_input_widget
voice_input_widget("my_widget_key")
st.text_area("Label", key="my_widget_key", ...)
```

### Page structure
```python
from ui import inject_css, render_sidebar, render_page_header, PALETTE
inject_css()
render_sidebar("plan")
render_page_header("plan", "📋 Plan", "subtitle")
```

### Python 3.9 constraint
No `X | Y` union types, no `list[str]` generics. No f-strings with backslash expressions — pre-extract variables before building HTML strings.

### HTML safety
User-generated text in `st.markdown(..., unsafe_allow_html=True)` must be wrapped in `html.escape()`.

---

## Design system tokens

| Token | Value |
|---|---|
| Ink (body bg) | `#0d0c14` |
| Sidebar bg | `#1a1826` (no PALETTE key — use hex directly) |
| Mid-ground | `PALETTE["ink_mid"]` → `#2a2838` |
| Gold accent | `PALETTE["gold"]` → `#c9a96e` |
| Gold dim | `PALETTE["gold_dim"]` → `#8a6e42` |
| Text | `PALETTE["text"]` → `#e8e4dc` |
| Muted | `PALETTE["muted"]` → `#9b9690` |
| Done green | `PALETTE["done"]` → `#4a9e6b` |
| Border | `PALETTE["border"]` → `#2e2c3a` |

---

## How to run

```bash
cd "/Users/mazeem147/Claude Code (Personal)/Azeem's Writing Workflow/Code"
.venv/bin/streamlit run app.py --server.port 8502
```

Or use `preview_start` with server name `"Writing Workflow"` (configured in `Code/.claude/launch.json`).

---

## Suggested skills for next session

- **`/code-review --effort low`** — run after implementing to catch runtime-correctness bugs
- **`/verify`** — use preview server to confirm Plan stage renders and ChromaDB query returns results
