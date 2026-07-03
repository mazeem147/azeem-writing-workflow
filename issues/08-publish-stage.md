# 08 — Publish stage: index article into `published_articles` ChromaDB collection

## What to build

The final stage closes the loop between the Writing Workflow and the Second Brain. The user publishes manually on Substack, then pastes the URL back into the tool. The full article text is chunked and upserted into a `published_articles` collection within the existing Second Brain ChromaDB (`Notion Second Brain (Code)/data/chroma/`), using the same `embed_utils.py` helper and `all-MiniLM-L6-v2` embedding model already in use. The Substack URL and publication date are stored as metadata on each chunk. A checklist on the screen shows the user what's been approved and what's pending before they submit the URL.

## Acceptance criteria

- [ ] Publish stage shows a checklist: Draft approved, Tweet Thread ready, LinkedIn Post ready, Substack URL provided
- [ ] URL input field accepts a Substack URL
- [ ] On submission, article text is chunked using the same chunking logic as `embed_utils.py`
- [ ] Chunks are upserted into a `published_articles` collection in the shared ChromaDB
- [ ] Each chunk's metadata includes the Substack URL and publication date
- [ ] `published_articles` collection uses the same `all-MiniLM-L6-v2` embedding model as the Notion notes collection
- [ ] Confirmation shown after successful indexing
- [ ] The Notion notes collection is never written to by this operation
- [ ] `st.session_state` is cleared after successful publication, ready for a new piece

## Blocked by

- Issue 07 — Repurposed Content
