# Handoff: Azeem's Writing Workflow — ready to build Issue 06

**Session date:** 2026-07-08
**Next task:** Implement Issue 06 — Draft stage (section-by-section generation, Style Fingerprint, section revision modal)

---

## What was done this session

### Issue 05 (completed this session)
Plan stage fully implemented.

**Files created/changed:**
- `pages/plan.py` — full implementation: Writing Plan extraction from Brain Dump via Claude, ChromaDB retrieval for Content Notes (per-section) and Style Notes, collapsible section editor with reorder/delete/add, Content Notes panel with pin-to-section, "Generate Draft →" navigation
- `requirements.txt` — added `chromadb>=0.5.0`, `sentence-transformers>=2.7.0`
- `WORKING_CONTEXT.md` — updated with Issue 05 build log

**Key decisions:**
- ChromaDB path resolved via `__file__` walk: `pages/ → Code/ → Writing Workflow/ → Claude Code (Personal)/` then into sibling `Notion Second Brain (Code)/data/chroma/`; no hardcoded absolute paths
- `@st.cache_resource` on `_load_embed_model()` and `_load_chroma()` — loaded once per Streamlit process
- Writing Plan extracted as JSON by Claude; code-fence stripping + regex fallback for malformed JSON
- Content Notes: one ChromaDB query per section (top 5), query = section title + bullets; keyed by `str(section_idx)` in `st.session_state.content_notes`
- Style Notes: single fixed-phrase query; top 10 results in `st.session_state.style_notes`
- Section manipulation (`_swap_sections`, `_delete_section`, `_add_section`) re-indexes `content_notes`, `pinned_notes`, `section_expanded` on every structural change
- Key type convention: `section_expanded` uses **int** keys; `content_notes` and `pinned_notes` use **str** keys — consistent throughout
- Pin state = `list[int]` (indices into section's content_notes list) in `st.session_state.pinned_notes`
- "Generate Draft →" embeds pinned note texts into `section["pinned_notes"]` before navigating

**Bugs caught in code review (both fixed):**
- `plan_data = None` initialized before `try` block — prevents `UnboundLocalError` if `st.stop()` is swallowed; same pattern documented for `ai_text` in develop.py
- Selectbox `notes_section_view` clamped to `[0, len(plan)-1]` before render — prevents `StreamlitAPIException` when user deletes the currently-selected section

Committed and pushed: this session's commits on `main`.

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
    05-plan-stage.md                ✅ done (this session)
    06-draft-stage.md               ← NEXT
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
      plan.py                       ✅ full implementation (this session)
      draft.py                      ← placeholder (next)
      publish.py                    ← placeholder
    requirements.txt
    .env.example
    .env                            ← real keys (not committed)
    .claude/launch.json             ← preview server "Writing Workflow" on port 8502
    WORKING_CONTEXT.md              ← full build log of all issues
```

GitHub: https://github.com/mazeem147/azeem-writing-workflow

---

## Session state entering Issue 06

The Draft stage will receive:

- `st.session_state.writing_plan` — `list[dict]` where each dict is:
  ```python
  {
      "title":        str,           # section title
      "bullets":      list[str],     # 3–5 bullet points
      "pinned_notes": list[str],     # full text of notes the user pinned to this section
  }
  ```

- `st.session_state.style_notes` — `list[dict]` where each dict is:
  ```python
  {"text": str, "meta": {"title": str, "created": str, ...}}
  ```
  Top 10 notes from ChromaDB selected for prose style. Used to extract a **Style Fingerprint** before generating the Draft.

- `st.session_state.brain_dump` — the full Develop conversation (still in state)
- `st.session_state.transcript` — the original cleaned transcript (still in state)

---

## Issue 06 spec summary

Full spec: `issues/06-draft-stage.md`

**What to build:**
1. **Style Fingerprint extraction** — one Claude call over the `style_notes` to extract rhetorical patterns: sentence rhythm, paragraph openers, how doubt is introduced, analogy structures. Store in `st.session_state.style_fingerprint`.
2. **Section-by-section Draft generation** — one Claude call per Writing Plan section. Each call gets: section title + bullets, pinned Content Notes for that section, Style Fingerprint, and Voice rules from `skills/writing-voice/SKILL.md`. Display sections as they complete (sequential streaming).
3. **Section display** — each Draft section shown as a Georgia-serif prose block with a hover-triggered "Revise →" button.
4. **Section revision modal** — clicking "Revise →" opens a modal with: the current section text, a feedback textarea (with mic button via `voice_input_widget`), and a "Regenerate" button. Only the targeted section is regenerated. Other sections unchanged.
5. **"Approve Draft →"** button — stores the final Draft in `st.session_state.draft_sections` and navigates to `pages/publish.py` (or `pages/repurposed.py` if Issue 07 comes first).

**Session state produced:**
- `st.session_state.style_fingerprint` — string describing rhetorical patterns
- `st.session_state.draft_sections` — `list[str]`, one prose paragraph per Writing Plan section

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
    timeout=90,
)
resp.raise_for_status()
return resp.json()["choices"][0]["message"]["content"].strip()
```

### Voice input (already built)
```python
from components.voice_input import voice_input_widget
voice_input_widget("revision_feedback")
st.text_area("Feedback", key="revision_feedback", ...)
```

### Page structure
```python
from ui import inject_css, render_sidebar, render_page_header, PALETTE
inject_css()
render_sidebar("draft")
render_page_header("draft", "✍️ Draft", "subtitle")
```

### Python 3.9 constraint
No `X | Y` union types, no `list[str]` generics. No f-strings with backslash expressions — pre-extract variables before building HTML strings.

### HTML safety
User-generated text in `st.markdown(..., unsafe_allow_html=True)` must be wrapped in `html.escape()`.

### UnboundLocalError pattern
Always initialize variables to `None` before a `try` block that assigns them, then guard after:
```python
result = None
with st.spinner("..."):
    try:
        result = do_thing()
    except Exception as exc:
        st.error(str(exc))
        st.stop()
if result is None:
    st.stop()
```

### Selectbox index safety
After any list mutation (delete/reorder), clamp persisted selectbox keys:
```python
stored = st.session_state.get("my_selectbox_key", 0)
if stored >= len(options):
    st.session_state["my_selectbox_key"] = max(0, len(options) - 1)
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

- **`/code-review --effort medium`** — run after implementing to catch runtime-correctness bugs (specifically: same `UnboundLocalError` and selectbox-out-of-range patterns)
- **`/verify`** — use preview server to confirm Draft generation renders sections sequentially and revision modal works
