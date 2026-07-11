import os
import json
import re
import html as _html
import httpx
import streamlit as st
from ui import inject_css, render_sidebar, render_page_header, PALETTE

inject_css()
render_sidebar("plan")
render_page_header("plan", "📋 Plan", "Review your Writing Plan and surface related notes from your Second Brain.")

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.get("brain_dump"):
    st.markdown(
        "<p style='color:" + PALETTE["muted"] + "'>No Brain Dump found. "
        "Please complete the <strong>Develop</strong> stage first.</p>",
        unsafe_allow_html=True,
    )
    if st.button("← Go to Develop"):
        st.switch_page("pages/develop.py")
    st.stop()

# ── ChromaDB path ─────────────────────────────────────────────────────────────
_PAGES_DIR  = os.path.dirname(os.path.abspath(__file__))
_CODE_DIR   = os.path.dirname(_PAGES_DIR)
_WF_DIR     = os.path.dirname(_CODE_DIR)
_WORKSPACE  = os.path.dirname(_WF_DIR)
CHROMA_DIR  = os.path.join(_WORKSPACE, "Notion Second Brain (Code)", "data", "chroma")


@st.cache_resource
def _load_embed_model():
    from sentence_transformers import SentenceTransformer  # noqa: PLC0415
    return SentenceTransformer("all-MiniLM-L6-v2")


@st.cache_resource
def _load_chroma():
    import chromadb  # noqa: PLC0415
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection("second_brain")


# ── LLM helper ────────────────────────────────────────────────────────────────
def _call_claude(messages, timeout=90):
    key = os.environ["OPENROUTER_API_KEY"]
    resp = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
        json={"model": "anthropic/claude-sonnet-4-5", "messages": messages},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── Writing Plan extraction ───────────────────────────────────────────────────
def _extract_writing_plan(brain_dump):
    turns = []
    for turn in brain_dump:
        role_label = "AI" if turn["role"] == "ai" else "Writer"
        turns.append(role_label + ": " + turn["text"])
    dump_text = "\n\n".join(turns)

    system = (
        "You are a writing plan architect. Extract a structured Writing Plan "
        "from the Brain Dump below.\n\n"
        "The Brain Dump is a conversation between Azeem (the writer) and an AI "
        "thinking partner. Synthesise the writer's ideas, arguments, stories, "
        "and positions into a structured article outline.\n\n"
        "Rules:\n"
        "- 2 to 8 sections total\n"
        "- Each section has a clear, specific title and 3-5 bullet points\n"
        "- Preserve the writer's own examples, analogies, and specific language\n"
        "- Follow the logical arc of the argument, not a generic essay structure\n"
        "- Return ONLY valid JSON, no preamble, no explanation, no code fences\n\n"
        'Format: [{"title": "Section title", "bullets": ["bullet 1", "bullet 2", "bullet 3"]}, ...]'
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Brain Dump:\n\n" + dump_text},
    ]
    raw = _call_claude(messages).strip()

    # Strip markdown code fences if Claude wrapped the JSON
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:])
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            plan = json.loads(match.group())
        else:
            raise ValueError("Could not parse Writing Plan JSON. Response was:\n" + raw[:300])

    if not isinstance(plan, list) or len(plan) == 0:
        raise ValueError("Writing Plan must be a non-empty list of sections.")

    # Normalise any missing fields
    for idx, section in enumerate(plan):
        if "title" not in section or not section["title"]:
            section["title"] = "Section " + str(idx + 1)
        if "bullets" not in section or not isinstance(section["bullets"], list):
            section["bullets"] = []

    return plan


