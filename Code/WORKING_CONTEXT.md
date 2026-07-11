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

**Bug fix (2026-07-11) — "+ Add" crash + broken button row:** clicking "+ Add" threw
`StreamlitAPIException: st.session_state.new_section_title cannot be modified after the
widget with key new_section_title is instantiated` AND the section button row rendered
with overlapping buttons. Two independent causes:
- **The crash** was the widget-key class that already bit `develop.py` and `draft.py`: the
  handler cleared `st.session_state["new_section_title"] = ""` inside the `if st.button(...)`
  block, *after* the `st.text_input` with that key was created this run. Fixed by moving the
  append + clear into an `on_click` callback `_add_section_from_input()` (callbacks run before
  widgets are instantiated on the rerun) — same idiom as `develop.py`'s `_submit_develop_response`.
- **The overlapping buttons** were a *separate, pre-existing* layout bug (present on every Plan
  render, not caused by the crash): the per-section row `st.columns([1, 9, 1, 1, 1])` gave each
  action-button column ~19px, but the `↑`/`↓` buttons render ~40px via `ui.py`'s button padding,
  so they overflowed and overlapped by 5–12px. Streamlit columns share equal `flex-grow`; weight
  only sets `flex-basis`. Fixed by widening to `st.columns([2, 10, 3, 3, 3])` (~46px action
  columns → clean 16px gaps between buttons). Layout is verified visually, not by AppTest.
- **Checked, benign:** the dict `_add_section` appends is `{"title", "bullets"}` (no `pinned_notes`
  key). Nothing on the Plan page reads `section["pinned_notes"]` directly, and the "Generate Draft →"
  handler rebuilds every section *with* that key before navigating, so no `KeyError` path exists.
- **Regression test:** `tests/test_plan_section_ops.py` drives `plan.py` headlessly via `AppTest`
  (asserts add/reorder/delete raise no exception and preserve the str-key/int-key invariants).
  Run: `.venv/bin/python tests/test_plan_section_ops.py` (self-running; also works under pytest).

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

### Issue 07 — Repurposed Content ✅ (superseded by Issue 10, see below)

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

---

### Issue 08 — Publish stage ✅

**Files changed:**
- `pages/publish.py` — full implementation: approval checklist, Substack URL input, chunk + upsert into `published_articles` ChromaDB collection, confirmation screen, session-state clear

**Key decisions:**
- ChromaDB path resolved via the same `__file__` walk as `plan.py` — no hardcoded paths
- `_load_published_collection()` uses `get_or_create_collection("published_articles", metadata={"hnsw:space": "cosine"})` — a **separate** collection; the Notion notes collection (`second_brain`) is never opened for writing here (verified: count 1610 unchanged across a publish)
- Chunking logic (`_chunk_text`, 350 words / 50 overlap) is copied verbatim from `Notion Second Brain (Code)/embed_utils.py` rather than imported (sibling dir not on `sys.path`; `plan.py` set the precedent of replicating Chroma helpers locally)
- Embedding model: `all-MiniLM-L6-v2` via `@st.cache_resource` — same as `plan.py`, so `published_articles` and the notes collection are query-compatible in one retrieval call
- Chunk IDs: `md5(url)[:12] + "__chunk" + i` — idempotent per URL (re-publishing the same URL overwrites, never duplicates; verified)
- Chunk metadata: `{"url", "published_date" (today, ISO), "title" (working_title), "chunk_index"}`
- Article text indexed = `working_title + "\n\n" + "\n\n".join(draft_sections)` so the title is retrievable
- **Confirmation before clear**: on success, details are stashed in `st.session_state.publish_confirmation` (a dict, NOT in the clear list); the confirmation screen renders from it. Piece state is cleared *immediately* after indexing, but the confirmation survives because it lives in its own key
- **Render order** (matters): confirmation block → guard on `draft_sections` → checklist/input. The confirmation block `st.stop()`s first, so it renders even though `draft_sections` was just cleared
- Checklist (4 rows): Draft approved (`draft_approved`), Tweet Thread ready (`tweet_thread`), LinkedIn Post ready (`linkedin_post`), Substack URL provided (live — `url` starts with `http://`/`https://`)
- Publish button gated on all four being true (`can_publish`)
- "Start a New Piece →" clears `publish_confirmation` + `substack_url` and switches to `transcribe.py`
- User-supplied URL + title escaped with `html.escape` in all `unsafe_allow_html` blocks

