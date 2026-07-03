# 02 — Transcribe stage: upload → Whisper → Claude clean → inline correction

## What to build

The Transcribe stage is a complete end-to-end path from audio file to a correctable transcript. The user uploads a voice memo (`.m4a`, `.mp3`, `.wav`), Whisper transcribes it via the OpenAI API directly (not OpenRouter — OpenRouter does not proxy audio endpoints), then a Claude pass via OpenRouter cleans the transcript: fixing Urdu transliteration errors and marking uncertain words with `[?]`. The cleaned transcript is displayed with `[?]` words highlighted in amber. The user clicks any highlighted word to correct it inline. When satisfied, they proceed to the Develop stage.

## Acceptance criteria

- [ ] File uploader accepts `.m4a`, `.mp3`, `.wav` audio files
- [ ] Whisper transcription runs on upload and displays a loading state while processing
- [ ] Claude cleaning pass (via OpenRouter) runs after transcription and normalises Urdu/English mixed text
- [ ] Uncertain words are marked `[?]` by Claude and rendered as clickable amber highlights in the transcript
- [ ] Clicking a highlighted word opens an inline edit field; saving updates the transcript in place
- [ ] Transcript is stored in `st.session_state` for use by the Develop stage
- [ ] "Begin Development Session →" button navigates to Develop stage and is disabled until transcription is complete
- [ ] `OPENAI_API_KEY` used for Whisper; `OPENROUTER_API_KEY` used for Claude cleaning pass
- [ ] Both keys read from `.env` file

## Blocked by

- Issue 01 — App scaffold + sidebar navigation
