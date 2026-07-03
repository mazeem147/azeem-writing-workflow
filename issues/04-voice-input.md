# 04 — Voice input: mic button across all stages

## What to build

A reusable mic component that can be dropped next to any text input in the app. Clicking it records audio from the user's microphone, sends the audio to Whisper (via OpenAI API directly), and inserts the cleaned transcript into the associated text field. The user reviews the transcribed text before submitting. The component must work in the Develop stage conversation input and the Draft revision modal at minimum.

## Acceptance criteria

- [ ] Mic button renders next to the conversation input on the Develop stage
- [ ] Mic button renders in the section revision modal on the Draft stage
- [ ] Clicking the mic button starts recording; the button changes state (pulsing animation) to indicate recording is active
- [ ] Clicking the button again stops recording
- [ ] Recorded audio is sent to Whisper via OpenAI API and transcribed
- [ ] Transcription is inserted into the associated text field for review before submission
- [ ] User can edit the transcribed text before sending
- [ ] Handles Urdu/English mixed speech (Whisper multilingual)
- [ ] Mic component is implemented as a reusable function/component, not duplicated per screen

## Blocked by

- Issue 03 — Develop stage