**Session state consumed:** `draft_sections`, `draft_approved`, `tweet_thread`, `linkedin_post`, `working_title`
**Session state produced:** `publish_confirmation` (transient, cleared on new piece); all piece keys cleared on success

---

---

---

### Issue 10 — Repurposed Content: LinkedIn Article + LinkedIn Feed Post ✅

Supersedes Issue 07's single Substack-teaser "LinkedIn Post". Substack is deferred (per Issue 09's glossary update); LinkedIn is now the primary publishing surface.

**Files changed:**
- `pages/repurpose.py` — `_generate_linkedin_post` (3-5 sentence Substack teaser) removed. Replaced with `_generate_linkedin_article` (600-900 words, full argument, native article editor) and `_generate_linkedin_feed_post` (150-200 words, first-hour-engagement hook, references the Article). Both go through `_strip_em_dashes` (unchanged Voice-rule enforcement) and a new `_strip_markdown` pass.
- `tests/test_repurpose_content.py` — new. AppTest-driven, `httpx.post` monkeypatched with marker-based canned responses (no network/API key needed).

**Key decisions:**
- Tweet Thread generation (`_generate_tweet_thread`) is unchanged except its closing-hook system-prompt line, which now points at the LinkedIn Article instead of Substack.
- All three generation system prompts avoid the literal word "Substack" entirely, including in negative instructions ("don't mention X") — an early test caught the article prompt's own "do not mention Substack" line violating the no-Substack-anywhere constraint. Rephrased to "do not reference any other publishing destination."
- `_strip_markdown(text)` (new, alongside `_strip_em_dashes`) strips `**bold**` and `#`/`##` headers from the Article and Feed Post outputs only — live testing showed the model sometimes opens the Feed Post with a bolded title-line or markdown headline, which LinkedIn renders as literal asterisks/hashes. Not applied to Tweet Thread (ticket requires it stay unchanged).
- Session state keys: `linkedin_post` → replaced by `linkedin_article` and `linkedin_feed_post`. `tweet_thread` unchanged.
- Generation order: Tweet Thread → LinkedIn Article → LinkedIn Feed Post, each its own session-state-gated phase with `st.spinner` + `st.rerun()`, same idiom as before. The Feed Post prompt doesn't take the Article's text as input (it references the Article only conceptually, e.g. "I go deeper in the article below") — this keeps regeneration of one tab fully independent of the others, and there's no real URL to link to yet (that only exists after manual publish, Issue 11).
- **Generation refactor (code-review follow-up):** the three near-identical generation phases were collapsed into one `_generate_output(full_draft, state_key, label, generate_fn, validate)` orchestrator, and the two single-block display tabs into `_render_text_output(state_key, text, regen_label, regen_key)`. The Tweet Thread tab keeps its bespoke per-tweet/char-count rendering inline (genuinely different, not folded). Validators: `_validate_tweet_count` (under-8) and `_word_range_validator(label, regen_label, lo, hi)` (a factory used for both the 600-900 article and 150-200 feed-post checks).
- **Word-count range warnings now persist across the rerun.** The earlier version emitted `st.warning()` on the same pass that then called `st.rerun()`, so warnings flashed and vanished (a code-review Spec finding — the visible backing for the 600-900 / 150-200 word ACs never reached the user). Fixed: `_generate_output` stores the validator's result in `st.session_state.gen_warnings[state_key]`, and the display phase (which does not rerun) renders it via `st.warning()`. Regenerating an output pops its warning. This also fixed the same dead-warning bug in the pre-existing Tweet Thread under-8 warning, which now surfaces too (the thread *output* is unchanged). `tests/test_repurpose_content.py` asserts the warnings actually render in the final tree.
- Tabs reorder to `["🐦 Tweet Thread", "📰 LinkedIn Article", "💼 LinkedIn Feed Post"]`; each has its own `↺ Regenerate …` button, independent (only its own session-state key + warning are cleared).
- **Known follow-on for Issue 11**: `pages/publish.py`'s checklist still checks `st.session_state.get("linkedin_post")` (now always falsy/absent) and still prompts for a Substack URL — both stale after this rename. Left untouched per this ticket's explicit scope; Issue 11 owns `publish.py`.
- **Manual verification**: driven live in the browser via a real 5-stage run (macOS `say` → `.wav` → real Whisper/Claude/OpenRouter calls, no mocks) after discovering the embedded preview browser can't drive native file-picker dialogs — used a temporary env-gated session-state seed block in `repurpose.py` (`WW_DEBUG_SEED=1`), fully removed afterward and confirmed via a clean server restart that the guard behaves normally again.

