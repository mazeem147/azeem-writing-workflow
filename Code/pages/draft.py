import streamlit as st
from ui import inject_css, render_sidebar, render_page_header

inject_css()
render_sidebar("draft")
render_page_header("draft", "✍️ Draft", "Article generated section by section in your Voice.")
st.info("Stage 4 placeholder — implementation coming in issue 06.")
