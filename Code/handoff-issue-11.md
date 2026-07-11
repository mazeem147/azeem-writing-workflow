# Handoff: Azeem's Writing Workflow — Issue 11 (final issue)

**Session date:** 2026-07-11
**Status: ✅ COMPLETE — commit `43a72a9` on `main`.**

Issue 11 was implemented, verified live in the browser, code-reviewed (Standards + Spec, both clean), and committed. All 11 issues are now done — the LinkedIn migration (09-11) is finished and all five stages are LinkedIn-native end to end. This doc is kept as a historical record of the stale-line mapping used to do the work; there is no further next-session task from this handoff.

**What shipped:**
- `pages/publish.py` — checklist split into 5 rows (`article_ok`/`feed_ok` replacing the dead `linkedin_ok`), Substack URL input replaced with a LinkedIn URL input, `gen_warnings` added to the piece-clear list, `stages_ready` extracted (code-review follow-up) to remove a duplicated 4-flag conjunction.
- `pages/draft.py` — dropped a stale "Substack article" mention from the section-generation system prompt (found during implementation, out of this ticket's original scope but fixed in the same commit per user instruction).
- `Code/WORKING_CONTEXT.md` — Issue 11 build-log entry added.

**Verification:** live browser run via a temporary env-gated seed (`SEED_PUBLISH_TEST`, one-time-fire guarded, fully removed before commit) confirmed all 5 checklist rows gate correctly, one chunk indexed into `published_articles` with correct LinkedIn URL/date metadata (checked directly against the real ChromaDB, then deleted), `second_brain` collection count unchanged (1610), confirmation screen survives the state clear, and "Start a New Piece" resets every stage. 7/7 repurpose + 3/3 plan tests still pass.

**Outstanding (not part of Issue 11, flagged for a future session):**
- The `origin` remote URL has a GitHub Personal Access Token embedded in it (see the security note at the bottom of this doc) — still needs rotating.

---

## What was done this session

### Issue 10 (completed + code-reviewed this session)
Repurposed Content stage reworked to produce **three** LinkedIn-native outputs. Committed as `79643a1` on `main`.

**Files changed:**
- `pages/repurpose.py` — removed the old single 3-5 sentence "LinkedIn Post → Substack" output. Added two Claude calls: **LinkedIn Article** (600-900 words, full argument) and **LinkedIn Feed Post** (150-200 words, hook + engagement prompt, references the Article). Tweet Thread retained; its closing-hook prompt now drives to the LinkedIn Article, not Substack.
- `tests/test_repurpose_content.py` — new; AppTest-driven, `httpx.post` mocked.
- `WORKING_CONTEXT.md` — Issue 10 build log entry.

**Key decisions (see WORKING_CONTEXT.md → "Issue 10" for the full list):**
- Session-state keys: `linkedin_post` is **GONE**. Replaced by `linkedin_article` (str) and `linkedin_feed_post` (str). `tweet_thread` unchanged.
- `_strip_em_dashes` (Voice rule) + a new `_strip_markdown` run on every generated Article/Feed Post string (LinkedIn renders `**`/`#` literally).
- Post-review refactor: three generation phases collapsed into `_generate_output(...)`; two single-block tabs into `_render_text_output(...)`.
- Post-review fix: word-count/tweet-count warnings used to flash behind `st.rerun()` and never reached the user. Now persisted into a new `st.session_state.gen_warnings` dict and rendered in the display phase.
- `Substack` appears nowhere in `repurpose.py` (code, strings, or UI).

**Verification:** 7/7 repurpose AppTests pass; 3/3 plan tests still pass. Full live browser run (real Whisper/Claude/OpenRouter) was done for the pre-refactor version; the refactor is behavior-preserving and covered by the AppTests (which run the real page).

---

## ✅ Resolved: `pages/publish.py` staleness after Issue 10

Issue 10 renamed `linkedin_post` → `linkedin_article` + `linkedin_feed_post`, and Issue 11 (this commit) caught `publish.py` up. Kept below as a record of the exact mapping that was applied — all rows in this table are now done in `pages/publish.py`.

| Line(s) | Current (stale) | Issue 11 target |
|---|---|---|
| 193 | `linkedin_ok = bool(st.session_state.get("linkedin_post"))` | split into `article_ok` (`linkedin_article`) + `feed_ok` (`linkedin_feed_post`) |
| 196-201 | `st.text_input("Substack URL", key="substack_url", placeholder=…substack…, help=…Substack…)` | LinkedIn URL label/placeholder/help/key |
| 212-217 | checklist: `"LinkedIn Post ready"`, `"Substack URL provided"` | `"LinkedIn Article ready"`, `"LinkedIn Feed Post ready"`, `"LinkedIn URL provided"` (5 rows total) |
| 235 | `can_publish = draft_ok and tweet_ok and linkedin_ok and url_ok` | include both `article_ok` and `feed_ok` |
| 243-244 | hint mentions "Substack URL" | LinkedIn URL |
| 117 | `_PIECE_KEYS` includes `"linkedin_post"` | replace with `"linkedin_article"`, `"linkedin_feed_post"`, and add `"gen_warnings"` |
| 175 | `st.session_state.pop("substack_url", …)` in "Start a New Piece" | pop the new LinkedIn URL key |

**Good news — the hard part is already done and matches Issue 11's criteria unchanged:** the chunking (`_chunk_text`, 350 words / 50 overlap), embedding (`all-MiniLM-L6-v2` via `@st.cache_resource`), and upsert into the **separate** `published_articles` collection (`_index_article`, idempotent per-URL via `md5(url)[:12]`, metadata `{url, published_date, title, chunk_index}`) were all implemented in Issue 08 and already satisfy Issue 11's ACs. The Notion notes collection is never written to. So **Issue 11 is essentially a relabel/repoint, not a rebuild** — don't rewrite the indexing.

---

## Session state entering Issue 11

The Publish stage will receive:

- `st.session_state.draft_sections` — `list[str]`, one prose block per section. Full article: `"\n\n".join(draft_sections)`.
- `st.session_state.draft_approved` — `bool` True.
- `st.session_state.tweet_thread` — `list[str]`, 8-12 tweets.
- `st.session_state.linkedin_article` — `str`, 600-900 words. **(replaces `linkedin_post`)**
- `st.session_state.linkedin_feed_post` — `str`, 150-200 words. **(replaces `linkedin_post`)**
- `st.session_state.gen_warnings` — `dict[state_key → warning str or None]` (new in Issue 10; add to the piece-clear list).
- `st.session_state.working_title` — `str`, working title.
- `st.session_state.writing_plan` — `list[dict]` `{"title", "bullets", "pinned_notes"}`.

---

## Issue 11 spec summary

Full spec: `issues/11-linkedin-publish-stage.md` — read it first. Supersedes Issue 08.

**Acceptance criteria:**
- Checklist reads: Draft approved, Tweet Thread ready, LinkedIn Article ready, LinkedIn Feed Post ready, LinkedIn URL provided.
- URL field accepts a LinkedIn article URL; **no Substack references anywhere** in the stage.
- On submit: chunk article text (same logic as `embed_utils.py`), upsert into `published_articles`, metadata includes the LinkedIn URL + publication date, `all-MiniLM-L6-v2` model, Notion notes collection never written.
- Confirmation shown; `st.session_state` cleared after success, ready for a new piece.

No LLM calls needed — this stage is ChromaDB + UI only.

---

## Patterns to follow (unchanged from prior issues)

- **Python 3.9**: no `X | Y` unions, no `list[str]` generics, no f-strings with backslash expressions — pre-extract variables before building HTML strings.
- **HTML safety**: user-supplied text (the LinkedIn URL, working title) in `unsafe_allow_html` blocks must go through `html.escape()` — already done for the existing URL/title.
- **Guard/None pattern**: `result = None` before the `try`; `if result is None: st.stop()` after.
- **ChromaDB path**: resolved via `__file__` walk (already correct in `publish.py`) — never hardcode.
- **Confirmation-survives-clear**: the confirmation dict lives in its own `publish_confirmation` key (NOT in the clear list) so it survives the rerun where piece state is wiped. Render order matters: confirmation block `st.stop()`s before the guard. Keep this structure.

## Design system tokens
See WORKING_CONTEXT.md / `ui.py` `PALETTE`. Ink `#0d0c14`, sidebar `#1a1826` (no PALETTE key), gold `#c9a96e`, text `#e8e4dc`, muted `#9b9690`, done `#4a9e6b`, error `#e05252`, border `#2e2c3a`.

## How to run
```bash
cd "/Users/mazeem147/Claude Code (Personal)/Azeem's Writing Workflow/Code"
.venv/bin/streamlit run app.py --server.port 8502
```
Or `preview_start` with server name `"Writing Workflow"` (`.claude/launch.json`). Note: the in-app preview browser can't drive native file-pickers — to exercise the full pipeline live, either use the Claude-in-Chrome surface for the upload step, or add a temporary env-gated session-state seed on `publish.py` (seed `draft_sections`, `draft_approved`, `tweet_thread`, `linkedin_article`, `linkedin_feed_post`) and remove it before committing.

## Tests
Run: `.venv/bin/python tests/test_repurpose_content.py` and `.venv/bin/python tests/test_plan_section_ops.py` (self-running; no pytest installed in the venv). A `tests/test_publish_*.py` for Issue 11 could assert the checklist gates on the new keys and that indexing writes only to `published_articles` (the PRD says use the real local ChromaDB, don't mock it).

## Done — no further build session needed off this handoff
Issue 11 was implemented, verified, code-reviewed, and committed this session (see status note at the top). All 11 issues are complete. Any future work is a new initiative, not a continuation of this handoff — the only carry-over item is the security note below.

## Repo / git
- GitHub: https://github.com/mazeem147/azeem-writing-workflow (remote `origin`, branch `main`).
- Last commit: `43a72a9` — "Issue 11: LinkedIn Publish stage (repoint from Substack URL)".
- Convention: each issue is committed directly to `main`.
- **Security note (flag to the user, still outstanding):** the `origin` remote URL has a GitHub Personal Access Token embedded in it (`git remote -v`). Consider rotating that token and switching to a credential helper / SSH so the secret isn't stored in `.git/config`.