# ── ChromaDB retrieval ────────────────────────────────────────────────────────
def _retrieve_notes(query, n=5):
    model      = _load_embed_model()
    collection = _load_chroma()
    embedding  = model.encode([query]).tolist()
    results    = collection.query(query_embeddings=embedding, n_results=n)
    return [
        {"text": doc, "meta": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


# ── Section manipulation helpers ──────────────────────────────────────────────
def _swap_sections(i, j):
    plan = st.session_state.writing_plan
    plan[i], plan[j] = plan[j], plan[i]

    for d in (st.session_state.content_notes, st.session_state.pinned_notes):
        si, sj = str(i), str(j)
        d[si], d[sj] = d.get(sj, []), d.get(si, [])

    se = st.session_state.section_expanded
    se[i], se[j] = se.get(j, True), se.get(i, True)


def _delete_section(idx):
    plan = st.session_state.writing_plan
    n_old = len(plan)
    plan.pop(idx)

    new_cn, new_pn, new_se = {}, {}, {}
    for j in range(n_old - 1):
        old_j = j if j < idx else j + 1
        new_cn[str(j)] = st.session_state.content_notes.get(str(old_j), [])
        new_pn[str(j)] = st.session_state.pinned_notes.get(str(old_j), [])
        new_se[j]      = st.session_state.section_expanded.get(old_j, True)

    st.session_state.content_notes  = new_cn
    st.session_state.pinned_notes   = new_pn
    st.session_state.section_expanded = new_se


def _add_section(title):
    plan = st.session_state.writing_plan
    idx  = len(plan)
    plan.append({"title": title, "bullets": []})
    st.session_state.content_notes[str(idx)]  = []
    st.session_state.pinned_notes[str(idx)]   = []
    st.session_state.section_expanded[idx]    = True


def _add_section_from_input():
    """on_click callback for the "+ Add" button.

    Callbacks run BEFORE widgets are instantiated on the resulting rerun, so
    clearing the new_section_title widget key here is legal. Doing the same
    reset inside the button's if-block (after st.text_input was already created
    this run) is what raised StreamlitAPIException. Same fix as develop.py's
    _submit_develop_response.
    """
    raw = st.session_state.get("new_section_title", "")
    title_to_add = raw.strip() if raw else "New Section"
    _add_section(title_to_add)
    st.session_state["new_section_title"] = ""


# ── Session state defaults ────────────────────────────────────────────────────
if "writing_plan" not in st.session_state:
    st.session_state.writing_plan = None
if "content_notes" not in st.session_state:
    st.session_state.content_notes = {}     # str(section_idx) -> list of note dicts
if "style_notes" not in st.session_state:
    st.session_state.style_notes = []
if "pinned_notes" not in st.session_state:
    st.session_state.pinned_notes = {}      # str(section_idx) -> list of int indices
if "section_expanded" not in st.session_state:
    st.session_state.section_expanded = {}  # int section_idx -> bool

# ── Generate on first entry ───────────────────────────────────────────────────
if st.session_state.writing_plan is None:
    plan_data = None   # guard against UnboundLocalError if st.stop() is swallowed
    with st.spinner("Extracting Writing Plan from your Brain Dump…"):
        try:
            plan_data = _extract_writing_plan(st.session_state.brain_dump)
        except Exception as exc:
            st.error("Writing Plan generation failed: " + str(exc))
            st.stop()

    if plan_data is None:
        st.stop()
    st.session_state.writing_plan = plan_data
    for k in range(len(plan_data)):
        st.session_state.section_expanded[k] = True

    with st.spinner("Searching your Second Brain for related notes…"):
        for k, section in enumerate(plan_data):
            try:
                query = section["title"] + ". " + " ".join(section["bullets"])
                st.session_state.content_notes[str(k)] = _retrieve_notes(query, n=5)
            except Exception:
                st.session_state.content_notes[str(k)] = []

        try:
            style_query = (
                "personal reflection opinion I believe I think first-person "
                "experience story voice analytical"
            )
            st.session_state.style_notes = _retrieve_notes(style_query, n=10)
        except Exception:
            st.session_state.style_notes = []

    st.rerun()

# ── From here writing_plan is populated ──────────────────────────────────────
plan = st.session_state.writing_plan

# ── Two-column layout ─────────────────────────────────────────────────────────
col_plan, col_notes = st.columns([3, 2])

# ── Left: Writing Plan ────────────────────────────────────────────────────────
with col_plan:
    gold   = PALETTE["gold"]
    muted  = PALETTE["muted"]
    text   = PALETTE["text"]
    border = PALETTE["border"]

    st.markdown(
        "<p style='color:" + gold + ";font-weight:600;font-family:Georgia,serif;"
        "font-size:1rem;margin-bottom:0.75rem'>Writing Plan</p>",
        unsafe_allow_html=True,
    )

    last = len(plan) - 1
    for i, section in enumerate(plan):
        expanded = st.session_state.section_expanded.get(i, True)

        # Action-button columns must be wide enough for the styled buttons
        # (the ↑/↓ buttons render ~40px via ui.py's button padding). The old
        # [1, 9, 1, 1, 1] gave them only ~19px, so buttons overflowed their
        # columns and overlapped. These weights give ~46px action columns.
        c_tog, c_title, c_up, c_dn, c_del = st.columns([2, 10, 3, 3, 3])

        with c_tog:
            tog = st.button(
                "▼" if expanded else "▶",
                key="tog" + str(i),
                help="Collapse / expand",
            )
        with c_title:
            num  = str(i + 1) + ". "
            safe = _html.escape(section["title"])
            st.markdown(
                "<p style='color:" + text + ";font-family:Georgia,serif;"
                "font-size:0.95rem;font-weight:600;margin:0.3rem 0;line-height:1.4'>"
                "<span style='color:" + gold + "'>" + num + "</span>" + safe + "</p>",
                unsafe_allow_html=True,
            )
        with c_up:
            up = st.button("↑", key="up" + str(i), disabled=(i == 0))
        with c_dn:
            dn = st.button("↓", key="dn" + str(i), disabled=(i == last))
        with c_del:
            dl = st.button("✕", key="dl" + str(i), help="Delete section")

        if tog:
            st.session_state.section_expanded[i] = not expanded
            st.rerun()
        if up:
            _swap_sections(i, i - 1)
            st.rerun()
        if dn:
            _swap_sections(i, i + 1)
            st.rerun()
        if dl:
            _delete_section(i)
            st.rerun()

        if expanded and section["bullets"]:
            bullets_html = (
                "<ul style='margin:0.1rem 0 0.65rem 1.25rem;"
                "font-family:Georgia,serif;font-size:0.88rem;"
                "color:" + muted + ";line-height:1.75;padding:0'>"
            )
            for bullet in section["bullets"]:
                bullets_html += "<li>" + _html.escape(bullet) + "</li>"
            bullets_html += "</ul>"
            st.markdown(bullets_html, unsafe_allow_html=True)
        elif expanded:
            st.markdown(
                "<p style='color:" + muted + ";font-size:0.8rem;"
                "font-style:italic;margin:0 0 0.5rem 1rem'>No bullets yet.</p>",
                unsafe_allow_html=True,
            )

        if i < last:
            st.markdown(
                "<hr style='margin:0.25rem 0;border:none;"
                "border-top:1px solid " + border + "'>",
                unsafe_allow_html=True,
            )

    # ── Add section ───────────────────────────────────────────────────────────
    st.markdown(
        "<div style='margin-top:1rem'></div>",
        unsafe_allow_html=True,
    )
    add_col_input, add_col_btn = st.columns([4, 1])
    with add_col_input:
        # Value is read from session_state["new_section_title"] inside the
        # on_click callback, so the return value is intentionally not captured.
        st.text_input(
            "New section",
            placeholder="New section title…",
            key="new_section_title",
            label_visibility="collapsed",
        )
    with add_col_btn:
        st.button("+ Add", key="add_section_btn", on_click=_add_section_from_input)

# ── Right: Content Notes ──────────────────────────────────────────────────────
with col_notes:
    gold   = PALETTE["gold"]
    muted  = PALETTE["muted"]
    text   = PALETTE["text"]
    border = PALETTE["border"]
    done   = PALETTE["done"]

    st.markdown(
        "<p style='color:" + gold + ";font-weight:600;font-family:Georgia,serif;"
        "font-size:1rem;margin-bottom:0.75rem'>Content Notes</p>",
        unsafe_allow_html=True,
    )

    if not plan:
        st.markdown(
            "<p style='color:" + muted + ";font-size:0.85rem'>"
            "Add sections to see related notes.</p>",
            unsafe_allow_html=True,
        )
    else:
        section_labels = [str(k + 1) + ". " + s["title"] for k, s in enumerate(plan)]
        # Clamp persisted index to valid range after any section deletions
        _stored = st.session_state.get("notes_section_view", 0)
        if _stored >= len(plan):
            st.session_state["notes_section_view"] = max(0, len(plan) - 1)
        view_idx = st.selectbox(
            "Section",
            options=list(range(len(plan))),
            format_func=lambda k: section_labels[k],
            key="notes_section_view",
            label_visibility="collapsed",
        )

        notes  = st.session_state.content_notes.get(str(view_idx), [])
        pinned = st.session_state.pinned_notes.get(str(view_idx), [])

        if not notes:
            st.markdown(
                "<p style='color:" + muted + ";font-size:0.85rem;font-style:italic'>"
                "No notes retrieved for this section.</p>",
                unsafe_allow_html=True,
            )
        else:
            for j, note in enumerate(notes):
                is_pinned = j in pinned

                note_title = note["meta"].get("title", "Untitled")
                note_date  = note["meta"].get("created", "")[:10]
                note_text  = note["text"]
                excerpt    = note_text[:180] + "…" if len(note_text) > 180 else note_text

                card_bg     = "#1a2e22" if is_pinned else PALETTE["ink_mid"]
                card_border = done if is_pinned else border

                safe_note_title   = _html.escape(note_title)
                safe_note_date    = _html.escape(note_date)
                safe_note_excerpt = _html.escape(excerpt).replace("\n", " ")

                card_html = (
                    "<div style='margin-bottom:0.6rem;padding:0.6rem 0.7rem;"
                    "background:" + card_bg + ";"
                    "border:1px solid " + card_border + ";"
                    "border-radius:6px'>"
                    "<p style='margin:0 0 1px;font-size:0.78rem;font-weight:600;"
                    "color:" + text + ";font-family:system-ui'>"
                    + safe_note_title + "</p>"
                    "<p style='margin:0 0 4px;font-size:0.68rem;color:" + muted + "'>"
                    + safe_note_date + "</p>"
                    "<p style='margin:0;font-size:0.78rem;color:" + muted + ";"
                    "font-family:Georgia,serif;line-height:1.5'>"
                    + safe_note_excerpt + "</p>"
                    "</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

                pin_key   = "pin_" + str(view_idx) + "_" + str(j)
                pin_label = "📌 Pinned ✓" if is_pinned else "📌 Pin"
                if st.button(pin_label, key=pin_key):
                    current = list(st.session_state.pinned_notes.get(str(view_idx), []))
                    if j in current:
                        current.remove(j)
                    else:
                        current.append(j)
                    st.session_state.pinned_notes[str(view_idx)] = current
                    st.rerun()

# ── Bottom bar ────────────────────────────────────────────────────────────────
st.markdown("---")

n_pinned   = sum(len(v) for v in st.session_state.pinned_notes.values())
n_sections = len(plan)
note_word  = "note" if n_pinned == 1 else "notes"
sec_word   = "section" if n_sections == 1 else "sections"
hint       = str(n_sections) + " " + sec_word + " · " + str(n_pinned) + " " + note_word + " pinned"

col_hint, col_btn = st.columns([3, 1])
with col_hint:
    st.markdown(
        "<p style='color:" + PALETTE["muted"] + ";font-size:0.85rem;padding-top:6px'>"
        + hint + "</p>",
        unsafe_allow_html=True,
    )
with col_btn:
    if st.button("Generate Draft →", type="primary", disabled=(n_sections == 0)):
        # Embed pinned note texts into the plan before navigating
        final_plan = []
        for k, section in enumerate(plan):
            pinned_idxs  = st.session_state.pinned_notes.get(str(k), [])
            notes_for_sec = st.session_state.content_notes.get(str(k), [])
            pinned_texts = [
                notes_for_sec[idx]["text"]
                for idx in pinned_idxs
                if idx < len(notes_for_sec)
            ]
            final_plan.append({
                "title":        section["title"],
                "bullets":      section["bullets"],
                "pinned_notes": pinned_texts,
            })
        st.session_state.writing_plan = final_plan
        st.switch_page("pages/draft.py")