**Session state consumed:** `st.session_state.draft_sections` (from Draft stage)
**Session state produced:** `st.session_state.tweet_thread` (list[str], 8-12 tweets), `st.session_state.linkedin_article` (str, 600-900 words), `st.session_state.linkedin_feed_post` (str, 150-200 words), `st.session_state.gen_warnings` (dict[state_key → warning str or None], drives the persistent range/count warnings)

---

### Issue 11 — Publish stage: repoint to LinkedIn URL ✅

Supersedes Issue 08. The `published_articles` ChromaDB indexing (`_chunk_text`, `_index_article`, `all-MiniLM-L6-v2` embedding, idempotent per-URL upsert, metadata) was already correct and untouched — this was a relabel/repoint of the stale Substack-era UI Issue 10 left behind, not a rebuild.

**Files changed:**
- `pages/publish.py` — `linkedin_ok` (checked the now-dead `linkedin_post` key) split into `article_ok` (`linkedin_article`) and `feed_ok` (`linkedin_feed_post`). The Substack URL `st.text_input` (key `substack_url`) replaced with a LinkedIn URL input (key `linkedin_url`, LinkedIn-specific placeholder/help text). Checklist grew from 4 to 5 rows: Draft approved, Tweet Thread ready, LinkedIn Article ready, LinkedIn Feed Post ready, LinkedIn URL provided. `can_publish` and the hint text below the checklist updated to require both `article_ok` and `feed_ok`. `_PIECE_KEYS` swapped `linkedin_post` for `linkedin_article` + `linkedin_feed_post`, and added `gen_warnings` (new in Issue 10, previously never cleared). "Start a New Piece" now pops `linkedin_url` instead of `substack_url`.

**Key decisions:**
- No changes to `_chunk_text`, `_index_article`, `_load_embed_model`, `_load_published_collection`, or the confirmation-screen/guard structure — all already matched this ticket's ACs from Issue 08.
- `publish_confirmation` stays out of `_PIECE_KEYS`, unchanged — it's still the separate key that survives `_clear_piece_state()` so the confirmation screen renders after the piece state is wiped.
- **Manual verification**: the embedded preview browser can't drive the native file-picker for the Transcribe upload step, so rather than running the full 5-stage pipeline, a temporary env-gated seed block (`SEED_PUBLISH_TEST=1`) was added to the top of `publish.py` to populate `draft_sections`/`draft_approved`/`tweet_thread`/`linkedin_article`/`linkedin_feed_post`/`working_title` directly, then removed before considering the work done. First seed attempt used `setdefault(...)`, which silently re-populated cleared keys on the post-publish `st.rerun()` and masked whether `_clear_piece_state()` actually worked — fixed by gating the seed behind a one-time `_seed_publish_test_done` flag so it only fires on the very first run of a session. Confirmed live: all 5 checklist rows gate correctly on the new keys, indexing wrote one chunk into `published_articles` with the correct LinkedIn URL/date/title metadata (verified by querying the real shared ChromaDB directly), the confirmation screen renders and survives the state clear, and after "Start a New Piece" the sidebar shows "Untitled piece" with every stage reset to unstarted. The one test chunk written to the real shared ChromaDB was deleted afterward; `second_brain` (Notion notes) collection count was confirmed unchanged (1610 before and after) — never written to.
- Found a stale "Substack article" mention in `pages/draft.py`'s section-generation system prompt (an internal Claude prompt, not user-facing UI) — out of this ticket's scope (Draft stage, not Publish), flagged separately rather than fixed here.

**Session state consumed:** `draft_sections`, `draft_approved`, `tweet_thread`, `linkedin_article`, `linkedin_feed_post`, `working_title`
**Session state produced:** `publish_confirmation` (dict: title, url, chunks, published_date) — survives the piece-state clear that follows a successful publish.

---

## What's next

All 8 original issues implemented, plus Issue 09 (vocabulary), Issue 10 (LinkedIn Article + Feed Post), and Issue 11 (LinkedIn publish stage). All 5 stages are now LinkedIn-native end to end. Outstanding: the stale "Substack article" line in `pages/draft.py`'s system prompt (flagged as a separate follow-up, not part of Issue 11's scope), and rotating the GitHub PAT embedded in the `origin` remote URL (flagged in the Issue 11 handoff).
