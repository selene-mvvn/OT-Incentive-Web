import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
with open(r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\ot_manual.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'with tab2:' in line:
        start_idx = i + 1
    if start_idx != -1 and 'st.markdown("<hr>", unsafe_allow_html=True)' in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_lines = lines[:start_idx]
    
    new_lines.append('        c1, c2 = st.columns([1.3, 1], gap="large")\n')
    new_lines.append('        with c1:\n')
    
    for j in range(start_idx, end_idx):
        if lines[j].strip() == '':
            new_lines.append('\n')
        else:
            new_lines.append('    ' + lines[j])
            
    c2_code = '''        with c2:
            st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('LỊCH ONLINE', 'オンラインカレンダー')}</h3>", unsafe_allow_html=True)
            st.caption(t("Xem lịch để đối chiếu ngày tháng (Lịch Lễ VN)", "日付を確認するためのカレンダー（ベトナムの祝日）"))
            import streamlit.components.v1 as components
            components.iframe("https://calendar.google.com/calendar/embed?height=500&wkst=2&bgcolor=%23ffffff&ctz=Asia%2FHo_Chi_Minh&showTitle=0&showPrint=0&showTabs=1&showCalendars=0&showTz=0&src=dmkudmlldG5hbWVzZSNob2xpZGF5QGdyb3VwLnYuY2FsZW5kYXIuZ29vZ2xlLmNvbQ&color=%230B8043", height=500, scrolling=True)
'''
    new_lines.append(c2_code)
    
    new_lines.extend(lines[end_idx:])
    
    with open(r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\ot_manual.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print('Done!')
else:
    print(f'Failed to find bounds. start: {start_idx}, end: {end_idx}')
