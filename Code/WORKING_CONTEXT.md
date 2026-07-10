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

---

### Issue 03 — Develop stage ✅

**Files changed:**
- `pages/develop.py` — full implementation: two-column layout, Seeder Question on entry, iterative Q&A loop, "Build the Plan →" navigation

**Key decisions:**
- Split-panel: transcript (left, read-only, scrollable) | conversation (right)
- Seeder Question generated on first entry via `anthropic/claude-sonnet-4-5` through OpenRouter — prompt instructs Claude to find a specific claim or gap, never ask generically
- Follow-up questions use full conversation history passed as `messages` array (system + transcript + prior turns)
- All conversation turns stored as `{"role": "ai"|"user", "text": str}` dicts in `st.session_state.conversation`
- "Build the Plan →" saves `st.session_state.brain_dump = list(st.session_state.conversation)` before switching pages
- Guard at top: if `st.session_state.transcript` is absent, shows error + back button + `st.stop()`
- `ai_text` initialized to `None` before try block; append guarded with `if ai_text` to prevent `UnboundLocalError` if `st.stop()` is swallowed
- `PALETTE` has no `"sidebar"` key — use `"#1a1826"` directly

**Session state consumed:** `st.session_state.transcript` (set by Transcribe stage)  
**Session state produced:** `st.session_state.brain_dump` (consumed by Plan stage)

---

---

### Issue 04 — Voice input component ✅

**Files created/changed:**
- `components/__init__.py` — package init
- `components/voice_input.py` — `voice_input_widget(widget_key)`: renders a mic button via `audio-recorder-streamlit`; on stop, sends WAV to Whisper, writes transcription into `st.session_state[widget_key]` (same key as paired `st.text_area`), reruns
- `pages/develop.py` — replaced `st.form` (incompatible with reactive audio recorder) with bare widgets; added `voice_input_widget("develop_response")` above the response text area; `key="develop_response"` on text_area so transcription is injected correctly; clears key on submit
- `requirements.txt` — added `audio-recorder-streamlit>=0.0.10`

**Key decisions:**
- `widget_key` passed to `voice_input_widget` must match the `key=` of the associated `st.text_area` — writing directly to the widget's session state key is the only way to inject text that survives Streamlit reruns (using `value=` on a keyed widget only sets the default on first mount)
- MD5 hash of audio bytes used to avoid re-transcribing on every rerun (component returns same bytes until next recording)
- No language specified in Whisper call — auto-detects Urdu/English code-switching

**Where to drop the component in future stages:**
- Draft revision modal (Issue 06): call `voice_input_widget("revision_feedback")`, pair with `st.text_area(..., key="revision_feedback")`

---

### Issue 05 — Plan stage ✅

**Files changed:**
- `pages/plan.py` — full implementation
- `requirements.txt` — added `chromadb>=0.5.0`, `sentence-transformers>=2.7.0`

