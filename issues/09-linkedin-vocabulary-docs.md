# 09 — Swap Substack→LinkedIn vocabulary in domain docs

## What to build

The domain glossary and PRD currently name Substack as the canonical publishing destination and describe the LinkedIn Post as a short teaser that drives traffic to Substack. After a strategy review (goal: build a LinkedIn brand to generate inbound AI PM opportunities), Substack is deferred and LinkedIn becomes the primary publishing surface. This ticket updates the reference docs so tickets 10 and 11 speak the correct glossary.

In `CONTEXT.md`:
- Add a **LinkedIn Article** term: the full argument, 600–900 words, published via LinkedIn's native article editor — a permanent, Google-indexed portfolio artifact on the profile.
- Add a **LinkedIn Feed Post** term: 150–200 words, engineered to earn comments in the first hour, links to the LinkedIn Article to trigger algorithmic amplification.
- Redefine **Repurposed Content** to produce: Tweet Thread, LinkedIn Article, LinkedIn Feed Post (Substack teaser removed).
- Redefine **Publication Record**: user publishes on LinkedIn, pastes the LinkedIn article URL back into the tool; article is indexed into the `published_articles` ChromaDB collection with the LinkedIn URL as metadata. (Substack removed; the indexing loop is retained — see ticket 11.)
- Update the **Draft** term: remove "Published on Substack"; the Draft is the source for the LinkedIn outputs.
- Mark Substack as an explicitly deferred future destination, not part of the current flow.

In `PRD.md`:
- Update any reference to Substack as the primary destination to reflect LinkedIn.
- Update the repurposed-content / output section to list the two LinkedIn outputs plus the Tweet Thread.

## Acceptance criteria

- [ ] `CONTEXT.md` defines `LinkedIn Article` (600–900w, native article editor, portfolio artifact)
- [ ] `CONTEXT.md` defines `LinkedIn Feed Post` (150–200w, first-hour engagement, links to the article)
- [ ] `CONTEXT.md` `Repurposed Content` no longer references a Substack teaser
- [ ] `CONTEXT.md` `Publication Record` references a LinkedIn URL, not Substack, and retains the `published_articles` indexing
- [ ] `CONTEXT.md` `Draft` no longer states "Published on Substack"
- [ ] Substack is noted as deferred, not current
- [ ] `PRD.md` output section reflects: Tweet Thread, LinkedIn Article, LinkedIn Feed Post
- [ ] No remaining doc text presents Substack as the active publishing destination

## Blocked by

- None — can start immediately
