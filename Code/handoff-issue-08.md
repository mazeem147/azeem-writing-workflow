# Handoff: Azeem's Writing Workflow — ready to build Issue 08

**Session date:** 2026-07-10
**Next task:** Implement Issue 08 — Publish stage (Substack URL input, approval checklist, index article into `published_articles` ChromaDB collection, clear session state)

---

## What was done this session

### Issue 07 (completed this session)
Repurposed Content stage fully implemented and code-reviewed.

**Files created/changed:**
- `pages/repurpose.py` — new page: guard on `draft_approved`, Tweet Thread generation, LinkedIn Post generation, tabs UI, per-tweet character count, regenerate buttons, "Mark as Published →" navigation
- `app.py` — added `pages/repurpose.py` to `st.navigation()` pages list
- `pages/draft.py` — "Approve Draft →" sets `st.session_state.draft_approved = True` before navigating to `repurpose.py`
- `ui.py` — added `PALETTE["error"]` (`#e05252`) for over-limit tweet character counts

**Key decisions:**
- Repurposed Content is not a separate sidebar stage — `render_sidebar("publish")` used, so Draft shows ✓ and Publish shows ● while on this page (documented in handoff-issue-07.md, intentional)
- Tweet Thread generated as JSON array via a single Claude call (claude-sonnet-4-5 via OpenRouter); code-fence stripping + `json.loads` with line-split fallback
- LinkedIn Post generated via a separate Claude call; returns plain text
- Sequential generation with spinners; `st.rerun()` after each stores state before display
- Each tweet displayed with `st.code(tweet, language=None)` — built-in copy button
- `draft_approved` flag: set in `draft.py` before navigation; `repurpose.py` guards on it (not just `draft_sections` presence)
- Minimum tweet count warning if Claude returns fewer than 8 (prompt instructs 8-12; warning allows regenerate)
- Regenerate buttons for each format independently (set key to `None`, rerun, generation phase picks it up)

**Code review findings fixed:**
- `"#e05252"` hardcoded hex → `PALETTE["error"]` after adding token to `ui.py`
- `PALETTE["muted"]` accessed inline in guard HTML → pre-extracted to `_guard_muted`

**Session state produced:**
- `st.session_state.draft_approved` — `bool` True (set in draft.py on "Approve Draft →")
- `st.session_state.tweet_thread` — `list[str]`, 8-12 tweet strings ≤280 chars
- `st.session_state.linkedin_post` — `str`, 3-5 sentence LinkedIn post

---

## Repo layout

```
Azeem's Writing Workflow/
  CONTEXT.md
  PRD.md
  issues/
    01-app-scaffold.md              ✅ done
    02-transcribe-stage.md          ✅ done
    03-develop-stage.md             ✅ done
    04-voice-input.md               ✅ done
    05-plan-stage.md                ✅ done
    06-draft-stage.md               ✅ done
    07-repurposed-content.md        ✅ done (this session)
    08-publish-stage.md             ← NEXT (final issue)
  Code/
    app.py                          ← entry point; repurpose.py now registered
    ui.py                           ← PALETTE (now includes "error"), inject_css(), render_sidebar(), render_page_header()
    components/
      __init__.py
      voice_input.py                ✅ reusable mic component
    pages/
      transcribe.py                 ✅ full implementation
      develop.py                    ✅ full implementation + mic
      plan.py                       ✅ full implementation
      draft.py                      ✅ full implementation + sets draft_approved
      repurpose.py                  ✅ full implementation (this session)
      publish.py                    ← placeholder — Issue 08
    requirements.txt
    .env.example
    .env                            ← real keys (not committed)
    WORKING_CONTEXT.md              ← full build log of all issues
    handoff-issue-08.md             ← this file
```

GitHub: https://github.com/mazeem147/azeem-writing-workflow  
Last commit: `0681f9f` — "Issue 06 + 07: Draft stage and Repurposed Content stage"

---

## Session state entering Issue 08

The Publish stage will receive:

- `st.session_state.draft_sections` — `list[str]`, one prose block per Writing Plan section. Full article: `"\n\n".join(st.session_state.draft_sections)`.
- `st.session_state.draft_approved` — `bool` True (set by "Approve Draft →" in draft.py)
- `st.session_state.tweet_thread` — `list[str]`, 8-12 tweets
- `st.session_state.linkedin_post` — `str`, LinkedIn post text
- `st.session_state.working_title` — `str`, working title from Transcribe stage (first 6 words of transcript)
- `st.session_state.writing_plan` — `list[dict]` where each dict is `{"title": str, "bullets": list[str], "pinned_notes": list[str]}`