**Key decisions:**
- ChromaDB path resolved via `__file__` walk: `pages/ → Code/ → Writing Workflow/ → Claude Code (Personal)/` then into `Notion Second Brain (Code)/data/chroma/` — sibling directory, no hardcoded paths
- `@st.cache_resource` on `_load_embed_model()` and `_load_chroma()` — model and collection loaded once per Streamlit process, not per rerun
- Writing Plan extracted as JSON by Claude (claude-sonnet-4-5 via OpenRouter); code-fence stripping + regex fallback for malformed JSON
- Content Notes: one ChromaDB query per section (top 5), using section title + bullets as query text; stored in `st.session_state.content_notes` keyed by `str(section_idx)`
- Style Notes: single fixed-phrase query ("personal reflection opinion I believe..."); top 10 results stored in `st.session_state.style_notes` for Draft stage Style Fingerprint extraction
- Section manipulation helpers (`_swap_sections`, `_delete_section`, `_add_section`) re-index `content_notes`, `pinned_notes`, `section_expanded` consistently on every structural change
- `section_expanded` uses **int** keys; `content_notes` and `pinned_notes` use **str** keys — consistent throughout
- Pin state stored as `list[int]` (indices into the section's content_notes list) in `st.session_state.pinned_notes`
- "Generate Draft →" embeds pinned note texts into each section's `pinned_notes` field before navigating to draft.py
- Selectbox `key="notes_section_view"` is clamped to valid range before render to prevent `StreamlitAPIException` after section deletion

**Bugs caught in code review:**
- `plan_data` initialized to `None` before try block — same pattern as `ai_text` in develop.py — prevents `UnboundLocalError` if `st.stop()` is swallowed
- Selectbox index clamped before render: `st.session_state["notes_section_view"] = min(stored, len(plan)-1)` after any deletion

**Session state consumed:** `st.session_state.brain_dump` (from Develop stage)
**Session state produced:** `st.session_state.writing_plan` (list of `{"title", "bullets", "pinned_notes"}`), `st.session_state.content_notes`, `st.session_state.style_notes`

---

---

### Issue 06 — Draft stage ✅

**Files changed:**
- `pages/draft.py` — full implementation: Style Fingerprint extraction, sequential section-by-section generation, section card renderer, inline revision form with mic input, "Approve Draft →" navigation

**Key decisions:**
- Style Fingerprint extracted via a single Claude call over `style_notes` before generation begins; stored in `st.session_state.style_fingerprint`. If no style_notes available, fingerprint is `""` and generation proceeds without it.
- SKILL.md (Voice rules) read at module load time from `../../../skills/writing-voice/SKILL.md` relative to `Code/pages/`; included verbatim in every section generation prompt.
- Section generation is sequential: on each rerun, already-completed sections are rendered, then the next section is generated and appended to `draft_sections`, then `st.rerun()`. Produces progressive "section appears" UX.
- Revision uses an **inline form** (not `@st.dialog`) because `voice_input_widget` calls `st.rerun()` internally after transcription; inside a `@st.dialog` this closes the modal before the user can see the transcribed text. The inline form persists across reruns via `st.session_state.modal_section_idx`.
- `modal_section_idx` tracks which section's revision form is open (int or None). Clicking "Revise ✦" sets it; "Cancel" or "Regenerate" clears it to None.
- Only one revision form open at a time (single `modal_section_idx`). Form is rendered inline below the section card.
- `revision_feedback` key shared between `voice_input_widget` and `st.text_area` — same pattern as `develop_response` in develop.py.
- Section generation prompt includes: section title + bullets, position hint (opening/middle/closing), Style Fingerprint, Voice Rules, pinned Content Notes, optional revision feedback. Model: `anthropic/claude-sonnet-4-5` via OpenRouter.
- Paragraph breaks in generated text rendered as `<p>` tags (double-newline → `</p><p>` replacement on HTML-escaped text).
- "Approve Draft →" navigates to `pages/publish.py` (placeholder until Issue 08).

**Session state consumed:** `st.session_state.writing_plan`, `st.session_state.style_notes`
**Session state produced:** `st.session_state.style_fingerprint` (str), `st.session_state.draft_sections` (list[str])

---

---

### Issue 07 — Repurposed Content ✅

**Files created/changed:**
- `pages/repurpose.py` — new page: guard, Tweet Thread generation, LinkedIn Post generation, tabs UI, regenerate buttons, "Mark as Published →" navigation
- `app.py` — added `pages/repurpose.py` to `st.navigation()` pages list
- `pages/draft.py` — "Approve Draft →" now navigates to `pages/repurpose.py` (was `pages/publish.py`)

**Key decisions:**
- Repurposed Content is not a separate sidebar stage — `render_sidebar("publish")` used, so Draft shows ✓ and Publish shows ● while on this page
- Tweet Thread generated as JSON array via a single Claude call (claude-sonnet-4-5 via OpenRouter); code-fence stripping + `json.loads` fallback to line-split if malformed
- LinkedIn Post generated via a separate Claude call; returns plain text
- Both generation calls happen sequentially on page load (tweet thread first, then LinkedIn post), each with its own `st.spinner`; `st.rerun()` after each to update state before proceeding
- Display uses `st.tabs(["🐦 Tweet Thread", "💼 LinkedIn Post"])` — tabs keep the screen uncluttered
- Each tweet displayed with `st.code(tweet, language=None)` — built-in copy button, no extra JS
- Character count shown per tweet (gold if ≤280, red `#e05252` if over)
- LinkedIn Post displayed with `st.code(post, language=None)` — single copyable block
- Regenerate buttons (`↺ Regenerate Thread`, `↺ Regenerate Post`) set the relevant session key to `None` and rerun; the generation phase picks them up
- Only one regeneration at a time (independent keys: `tweet_thread`, `linkedin_post`)
- "Mark as Published →" navigates to `pages/publish.py`

**Session state consumed:** `st.session_state.draft_sections` (from Draft stage)
**Session state produced:** `st.session_state.tweet_thread` (list[str], 8-12 tweets), `st.session_state.linkedin_post` (str)

---

## What's next

Issues still to implement (in order):
- `08-publish-stage.md` — Substack URL input, index into `published_articles` ChromaDB collection
