# 06 — Draft stage: section-by-section generation + section revision

## What to build

The Draft stage generates the article and handles targeted revision. On entry, a Style Fingerprint is extracted by Claude (via OpenRouter) from the Style Notes retrieved in the Plan stage — capturing sentence rhythms, paragraph openers, how doubt is introduced, and analogy structures. Then each Writing Plan section is generated sequentially as a separate Claude call, with Content Notes and the Style Fingerprint included in context alongside the Voice rules from the writing-voice skill.

Each generated section is shown separately. Hovering a section reveals a "Revise ✦" button. Clicking it opens a modal where the user gives typed or voiced feedback. A single Claude call regenerates only that section with the feedback; all other sections remain unchanged. When satisfied with all sections, the user proceeds to Repurposed Content generation.

## Acceptance criteria

- [ ] Style Fingerprint is extracted from Style Notes via a Claude call (via OpenRouter) before Draft generation begins
- [ ] Each Writing Plan section is generated as a separate Claude call, sequentially
- [ ] Voice rules from `skills/writing-voice/SKILL.md` are included in every section generation prompt
- [ ] Content Notes pinned to a section are included in that section's generation context
- [ ] Generated sections are displayed separately in Georgia serif, matching the mockup
- [ ] Hovering a section reveals a "Revise ✦" button; the button is hidden when not hovering
- [ ] Clicking "Revise ✦" opens a modal with a text area and a mic button (from Issue 04)
- [ ] Submitting revision feedback regenerates only that section; other sections are unchanged
- [ ] Loading state shown per section during generation and during revision
- [ ] Full Draft stored in `st.session_state` as a list of section texts
- [ ] "Generate Repurposed Content →" button available after all sections are generated

## Blocked by

- Issue 05 — Plan stage
- Issue 04 — Voice input (for revision modal mic button)
