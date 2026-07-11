# PRD: Azeem's Writing Workflow

## Problem Statement

Azeem can speak compellingly about ideas — in conversation, he explains clearly, connects arguments, and persuades. But this does not translate into writing. The core friction points are:

1. **Activation energy**: a blank page provides nothing to push against. Writing feels like starting from zero.
2. **Trigger-to-capture gap**: ideas are sparked by external stimuli (a YouTube video, a tweet, a workplace experience) in moments away from a laptop. If not captured immediately, the Juice — the emotional and intellectual energy — fades within hours. The opinion survives but the aliveness doesn't.
3. **AI slop problem**: existing AI writing tools produce generic output that doesn't sound like Azeem. His voice is specific: journey structure (not report), analytical and personal in the same sentence, Urdu/Pakistani cadence, thinks out loud, ends open.

The result: a backlog of ideas that never become articles, and a LinkedIn presence that never gets built.

## Solution

A standalone 5-stage desktop tool that turns a voice memo into a publishable LinkedIn Article and its Repurposed Content (Tweet Thread + LinkedIn Feed Post), grounded in Azeem's own notes and written in his actual Voice.

The workflow exploits how Azeem's brain works: it starts with a Trigger, captures the Juice via phone before it fades, then expands the Capture into a full piece through an AI-driven conversation — not a blank page. The output is a Draft the user revises section by section, not a document to rewrite from scratch.

**The 5 stages:**

1. **Transcribe** — Upload the voice memo, transcribe via Whisper, clean with Claude. Uncertain Urdu/English words flagged for manual correction.
2. **Develop** — AI generates Seeder Questions from the Capture. User responds by typing or recording voice. Repeats until user is ready to build the plan.
3. **Plan** — Writing Plan extracted from the Brain Dump. Related notes from the Second Brain surfaced as Content Notes. User reviews and approves before generation.
4. **Draft** — Article generated section by section, grounded in Content Notes and a Style Fingerprint extracted from Style Notes. The Draft is adapted into the LinkedIn Article (the primary output), with Repurposed Content (Tweet Thread + LinkedIn Feed Post) generated in the same session. User revises individual sections via text or voice.
5. **Publish** — User publishes on LinkedIn manually, pastes the LinkedIn article URL back. Tool indexes the article into the `published_articles` ChromaDB collection for future reference.

## User Stories

1. As Azeem, I want to upload a voice memo file so that I can begin a Development Session from a Capture I made on my phone.
2. As Azeem, I want the tool to transcribe my voice memo using Whisper so that I don't have to type out what I said.
3. As Azeem, I want a Claude cleaning pass applied to the transcript so that garbled words and Urdu transliteration errors are fixed before I see them.
4. As Azeem, I want uncertain words highlighted in the transcript so that I can correct only what needs correcting, not read the whole thing.
5. As Azeem, I want to correct an unclear word inline so that I don't have to leave the transcript view to fix it.
6. As Azeem, I want the AI to generate Seeder Questions from my transcript so that the conversation feels reactive to what I actually said, not a generic template.
7. As Azeem, I want to see my original transcript alongside the conversation so that I can refer back to what I said without switching views.
8. As Azeem, I want to respond to Seeder Questions by typing so that I can give detailed answers when I have time to think.
9. As Azeem, I want a mic button next to every text input so that I can speak my answer instead of typing it anywhere in the tool.
10. As Azeem, I want my voice recording transcribed and inserted into the text field so that I can review it before sending.
11. As Azeem, I want to send my response with Enter so that the conversation flows quickly.
12. As Azeem, I want the AI to ask follow-up questions after each of my responses so that the conversation goes deeper than my initial reaction.
13. As Azeem, I want to hit "Build the Plan" whenever I feel ready — with no fixed number of rounds — so that short topics don't get over-questioned and rich topics don't get cut short.
14. As Azeem, I want the Writing Plan generated from my Brain Dump so that the structure reflects what I actually said, not a generic essay format.
15. As Azeem, I want the Writing Plan shown as collapsible sections so that I can see the full shape at a glance and drill into any section.
16. As Azeem, I want to reorder sections in the Writing Plan so that I can adjust the argument flow before generation.
17. As Azeem, I want to delete sections from the Writing Plan so that I can cut ideas that don't belong.
18. As Azeem, I want to add a new section to the Writing Plan so that I can include something I thought of after the conversation.
19. As Azeem, I want related notes from my Second Brain surfaced as Content Notes alongside the Writing Plan so that I can see what I've already thought about this topic.
20. As Azeem, I want Content Notes shown per section so that I know which past thinking is relevant to which part of the article.
21. As Azeem, I want to pull a Content Note into a section so that it gets used during Draft generation.
22. As Azeem, I want a Style Fingerprint extracted from my most representative notes so that the Draft generation uses evidence of how I write, not just rules.
23. As Azeem, I want the Draft generated section by section, matching the approved Writing Plan so that the structure I approved is what I get.
24. As Azeem, I want each Draft section shown separately so that I can evaluate each part on its own.
25. As Azeem, I want to hover a Draft section and see a Revise button so that the revision affordance is always available but never in the way.
26. As Azeem, I want to type revision feedback in a modal so that I can be specific about what's wrong.
27. As Azeem, I want a mic button in the revision modal so that I can speak my feedback instead of typing it.
28. As Azeem, I want only the flagged section to regenerate so that good sections aren't discarded because one section was wrong.
29. As Azeem, I want a Tweet Thread generated from my Draft in Twitter's native attention structure so that it performs on the platform, not just summarises the article.
30. As Azeem, I want the Tweet Thread to open with a provocation, not the article's introduction so that it earns attention from the first tweet.
31. As Azeem, I want a LinkedIn Article and LinkedIn Feed Post generated from the Draft — the Article carrying the full argument and the Feed Post surfacing its core provocation — so that I have ready-to-copy LinkedIn outputs.
32. As Azeem, I want the Tweet Thread, LinkedIn Article, and LinkedIn Feed Post shown in tabs so that the screen doesn't feel cluttered.
33. As Azeem, I want to review the Tweet Thread, LinkedIn Article, and LinkedIn Feed Post before marking as published so that nothing goes live before I've approved everything.
34. As Azeem, I want to paste my LinkedIn article URL after publishing so that the article can be indexed into the Second Brain.
35. As Azeem, I want the published article indexed into a `published_articles` ChromaDB collection so that future Development Sessions can surface it as a Content Note.
36. As Azeem, I want a persistent left-sidebar showing my stage progress so that I always know where I am in the workflow.
37. As Azeem, I want to navigate between stages by clicking the sidebar so that I can revisit a previous stage if I need to.
38. As Azeem, I want to see the current piece's working title in the sidebar so that I know which article I'm working on.
39. As Azeem, I want the tool to run locally on my laptop so that it costs nothing to run beyond API calls.
40. As Azeem, I want the tool to share the Second Brain's ChromaDB so that I don't have to maintain two separate databases.

