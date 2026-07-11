# 10 — Repurposed Content: two LinkedIn outputs (Article + Feed Post)

## What to build

Supersedes the behaviour in issue 07. After the Draft is approved, the tool generates LinkedIn-native distribution content instead of a Substack teaser. Two Claude calls (via OpenRouter) produce:

1. **LinkedIn Article** — 600–900 words, the complete argument delivered in full (not a summary or teaser), written in Azeem's voice. Intended for LinkedIn's native article editor, where it becomes a permanent, Google-indexed portfolio artifact.
2. **LinkedIn Feed Post** — 150–200 words, written to earn comments in the first hour (direct opening hook, surfaces the core provocation, ends on a question or strong opinion that invites replies). Links to the LinkedIn Article.

The existing **Tweet Thread** output is retained unchanged. All three are shown in tabs below the Draft, individually copyable. Nothing is auto-posted — the tool generates and stops. The old single 3–5 sentence "LinkedIn Post → Substack" output is removed.

## Acceptance criteria

- [ ] LinkedIn Article generated via a Claude call (via OpenRouter) after Draft approval
- [ ] LinkedIn Article is 600–900 words and delivers the full argument, not a teaser
- [ ] LinkedIn Feed Post generated via a separate Claude call (via OpenRouter)
- [ ] LinkedIn Feed Post is 150–200 words, opens with a hook, ends on an engagement prompt
- [ ] LinkedIn Feed Post references/links to the LinkedIn Article
- [ ] Tweet Thread output retained and unchanged
- [ ] All three outputs shown in tabs below the Draft (Tweet Thread / LinkedIn Article / LinkedIn Feed Post)
- [ ] Each output is copyable (article and feed post as single blocks; tweets individually)
- [ ] Old 3–5 sentence Substack-teaser LinkedIn Post output removed from code and UI
- [ ] Loading states shown during generation of each
- [ ] "Mark as Published →" button available after outputs are generated

## Blocked by

- Issue 09 — LinkedIn vocabulary in docs
