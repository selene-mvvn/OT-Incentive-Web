import streamlit as st
import pandas as pd
df = pd.DataFrame({'val': [1000000, 20000]})
st.data_editor(df, column_config={'val': st.column_config.NumberColumn(format='%d')})
st.data_editor(df, column_config={'val': st.column_config.NumberColumn(format='%,d')})
st.data_editor(df, column_config={'val': st.column_config.NumberColumn(format='%,.0f')})
