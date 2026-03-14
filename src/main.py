import streamlit as st

pages = [
    st.Page("investment_analytics/pages/top.py", title="トップ", icon=":material/home:"),
    st.Page("investment_analytics/pages/realtime.py", title="リアルタイム分析", icon=":material/show_chart:"),
    st.Page("investment_analytics/pages/history.py", title="時系列分析", icon=":material/finance:"),
]

page = st.navigation(pages)

st.set_page_config(layout="wide")

page.run()
