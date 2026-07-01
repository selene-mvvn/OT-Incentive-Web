import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
with open(r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\ot_manual.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_str_1 = '''            const holidays = {holidays_json};
            let currentDate = new Date();

            function renderCalendar() {{
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth();

                document.getElementById("monthYear").innerText = "Tháng " + (month + 1) + ", " + year;'''

new_str_1 = '''            const holidays = {holidays_json};
            const currentLang = "{t('vn', 'jp')}";
            let currentDate = new Date();

            function renderCalendar() {{
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth();

                if (currentLang === 'vn') {{
                    document.getElementById("monthYear").innerText = "Tháng " + (month + 1) + ", " + year;
                }} else {{
                    document.getElementById("monthYear").innerText = year + "年 " + (month + 1) + "月";
                }}'''

old_str_2 = '''                    <div class="day-name">T2</div>
                    <div class="day-name">T3</div>
                    <div class="day-name">T4</div>
                    <div class="day-name">T5</div>
                    <div class="day-name">T6</div>
                    <div class="day-name">T7</div>
                    <div class="day-name">CN</div>'''

new_str_2 = '''                    <div class="day-name">{t('T2', '月')}</div>
                    <div class="day-name">{t('T3', '火')}</div>
                    <div class="day-name">{t('T4', '水')}</div>
                    <div class="day-name">{t('T5', '木')}</div>
                    <div class="day-name">{t('T6', '金')}</div>
                    <div class="day-name">{t('T7', '土')}</div>
                    <div class="day-name">{t('CN', '日')}</div>'''

if old_str_1 in content and old_str_2 in content:
    content = content.replace(old_str_1, new_str_1)
    content = content.replace(old_str_2, new_str_2)
    with open(r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\ot_manual.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done replacement!')
else:
    print('Strings not found!')
