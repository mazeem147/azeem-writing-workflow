import os
import html as _html
import hashlib
import datetime
import streamlit as st
from ui import inject_css, render_sidebar, render_page_header, PALETTE

inject_css()
render_sidebar("publish")
render_page_header(
    "publish",
    "🚀 Publish",
    "Index your published article into the Second Brain.",
)

# ── ChromaDB path (same resolution as plan.py — sibling directory) ─────────────
_PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
_CODE_DIR  = os.path.dirname(_PAGES_DIR)
_WF_DIR    = os.path.dirname(_CODE_DIR)
_WORKSPACE = os.path.dirname(_WF_DIR)
CHROMA_DIR = os.path.join(_WORKSPACE, "Notion Second Brain (Code)", "data", "chroma")

# Chunking constants — mirror embed_utils.py in the Second Brain codebase.
CHUNK_SIZE_WORDS    = 350
CHUNK_OVERLAP_WORDS = 50
PUBLISHED_COLLECTION = "published_articles"


@st.cache_resource
def _load_embed_model():
    from sentence_transformers import SentenceTransformer  # noqa: PLC0415
    return SentenceTransformer("all-MiniLM-L6-v2")


@st.cache_resource
def _load_published_collection():
    """Load (or create) the published_articles collection.

    Never touches the Notion notes collection ("second_brain") — this operation
    only ever writes to a dedicated, separate collection in the shared ChromaDB.
    """
    import chromadb  # noqa: PLC0415
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(
        PUBLISHED_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def _chunk_text(text, chunk_size=CHUNK_SIZE_WORDS, overlap=CHUNK_OVERLAP_WORDS):
    """Word-based chunking with overlap — identical logic to embed_utils.chunk_text."""
    words = text.split()
    if not words:
        return []
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def _index_article(full_text, url, title):
    """Chunk the article and upsert every chunk into published_articles.

    Returns (n_chunks, published_date). Idempotent per URL: the doc-id prefix is
    derived from the URL, so re-publishing the same article overwrites its chunks
    rather than duplicating them.
    """
    model      = _load_embed_model()
    collection = _load_published_collection()

    chunks = _chunk_text(full_text)
    if not chunks:
        raise ValueError("Article text is empty — nothing to index.")

    pub_date = datetime.date.today().isoformat()
    prefix   = hashlib.md5(url.encode("utf-8")).hexdigest()[:12]

    embeddings = model.encode(chunks, show_progress_bar=False).tolist()
    ids  = [prefix + "__chunk" + str(i) for i in range(len(chunks))]
    metas = [
        {
            "url":            url,
            "published_date": pub_date,
            "title":          title,
            "chunk_index":    i,
        }
        for i in range(len(chunks))
    ]
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metas,
    )
    return len(chunks), pub_date


# Keys that belong to the current piece — cleared once it's published.
_PIECE_KEYS = [
    # Transcribe stage
    "transcript", "transcript_raw", "transcript_clean", "corrections",
    "last_uploaded_file", "working_title",
    # Develop stage
    "conversation", "seeder_requested", "awaiting_ai", "develop_response",
    "brain_dump",
    # Plan stage
    "writing_plan", "content_notes", "style_notes", "pinned_notes",
    "section_expanded", "notes_section_view", "new_section_title",
    # Draft stage
    "style_fingerprint", "draft_sections", "draft_approved",
    "modal_section_idx", "revision_feedback",
    # Repurpose stage
    "tweet_thread", "linkedin_article", "linkedin_feed_post", "gen_warnings",
]


def _clear_piece_state():
    for key in _PIECE_KEYS:
        st.session_state.pop(key, None)


gold    = PALETTE["gold"]
muted   = PALETTE["muted"]
text    = PALETTE["text"]
done    = PALETTE["done"]
border  = PALETTE["border"]
ink_mid = PALETTE["ink_mid"]

