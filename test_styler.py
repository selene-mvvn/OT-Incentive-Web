import streamlit as st
import pandas as pd

st.title("Data Editor Styler Test")
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "150%": [10, 20, 30]})

def color_cols(s):
    if "150" in str(s.name):
        return ['background-color: #e8f5e9; color: #2e7d32'] * len(s)
    return [''] * len(s)

styled_df = df.style.apply(color_cols, axis=0)

edited = st.data_editor(styled_df, key="test_editor")
st.write(edited)
