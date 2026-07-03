---
title: Phone capture via native voice memo + email
status: accepted
date: 2026-07-03
---

## Context

Triggers happen away from the laptop. The Juice (creative energy) fades within hours. A capture mechanism must work in under 60 seconds from a phone, with zero cost and zero new apps.

## Decision

Capture = iPhone Voice Memos app → share via email to self. On laptop, user manually uploads the file to the workflow app, which transcribes via Whisper then cleans the transcript with a Claude pass.

## Alternatives rejected

- WhatsApp bot: costs money (Twilio/Meta API)
- iMessage bot: same cost issue
- Custom iOS app: too much to build, too much friction to maintain
- Email polling / auto-ingest: requires a running server or cron job — infra overhead not justified at this stage

## Consequences

- No automatic ingest — user must manually upload on laptop. Acceptable because upload happens during an intentional Development Session, not in the moment of capture.
- Urdu/English mixed audio handled by Whisper + Claude cleaning pass. Uncertain words marked `[?]` for manual correction.
