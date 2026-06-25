import streamlit as st

def t(vn_text: str, jp_text: str) -> str:
    """
    Returns the text in the currently selected language.
    Defaults to Vietnamese ('VN') if not set.
    """
    lang = st.session_state.get('lang', 'VN')
    if lang == 'JP':
        return jp_text
    return vn_text