## Implementation Decisions

- **Inference via OpenRouter** (per ADR-0002): all LLM calls are routed through OpenRouter using its OpenAI-compatible API. A single `OPENROUTER_API_KEY` env var is the only credential needed. The model is configurable per call type — a cheaper model for transcript cleaning, a stronger one for Draft generation — without changing client code. Exception: Whisper audio transcription is called directly via the OpenAI API (`OPENAI_API_KEY`), as OpenRouter does not proxy audio endpoints.

- **Standalone Streamlit app** in `Azeem's Writing Workflow/` directory. Separate from the Second Brain Streamlit app — different entry point, different pages — but shares the Second Brain's ChromaDB at its known path on disk. No data duplication, no syncing required.

- **Shared ChromaDB, separate collection**: the existing Second Brain ChromaDB (`Notion Second Brain (Code)/data/chroma/`) is read for Content Notes and Style Notes retrieval. Published articles are written to a new `published_articles` collection within the same ChromaDB. The Notion notes collection is never written to by this tool.

- **Capture mechanism** (per ADR-0001): iPhone Voice Memos → email to self → manual file upload on laptop. No automatic email polling. No third-party messaging APIs. Upload happens at the start of a Development Session, not at the moment of Capture.

- **Transcription pipeline**: Whisper for speech-to-text (handles Urdu/English code-switching). Followed by a Claude pass that normalises Urdu transliteration errors and marks uncertain words with `[?]`. User corrects only `[?]` markers — not the full transcript.

- **Seeder Questions**: generated by Claude from the cleaned transcript, not from a template. Each question must probe a specific claim or gap in what was said. One question per turn.

- **Voice input**: a mic button sits next to every text input in the app (Develop screen, revision modal). Clicking it records audio, sends to Whisper, and inserts the cleaned transcript into the field. User reviews before submitting.

- **Writing Plan build**: triggered by user explicitly, after any number of conversation rounds. Claude synthesises the full Brain Dump into a structured outline. Simultaneously, ChromaDB is queried for Content Notes (topical relevance) and Style Notes (prose exemplars) from the existing Notion notes collection.

- **Style Fingerprint**: a Claude pass over 5-10 retrieved Style Notes extracts rhetorical patterns — sentence rhythm, paragraph openers, how doubt is introduced, analogy structures. This fingerprint is added to the Draft generation prompt alongside the Voice rules from the writing-voice skill.