---

## Issue 08 spec summary

Full spec: `issues/08-publish-stage.md` — read this before implementing.

**What to build:**
1. **Approval checklist** — four items shown before the URL input:
   - Draft approved ✓ (check `draft_approved`)
   - Tweet Thread ready ✓ (check `tweet_thread`)
   - LinkedIn Post ready ✓ (check `linkedin_post`)
   - Substack URL provided (live — updates as user types)
2. **URL input** — `st.text_input` for the Substack URL
3. **Index into ChromaDB** — on submission, chunk the full article text and upsert into a `published_articles` collection in the shared Second Brain ChromaDB, with Substack URL + publication date as chunk metadata. Use the same `all-MiniLM-L6-v2` embedding model already in use by the Notion notes collection.
4. **Confirmation** — shown after successful indexing
5. **Clear session state** — reset all piece-related keys after publication so the tool is ready for a new piece

**Session state produced:**
- None persisted — on success, relevant keys are cleared.

---

## ChromaDB integration — critical context

This is the hardest part of Issue 08. Key facts:

- **ChromaDB path**: same resolution as in `plan.py` — walk up from `pages/` via `__file__` to `Claude Code (Personal)/`, then into `Notion Second Brain (Code)/data/chroma/`. Do NOT hardcode the path.
- **Embedding model**: `all-MiniLM-L6-v2` via `sentence-transformers`. Already loaded with `@st.cache_resource` in `plan.py` — replicate that pattern.
- **Collection name**: `published_articles` (new collection, created on first use; ChromaDB creates it if it doesn't exist).
- **Notion notes collection** (`st.session_state` reads from it in plan.py): never write to it. Only write to `published_articles`.
- **`embed_utils.py`** lives at `Notion Second Brain (Code)/embed_utils.py` — read it before implementing to understand the chunking + upsert pattern. The PRD says to use it; the Publish stage should mirror its approach.
- **Chunk metadata** to include per chunk: `{"url": substack_url, "published_date": "YYYY-MM-DD", "title": working_title, "chunk_index": int}`.
- **IDs**: use `working_title + "_chunk_" + str(chunk_index)` (or a hash) so re-upserts are idempotent.

---

## Patterns to follow

### LLM calls (OpenRouter)
No Claude calls needed for Issue 08 — this stage is purely ChromaDB + UI.

### Page structure
```python
from ui import inject_css, render_sidebar, render_page_header, PALETTE
inject_css()
render_sidebar("publish")
render_page_header("publish", "🚀 Publish", "Index your article into the Second Brain.")
```

### ChromaDB (from plan.py)
```python
import chromadb
from sentence_transformers import SentenceTransformer

@st.cache_resource
def _load_embed_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def _load_chroma():
    # walk __file__ to find the ChromaDB path
    ...
    return chromadb.PersistentClient(path=chroma_path)
```

### Python 3.9 constraint
No `X | Y` union types, no `list[str]` generics. No f-strings with backslash expressions — pre-extract variables before building HTML strings.

### HTML safety
User-supplied text (the Substack URL, the working title) in `st.markdown(..., unsafe_allow_html=True)` must be wrapped in `html.escape()`.

### UnboundLocalError pattern
```python
result = None
with st.spinner("…"):
    try:
        result = do_thing()
    except Exception as exc:
        st.error(str(exc))
        st.stop()
if result is None:
    st.stop()
```

### Session state clear on success
After successful indexing, clear the keys that belong to the current piece:
```python
for key in ["transcript", "brain_dump", "conversation", "writing_plan",
            "content_notes", "style_notes", "style_fingerprint",
            "draft_sections", "draft_approved", "tweet_thread",
            "linkedin_post", "working_title", "modal_section_idx",
            "revision_feedback"]:
    st.session_state.pop(key, None)
```

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
| Error red | `PALETTE["error"]` → `#e05252` |
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

- **`/implement Issue 08`** — triggers the same build pattern; read `issues/08-publish-stage.md` and `embed_utils.py` (in the Second Brain sibling directory) first
- **`/code-review --since HEAD`** — run after implementing to catch HTML safety issues with user-supplied URL text and ChromaDB write isolation
- **`/verify`** — use preview server to confirm the checklist updates live, the confirmation screen appears after indexing, and session state is cleared
