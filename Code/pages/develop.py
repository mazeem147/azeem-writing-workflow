import streamlit as st
from ui import inject_css, render_sidebar, render_page_header

inject_css()
render_sidebar("develop")
render_page_header("develop", "💬 Develop", "Expand your Capture into a full position via AI-driven conversation.")
st.info("Stage 2 placeholder — implementation coming in issue 03.")
