# Working Context — Azeem's Writing Workflow

## What's been built

### Issue 01 — App scaffold + sidebar navigation ✅

**Files created:**
- `app.py` — entry point, `st.navigation()` with 5 pages, `position="hidden"` (sidebar handles nav)
- `ui.py` — shared design system: `PALETTE`, `inject_css()`, `render_sidebar()`, `render_page_header()`
- `pages/transcribe.py` — Stage 1 placeholder
- `pages/develop.py` — Stage 2 placeholder
- `pages/plan.py` — Stage 3 placeholder
- `pages/draft.py` — Stage 4 placeholder
- `pages/publish.py` — Stage 5 placeholder
- `requirements.txt` — `streamlit>=1.35.0`
- `.venv/` — Python 3.9 venv, streamlit installed

**Design system (ui.py):**
- Ink ground: `#0d0c14`, sidebar: `#1a1826`
- Amber-gold accent: `#c9a96e`
- Georgia serif for article headings, system-ui for chrome
- `render_sidebar(active_stage)` — draws dot/connector stage list + `st.page_link` nav; active stage highlighted gold, done stages green ✓, pending stages muted
- `render_page_header(stage_key, title, subtitle)` — shared h1 + subtitle used on every page
- Sidebar collapse/expand: `stToolbar` kept visible (contains expand button); Deploy button and status widget hidden via CSS; expand button styled gold

**Known issues / non-ideal things:**
- Sidebar stage dots are visual-only (not individually clickable); navigation is via `st.page_link` items below the dots
- Python 3.9 — no f-strings with backslash expressions; all HTML built with string concatenation using pre-extracted variables
- `working_title` in sidebar is hardcoded to `"Untitled piece"` (comes from `st.session_state.get("working_title", "Untitled piece")`)

**How to run:**
```
cd "Azeem's Writing Workflow/Code"
.venv/bin/streamlit run app.py
```
Or via Claude Code preview: server named "Writing Workflow" on port 8502 (configured in `.claude/launch.json`).

---

### Issue 02 — Transcribe stage ✅

**Files changed:**
- `pages/transcribe.py` — full implementation: file uploader, Whisper transcription, Claude cleaning pass, `[word?]` highlight + correction panel, "Begin Development Session →" button
- `app.py` — added `load_dotenv()` at startup
- `requirements.txt` — added `openai`, `httpx`, `python-dotenv`
- `.env.example` — template with `OPENAI_API_KEY` and `OPENROUTER_API_KEY`

**Key decisions:**
- `[word?]` format (e.g. `[yaar?]`) for uncertain words — Claude wraps its best guess inside brackets
- Corrections panel shows each uncertain word with an inline text input; live-updates the rendered transcript on change
- Final corrected transcript stored in `st.session_state.transcript` (strips all `[word?]` markers, replaces with correction or original guess)
- `working_title` auto-set from first 6 words of cleaned transcript
- Model: `anthropic/claude-haiku-4-5` via OpenRouter for the cleaning pass

---

## What's next

Issues still to implement (in order):
- `03-develop-stage.md` — Seeder Questions, multi-turn conversation, Brain Dump accumulation
- `04-voice-input.md` — mic button on every text input, Whisper insertion
- `05-plan-stage.md` — Writing Plan extraction, ChromaDB retrieval (Content Notes + Style Notes)
- `06-draft-stage.md` — section-by-section draft generation, Style Fingerprint, section revision modal
- `07-repurposed-content.md` — Tweet Thread + LinkedIn Post generation
- `08-publish-stage.md` — Substack URL input, index into `published_articles` ChromaDB collection