# ── Confirmation screen ────────────────────────────────────────────────────────
# Shown after a successful index. Stored separately from the piece state so it
# survives the rerun in which the piece keys are cleared.
_conf = st.session_state.get("publish_confirmation")
if _conf:
    safe_title = _html.escape(str(_conf.get("title", "Untitled piece")))
    safe_url   = _html.escape(str(_conf.get("url", "")))
    n_chunks   = str(_conf.get("chunks", 0))
    pub_date   = _html.escape(str(_conf.get("published_date", "")))
    chunk_word = "chunk" if _conf.get("chunks", 0) == 1 else "chunks"

    st.markdown(
        "<div style='text-align:center;padding:2rem 1rem 1rem'>"
        "<div style='font-size:2.5rem;margin-bottom:0.5rem'>✅</div>"
        "<p style='font-family:Georgia,serif;font-size:1.35rem;color:" + gold + ";"
        "margin:0 0 0.35rem'>Published &amp; indexed</p>"
        "<p style='color:" + muted + ";font-size:0.9rem;margin:0'>"
        "Your article is now part of your Second Brain. Future Development Sessions "
        "can surface it as a Content Note.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='background:" + ink_mid + ";border:1px solid " + border + ";"
        "border-radius:8px;padding:1rem 1.25rem;margin:1rem 0'>"
        "<p style='margin:0 0 0.4rem;font-family:Georgia,serif;font-size:1.05rem;color:" + text + "'>"
        + safe_title + "</p>"
        "<p style='margin:0 0 0.3rem;font-size:0.82rem;color:" + muted + "'>"
        "<span style='color:" + gold + "'>↗</span> "
        "<a href='" + safe_url + "' target='_blank' style='color:" + gold + "'>" + safe_url + "</a></p>"
        "<p style='margin:0;font-size:0.78rem;color:" + muted + "'>"
        "Indexed into <code>published_articles</code> · " + n_chunks + " " + chunk_word
        + " · " + pub_date + "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    _, btn_col = st.columns([2, 1])
    with btn_col:
        if st.button("Start a New Piece →", type="primary"):
            st.session_state.pop("publish_confirmation", None)
            st.session_state.pop("linkedin_url", None)
            st.switch_page("pages/transcribe.py")
    st.stop()

# ── Guard ──────────────────────────────────────────────────────────────────────
if not st.session_state.get("draft_sections"):
    st.markdown(
        "<p style='color:" + muted + "'>No Draft found. "
        "Please complete the <strong>Draft</strong> stage first.</p>",
        unsafe_allow_html=True,
    )
    if st.button("← Go to Draft"):
        st.switch_page("pages/draft.py")
    st.stop()

# ── Readiness state ──────────────────────────────────────────────────────────
draft_ok   = bool(st.session_state.get("draft_approved"))
tweet_ok   = bool(st.session_state.get("tweet_thread"))
article_ok = bool(st.session_state.get("linkedin_article"))
feed_ok    = bool(st.session_state.get("linkedin_feed_post"))

# ── LinkedIn URL input ───────────────────────────────────────────────────────
raw_url = st.text_input(
    "LinkedIn URL",
    placeholder="https://www.linkedin.com/pulse/your-article",
    key="linkedin_url",
    help="Publish the LinkedIn Article first, then paste the live URL here.",
)
url = (raw_url or "").strip()
url_ok = url.startswith("http://") or url.startswith("https://")

# ── Approval checklist ───────────────────────────────────────────────────────
st.markdown(
    "<p style='color:" + gold + ";font-weight:600;font-family:Georgia,serif;"
    "font-size:1rem;margin:1.25rem 0 0.5rem'>Before you publish</p>",
    unsafe_allow_html=True,
)

_CHECKLIST = [
    (draft_ok,   "Draft approved"),
    (tweet_ok,   "Tweet Thread ready"),
    (article_ok, "LinkedIn Article ready"),
    (feed_ok,    "LinkedIn Feed Post ready"),
    (url_ok,     "LinkedIn URL provided"),
]

checklist_html = "<div style='margin-bottom:0.5rem'>"
for is_done, label in _CHECKLIST:
    mark       = "✓" if is_done else "○"
    mark_color = done if is_done else muted
    lbl_color  = text if is_done else muted
    checklist_html += (
        "<div style='display:flex;align-items:center;gap:0.6rem;padding:0.3rem 0'>"
        "<span style='color:" + mark_color + ";font-size:0.95rem;width:1rem;"
        "text-align:center'>" + mark + "</span>"
        "<span style='color:" + lbl_color + ";font-size:0.9rem'>"
        + _html.escape(label) + "</span>"
        "</div>"
    )
checklist_html += "</div>"
st.markdown(checklist_html, unsafe_allow_html=True)

stages_ready = draft_ok and tweet_ok and article_ok and feed_ok
can_publish  = stages_ready and url_ok

st.markdown("---")

hint_col, btn_col = st.columns([3, 1])
with hint_col:
    if not stages_ready:
        hint = "Complete the earlier stages before publishing."
    elif not url_ok:
        hint = "Paste your live LinkedIn URL above to enable publishing."
    else:
        hint = "Ready — this will index the article into your Second Brain."
    st.markdown(
        "<p style='color:" + muted + ";font-size:0.85rem;padding-top:6px'>"
        + _html.escape(hint) + "</p>",
        unsafe_allow_html=True,
    )
with btn_col:
    if st.button("Publish & Index →", type="primary", disabled=not can_publish):
        title = str(st.session_state.get("working_title", "Untitled piece"))
        body  = "\n\n".join(st.session_state.draft_sections)
        full_text = title + "\n\n" + body

        result = None
        with st.spinner("Chunking and indexing your article…"):
            try:
                result = _index_article(full_text, url, title)
            except Exception as exc:
                st.error("Indexing failed: " + str(exc))
                st.stop()

        if result is None:
            st.stop()

        n_chunks, pub_date = result
        st.session_state.publish_confirmation = {
            "title":          title,
            "url":            url,
            "chunks":         n_chunks,
            "published_date": pub_date,
        }
        _clear_piece_state()
        st.rerun()
