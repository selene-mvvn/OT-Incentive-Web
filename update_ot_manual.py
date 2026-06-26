import sys

with open('components/ot_manual.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = """    with tab_calc:
        st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('1. KỲ TÍNH LƯƠNG', '1. 給与計算期間')}</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            import datetime
            from_date = st.date_input(t("TỪ NGÀY", "開始日"), key="ot_from_date", value=datetime.date.today().replace(day=21) - datetime.timedelta(days=30))
        with c2:
            to_date = st.date_input(t("ĐẾN NGÀY", "終了日"), key="ot_to_date", value=datetime.date.today().replace(day=20))"""

replacement = """    with tab_calc:
        import datetime
        try:
            fd_str = st.session_state['ot_base_data'].get('from_date', '')
            if fd_str:
                from_date = datetime.datetime.strptime(fd_str, "%Y-%m-%d").date()
            else:
                from_date = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
        except:
            from_date = datetime.date.today().replace(day=21) - datetime.timedelta(days=30)
            
        try:
            td_str = st.session_state['ot_base_data'].get('to_date', '')
            if td_str:
                to_date = datetime.datetime.strptime(td_str, "%Y-%m-%d").date()
            else:
                to_date = datetime.date.today().replace(day=20)
        except:
            to_date = datetime.date.today().replace(day=20)"""

new_text = text.replace(pattern, replacement)
if text == new_text:
    print('Failed to replace ot_manual')
else:
    with open('components/ot_manual.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('Success ot_manual')
