import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

st.set_page_config(
    page_title="Writing Workflow",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page("pages/transcribe.py", title="Transcribe", icon="🎙"),
    st.Page("pages/develop.py",    title="Develop",    icon="💬"),
    st.Page("pages/plan.py",       title="Plan",       icon="📋"),
    st.Page("pages/draft.py",      title="Draft",      icon="✍️"),
    st.Page("pages/publish.py",    title="Publish",    icon="🚀"),
]

pg = st.navigation(pages, position="hidden")
pg.run()
