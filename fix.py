import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
file_path = r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\action_history_ui.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = lines[:204]

correct_ending = '''        with pc1:
            if st.button("⬅️ " + t("Trang trước", "前へ"), disabled=(current_page == 1), use_container_width=True):
                st.session_state['history_page'] -= 1
                st.rerun()
        with pc2:
            st.markdown(f"<div style='text-align: center; margin-top: 10px; font-size: 16px;'><b>{t('Trang', 'ページ')} {current_page} / {total_pages}</b></div>", unsafe_allow_html=True)
        with pc3:
            if st.button(t("Trang sau", "次へ") + " ➡️", disabled=(current_page == total_pages), use_container_width=True):
                st.session_state['history_page'] += 1
                st.rerun()

    from components.ui_utils import make_history_cards_white
    make_history_cards_white()
'''

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
    f.write(correct_ending)

print('File fixed successfully')
