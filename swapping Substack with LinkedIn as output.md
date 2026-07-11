# Handoff: Swap Substack with LinkedIn as Primary Output

## Context

Azeem's writing workflow tool was designed with Substack as the canonical publishing destination and a short LinkedIn post as a traffic driver to Substack. After reviewing the actual goal — building a LinkedIn brand to generate inbound AI PM job opportunities — this architecture is wrong. Recruiters and hiring managers don't browse Substack. They live on LinkedIn. Substack is being removed entirely from the near-term publishing flow.

> **This work is now ticketed.** The source of truth is `issues/09-linkedin-vocabulary-docs.md`, `issues/10-linkedin-repurposed-content.md`, and `issues/11-linkedin-publish-stage.md`. This handoff is the background rationale; where it disagrees with the tickets, the tickets win.

## Decision Summary

- **Drop Substack** as a publishing destination for now (revisit in 6+ months)
- **Replace** the current "LinkedIn Post (3-5 sentences to drive traffic to Substack)" output with two LinkedIn-native outputs
- **Keep** the Publication Record flow but **repoint it to LinkedIn** — user pastes the published LinkedIn article URL back into the tool, and the article is still indexed into the `published_articles` ChromaDB collection so future Development Sessions can surface past pieces as Content Notes. (This supersedes the earlier plan to remove the publish stage; the Second Brain feedback loop is worth keeping.)
- **Keep** the Tweet Thread output unchanged

## New Output Spec

Replace the single LinkedIn Post output with these two outputs, generated in the same session as the Draft:

### Output 1: LinkedIn Native Article
- **Length:** 600–900 words
- **Format:** Full argument delivered completely — not a teaser
- **Purpose:** Published via LinkedIn's article editor (not the feed). Indexed by Google. Appears permanently on Azeem's LinkedIn profile as a portfolio artifact.
- **Tone:** Matches Azeem's voice (see writing-voice skill and CONTEXT.md Voice definition)

### Output 2: LinkedIn Feed Post
- **Length:** 150–200 words
- **Format:** Written to generate comments and engagement in the first 60 minutes after publishing
- **Purpose:** Algorithmic amplification. Links to the LinkedIn native article.
- **Tone:** Direct opening hook, surfaces the core provocation, ends with a question or strong opinion to invite replies

## Files to Update

### 1. `CONTEXT.md`
- In the **Repurposed Content** definition: replace "LinkedIn Post (3-5 sentences to drive traffic to Substack)" with the two-output structure above
- In the **LinkedIn Post** definition: replace with the new Feed Post definition
- Add a new **LinkedIn Article** definition
- Redefine the **Publication Record** definition: LinkedIn article URL paste-back (not Substack), indexing into `published_articles` retained
- Update the **Draft** definition: remove "Published on Substack"
- Keep the **Tweet Thread** definition unchanged

### 2. `PRD.md`
- Find any references to Substack as the primary publishing destination and update them to LinkedIn
- Update the repurposed content section to reflect the two LinkedIn outputs
- Keep the publication record / ChromaDB `published_articles` indexing feature — repoint its URL input to LinkedIn

### 3. Any UI or page files that reference the Substack URL input or Publication Record flow
- Search for "substack" across `pages/` and `components/`
- Swap any UI that asks the user to paste a Substack URL for a LinkedIn article URL (do not remove the indexing step)

## What NOT to Change

- The **Draft** generation step — the full article draft is still generated and is the source for both LinkedIn outputs
- The **ChromaDB content notes** and **style notes** retrieval — unchanged
- The **Writing Plan**, **Seeder Questions**, **Brain Dump**, **Capture** flows — all unchanged
- The **Tweet Thread** output — leave in place unless Azeem decides to remove it separately

## Verification

After changes, confirm:
1. CONTEXT.md glossary defines Publication Record via a LinkedIn URL, and no longer names Substack as a destination
2. PRD.md output section lists: Draft, LinkedIn Article, LinkedIn Feed Post, Tweet Thread
3. No UI element prompts the user to paste a Substack URL — the publish stage asks for a LinkedIn article URL and still indexes into `published_articles`
4. The two LinkedIn outputs are generated together in the same session step as the Draft
