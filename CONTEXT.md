---
name: writing-workflow
description: Domain glossary for Azeem's speech-to-article writing workflow
---

# Glossary

**Trigger**
An external stimulus — a YouTube video, a tweet, a workplace experience — that involuntarily activates Azeem's opinion-formation. The workflow always begins here. Never begins from a blank topic choice.

**Juice**
The emotional and intellectual energy that accompanies a Trigger. Fades within hours. If not captured, the resulting article feels flat — like reheating food. The opinion may survive but the aliveness doesn't.

**Capture**
A low-friction, phone-first action taken immediately after a Trigger while Juice is still present. Records the stimulus (link, quote, description) and the raw gut reaction. Must take under 60 seconds. Not writing — just preserving the live signal.

**Development Session**
A separate, intentional session (typically on laptop) where a Capture is expanded into a full position via AI-driven conversation. Happens after Juice has faded — works from the preserved signal, not memory.

**Seeder Questions**
AI-generated questions asked during a Development Session, derived from the Capture itself. Not templated. Designed to probe the opinion, surface contradictions, and make Azeem talk — not think abstractly.

**Brain Dump**
Azeem's spoken or typed response to Seeder Questions. The raw material. Unpolished. May include Urdu phrases, analogies, digressions. This is the voice source.

**Writing Plan**
A structured outline extracted from the Brain Dump. Key claims, arguments, personal stories, analogies, contrarian positions. Reviewed and approved by Azeem before generation.

**Draft**
An article generated from the Writing Plan, grounded in Azeem's RAG notes (past thinking), and written in Azeem's voice. Not generic AI output. Published on Substack.

**Voice**
Azeem's rhetorical signature: journey structure (not report), analytical and personal in the same sentence, Urdu/Pakistani cadence, thinks out loud, ends open. Captured in the writing-voice skill.

**Style Fingerprint**
A dynamically extracted description of Azeem's rhetorical patterns, derived from 5-10 representative retrieved notes at generation time. Captures sentence rhythms, paragraph openings, how doubt is introduced, favourite analogy structures. Distinct from Voice rules — this is evidence, not instruction.

**Capture Session**
The phone-first, sub-60-second act of recording a voice memo (native iPhone app) and emailing it to oneself. Contains: the trigger stimulus (link/quote/experience description) + raw gut reaction. No structure required.

**Development Session**
Desktop-only. User uploads the voice memo, transcript is cleaned by Claude, Seeder Questions begin. User talks back until satisfied, then hits "build the plan." Retrieves related notes from ChromaDB at plan-build time.

**Content Notes**
Notes retrieved from ChromaDB for their topical relevance to the Writing Plan. Used to enrich the Draft with past thinking.

**Style Notes**
Notes retrieved from ChromaDB as stylistic exemplars — selected for how well they represent Azeem's prose rhythms, not their topic. Used to generate the Style Fingerprint.

**Repurposed Content**
Outputs generated from the Draft before publishing: a Tweet Thread and a LinkedIn Post. Generated in the same session as the Draft, reviewed and approved before anything goes live. Never auto-posted — tool stops at generation.

**Tweet Thread**
8-12 tweets written natively for Twitter's attention structure: strong opener, each tweet standalone-readable, closes with a hook to Substack. Not a compressed version of the article — a rewrite for a different medium.

**LinkedIn Post**
Short post (3-5 sentences) written to surface the core provocation of the article and drive traffic to Substack. Tone: direct, not corporate.

**Publication Record**
After the user publishes manually on Substack and pastes the URL back into the tool, the article is indexed into the `published_articles` ChromaDB collection and the URL is stored. Future Development Sessions can surface published articles as Content Notes.

**Inference Provider**
All LLM calls (transcription cleaning, Seeder Questions, Writing Plan extraction, Style Fingerprint, Draft generation, Repurposed Content) are routed through OpenRouter, not directly to Anthropic or OpenAI APIs. OpenRouter provides model flexibility and a single API key across providers.

