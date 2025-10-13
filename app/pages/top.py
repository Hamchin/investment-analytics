import streamlit as st


st.title("投資分析ツール")

st.markdown("株式や暗号資産などの価格データをもとに、様々な分析を行うことができます。")

st.subheader("メニュー")

st.page_link("pages/realtime.py", label="リアルタイム分析", icon=":material/show_chart:")
st.page_link("pages/history.py", label="時系列分析", icon=":material/finance:")
