import streamlit as st
from ui import inject_css, render_sidebar, render_page_header

inject_css()
render_sidebar("plan")
render_page_header("plan", "📋 Plan", "Review and approve your Writing Plan before generation.")
st.info("Stage 3 placeholder — implementation coming in issue 05.")
