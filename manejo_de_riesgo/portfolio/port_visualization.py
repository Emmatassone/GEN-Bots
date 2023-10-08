import streamlit as st
import pandas as pd
from datetime import date
from main import portfolio_w, report, portfolio


st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title('Portfolio Dashboard')
st.write(':')
st.line_chart(portfolio['Cumulative Return'])
st.dataframe(
    report.transpose())
st.dataframe(
    portfolio_w.transpose(),
    use_container_width=True,
)
# streamlit run myfile.py

#%%
