import streamlit as st


pages = [
    st.Page("pages/top.py", title="トップ", icon=":material/home:"),
    st.Page("pages/history.py", title="時系列分析", icon=":material/analytics:"),
]

page = st.navigation(pages)

st.set_page_config(layout="wide")

page.run()
