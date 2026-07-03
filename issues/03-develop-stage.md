# 03 — Develop stage: Seeder Questions + typed conversation

## What to build

The Develop stage turns the cleaned transcript into a Brain Dump through open-ended AI conversation. On entering the stage, Claude (via OpenRouter) reads the transcript and generates the first Seeder Question — a specific, probing question derived from something the user actually said, not a generic template. The user types their answer and submits. Claude asks a follow-up. This continues for as many rounds as the user wants. A persistent "Build the Plan →" button is always visible and navigates to the Plan stage when clicked.

The stage layout is a split panel: the cleaned transcript on the left for reference, the conversation on the right. The full conversation history (all questions and answers) is stored in `st.session_state` as the Brain Dump for use by the Plan stage.

## Acceptance criteria

- [ ] On stage entry, Claude generates the first Seeder Question from the transcript (via OpenRouter)
- [ ] Seeder Question is derived from a specific claim or gap in the transcript — not generic
- [ ] Split-panel layout: transcript (left, read-only) and conversation (right)
- [ ] User types an answer and submits with Enter or the Send button
- [ ] Claude generates a follow-up question after each user response
- [ ] Full conversation history shown in the conversation panel, oldest at top
- [ ] "Build the Plan →" button is always visible and available regardless of how many rounds have occurred
- [ ] Full Brain Dump (all Q&A turns) stored in `st.session_state` on clicking "Build the Plan →"
- [ ] Loading state shown while Claude is generating a question

## Blocked by

- Issue 02 — Transcribe stage
