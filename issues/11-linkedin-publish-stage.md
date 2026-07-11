# 11 — Publish stage: repoint to LinkedIn URL, keep `published_articles` indexing

## What to build

Supersedes the behaviour in issue 08. The Publish stage keeps the Second Brain feedback loop but swaps the platform. The user publishes manually on LinkedIn, then pastes the **LinkedIn article URL** back into the tool. The full article text is chunked and upserted into the `published_articles` collection in the shared Second Brain ChromaDB, using the same `embed_utils.py` helper and `all-MiniLM-L6-v2` embedding model already in use. The LinkedIn URL and publication date are stored as metadata on each chunk, so future Development Sessions can surface past published pieces as Content Notes.

All Substack references are removed from this stage — the URL field, checklist labels, and any copy. The indexing behaviour itself is unchanged.

Note: this ticket supersedes the original handoff note, which proposed removing the publish stage entirely. Decision (confirmed): repoint to LinkedIn and retain indexing.

## Acceptance criteria

- [ ] Publish stage checklist reads: Draft approved, Tweet Thread ready, LinkedIn Article ready, LinkedIn Feed Post ready, LinkedIn URL provided
- [ ] URL input field accepts a LinkedIn article URL (no Substack references anywhere in the stage)
- [ ] On submission, article text is chunked using the same logic as `embed_utils.py`
- [ ] Chunks are upserted into the `published_articles` collection in the shared ChromaDB
- [ ] Each chunk's metadata includes the LinkedIn URL and publication date
- [ ] `published_articles` uses the same `all-MiniLM-L6-v2` embedding model as the Notion notes collection
- [ ] The Notion notes collection is never written to by this operation
- [ ] Confirmation shown after successful indexing
- [ ] `st.session_state` is cleared after successful publication, ready for a new piece

## Blocked by

- Issue 09 — LinkedIn vocabulary in docs
