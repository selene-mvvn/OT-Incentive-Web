import re

with open('components/incentive_ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove tab_charts from the tabs definition
# Instead of `tab_calc, tab_charts = st.tabs(...)`
# We'll just have no tabs, or keep just a single container, or keep it inside the main flow.
# But wait, we can just replace `tab_calc, tab_charts = st.tabs(...)` with `tab_calc = st.container()`
text = text.replace(
    'tab_calc, tab_charts = st.tabs([t("1. TÍNH INCENTIVE", "1. インセンティブ計算"), t("2. BẢNG XẾP HẠNG & BIỂU ĐỒ", "2. ランキング＆チャート")])',
    'tab_calc = st.container()'
)

# 2. Find `# ==========================\n    # TAB 2: RANKING & CHARTS\n    # ==========================\n    with tab_charts:`
# and replace it with `    if 'last_incentive_calc' in st.session_state:`
# But wait, there is already `with tab_calc:` around line 289 where "BẢNG DỮ LIỆU CHỜ XUẤT" is.
# So we can just replace `with tab_charts:` with `if 'last_incentive_calc' in st.session_state:`
text = text.replace(
    '    with tab_charts:',
    "    if 'last_incentive_calc' in st.session_state:"
)

# 3. But wait, `with tab_calc:` before `info_text = t(...)`
# We can leave `with tab_calc:` as `with tab_calc:` since `tab_calc` is now a container.

with open('components/incentive_ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Success")
