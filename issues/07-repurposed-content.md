# 07 — Repurposed Content: Tweet Thread + LinkedIn Post

## What to build

After the Draft is approved, two Claude calls (via OpenRouter) generate platform-native content for distribution. The Tweet Thread is 8-12 tweets written for Twitter's attention structure — strong opening provocation, each tweet standalone-readable, closes with a hook to Substack. It is not a summary of the article; it is a rewrite for a different medium. The LinkedIn Post is 3-5 sentences surfacing the core provocation and driving traffic to Substack, in a direct non-corporate tone.

Both are shown in tabs below the Draft article. The user reviews and approves both before proceeding to the Publish stage. Nothing is posted automatically — the tool generates and stops.

## Acceptance criteria

- [ ] Tweet Thread generated via a single Claude call (via OpenRouter) after Draft approval
- [ ] Tweet Thread contains 8-12 tweets, each under 280 characters
- [ ] First tweet opens with a provocation, not the article's introduction
- [ ] Final tweet contains a hook driving to Substack
- [ ] LinkedIn Post generated via a separate Claude call (via OpenRouter)
- [ ] LinkedIn Post is 3-5 sentences, direct tone, surfaces the core provocation
- [ ] Both shown in tabs (Tweet Thread / LinkedIn Post) below the Draft article
- [ ] Tweet Thread tweets are individually copyable
- [ ] LinkedIn Post is copyable as a single block
- [ ] "Mark as Published →" button available after both are generated
- [ ] Loading states shown during generation of each

## Blocked by

- Issue 06 — Draft stage