- **Draft generation**: one Claude call per Writing Plan section. Content Notes and Style Fingerprint included in each call's context. Sections generated and displayed sequentially.

- **Section revision**: user opens a modal per section, gives typed or voiced feedback. One Claude call regenerates only that section with the feedback appended. Other sections unchanged.

- **LinkedIn Article + Repurposed Content generation**: after Draft approval, the Draft is adapted into the LinkedIn Article (600-900 words, native article structure, portfolio artifact) — the primary publishable output — via one Claude call. Two further Claude calls produce its Repurposed Content: a Tweet Thread (native Twitter attention structure, 8-12 tweets) and a LinkedIn Feed Post (150-200 words, engineered for first-hour engagement, links to the LinkedIn Article). Generated before publishing, not after.

- **Publication Record**: after user pastes the LinkedIn article URL, the full article text is chunked and upserted into the `published_articles` ChromaDB collection using the same `embed_utils.py` helper from the Second Brain codebase. The URL and publication date are stored in metadata.

- **App structure**: single `app.py` entry point using `st.navigation()`. One page per stage. Shared state via `st.session_state` (current piece, transcript, Brain Dump, Writing Plan, Draft sections, Repurposed Content).

## Testing Decisions

A good test verifies what the user experiences, not how the code is structured internally. Tests should assert on outputs given inputs — a transcript goes in, a cleaned transcript with `[?]` markers comes out — not on which Claude prompt was used internally.

The highest seam across the entire pipeline is the **stage transition**: each stage takes an input artifact (audio file, transcript, Brain Dump, Writing Plan, Draft) and produces an output artifact. Tests should assert on the shape and content of these artifacts, not on intermediate Claude calls.

**Modules to test:**

- **Transcription + cleaning**: given a known audio file, assert the transcript is non-empty, `[?]` markers are present for known uncertain words, and the output is valid UTF-8 text. Mock Whisper and Claude API calls.
- **Seeder Question generation**: given a cleaned transcript, assert the output is a non-empty string that contains a question mark. Assert it does not repeat the transcript verbatim.
- **Writing Plan extraction**: given a Brain Dump (multi-turn conversation text), assert the output is a structured list of sections, each with a title and bullet points. Assert section count is between 2 and 8.
- **ChromaDB retrieval**: given a query string, assert Content Notes and Style Notes are returned as non-empty lists of strings. Use the real ChromaDB (it's local and fast) — do not mock.
- **Style Fingerprint extraction**: given a list of Style Notes, assert the fingerprint is a non-empty string describing rhetorical patterns.
- **Draft section generation**: given a section outline + Content Notes + Style Fingerprint, assert the output is a non-empty paragraph in prose (not bullet points). Mock Claude API.
- **LinkedIn Article + Repurposed Content generation**: given a full Draft, assert LinkedIn Article is 600-900 words. Assert Tweet Thread is a list of 8-12 strings each under 280 characters. Assert LinkedIn Feed Post is 150-200 words.
- **Publication Record indexing**: given article text and a LinkedIn article URL, assert the `published_articles` collection in ChromaDB has a new entry with matching metadata. Use the real ChromaDB.

Prior art: `indexer.py` and `embed_utils.py` in the Second Brain codebase for ChromaDB upsert patterns. `pages/chat.py` for the RAG retrieval pattern.

## Out of Scope

- **Automatic email polling**: the tool does not watch an inbox. Upload is always manual.
- **Auto-posting to Twitter or LinkedIn**: the tool generates content and stops. No social API integrations.
- **Scheduling posts**: no queuing or scheduled publishing.
- **Multi-article management**: the tool handles one active piece at a time. No article library or history view in this version.
- **Mobile web interface**: the tool is desktop-only. Phone is used only for Capture (voice memo + email).
- **Re-indexing or syncing Notion notes**: the tool reads from the existing Second Brain ChromaDB. Re-syncing Notion is done from the Second Brain app.
- **Collaboration**: single-user tool, no sharing or commenting.
- **Analytics**: no word count goals, publishing cadence tracking, or audience metrics.

## Further Notes

- The writing-voice skill lives at `skills/writing-voice/SKILL.md` and defines the Voice rules used in Draft generation. Any changes to Voice rules should be made there, not hardcoded in this tool.
- Urdu words in the Brain Dump should be preserved as-is in the Draft — not translated, not removed. The Style Fingerprint should note their presence as part of Azeem's cadence.
- The `published_articles` ChromaDB collection uses the same embedding model (`all-MiniLM-L6-v2`) as the Notion notes collection so both can be queried in a single retrieval call during future Development Sessions.
- The design system for this tool (dark ink ground, amber-gold accent, Georgia serif for article text, system-ui for chrome) is documented in the interactive mockup and should be implemented consistently across all 5 stage screens.
