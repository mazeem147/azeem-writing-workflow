# 01 — App scaffold + sidebar navigation

## What to build

Create the standalone Streamlit app entry point with 5 stage pages wired up and a persistent left sidebar. No business logic — just the shell, navigation, and design system applied consistently.

The sidebar shows: the tool name, a vertical stage list with dots and connectors (done / active / pending states), and the current piece's working title at the bottom. Clicking any stage navigates to it. The design system (dark ink ground `#0d0c14`, amber-gold accent `#c9a96e`, Georgia serif for article headings, system-ui for chrome) must be applied from the start so all subsequent slices inherit it.

## Acceptance criteria

- [ ] `app.py` entry point launches with `streamlit run app.py` from the `Azeem's Writing Workflow/` directory
- [ ] 5 stage pages exist: Transcribe, Develop, Plan, Draft, Publish — each showing its stage name and a placeholder
- [ ] Sidebar shows all 5 stages with correct done/active/pending visual states
- [ ] Clicking a stage in the sidebar navigates to that stage's page
- [ ] Current piece title is visible in the sidebar (hardcoded placeholder is fine)
- [ ] Design system (palette, typography) is applied via a shared `ui.py` CSS injection, matching the mockup
- [ ] App runs without errors against a fresh venv with dependencies installed

## Blocked by

None — can start immediately.
