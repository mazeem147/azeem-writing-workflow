import streamlit as st
from ui import inject_css, render_sidebar, render_page_header

inject_css()
render_sidebar("publish")
render_page_header("publish", "🚀 Publish", "Paste your Substack URL to index the article into your Second Brain.")
st.info("Stage 5 placeholder — implementation coming in issue 08.")
