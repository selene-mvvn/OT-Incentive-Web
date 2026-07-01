import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
with open(r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\ot_manual.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_c2 = '''        with c2:
            st.markdown(f"<h3 style='font-size: 20px; font-weight: 600;'>{t('LỊCH ONLINE', 'オンラインカレンダー')}</h3>", unsafe_allow_html=True)
            st.caption(t("Xem lịch để đối chiếu ngày tháng (Lịch Lễ VN)", "日付を確認するためのカレンダー（ベトナムの祝日）"))
            import streamlit.components.v1 as components
            components.iframe("https://calendar.google.com/calendar/embed?height=500&wkst=2&bgcolor=%23ffffff&ctz=Asia%2FHo_Chi_Minh&showTitle=0&showPrint=0&showTabs=1&showCalendars=0&showTz=0&src=dmkudmlldG5hbWVzZSNob2xpZGF5QGdyb3VwLnYuY2FsZW5kYXIuZ29vZ2xlLmNvbQ&color=%230B8043", height=550, scrolling=True)'''

new_c2 = '''        with c2:
            import json
            import streamlit.components.v1 as components
            holidays_list = []
            if current_df is not None and not current_df.empty:
                for _, row in current_df.iterrows():
                    dt = row.get("Ngày nghỉ")
                    reason = row.get("Lý do", "")
                    if pd.notnull(dt):
                        date_str = str(dt)[:10]
                        holidays_list.append({"date": date_str, "reason": reason})
            
            holidays_json = json.dumps(holidays_list)
            
            html_code = f"""
            <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; color: #334155; }}
            .cal-header {{ display: flex; justify-content: space-between; align-items: center; padding: 5px 0 15px 0; }}
            .cal-header button {{ background: none; border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px 12px; cursor: pointer; color: #475569; font-weight: bold; background: white; }}
            .cal-header button:hover {{ background: #f1f5f9; }}
            .cal-header h3 {{ margin: 0; font-size: 18px; font-weight: 600; color: #0f172a; }}
            .cal-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 1px; background: #e2e8f0; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            .cal-grid > div {{ background: #fff; min-height: 85px; padding: 4px; box-sizing: border-box; }}
            .day-name {{ min-height: 30px !important; text-align: center; font-weight: bold; background: #f8fafc !important; font-size: 13px; padding-top: 8px !important; color: #64748b; }}
            .day-number {{ font-weight: 500; font-size: 13px; margin-bottom: 4px; text-align: right; color: #475569; }}
            .holiday-event {{ background: #10b981; color: white; font-size: 11px; padding: 3px 5px; border-radius: 4px; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; }}
            .holiday-event:hover {{ white-space: normal; overflow: visible; word-break: break-word; }}
            .other-month {{ background: #f8fafc !important; color: #cbd5e1 !important; }}
            .other-month .day-number {{ color: #cbd5e1 !important; }}
            .today {{ background: #eff6ff !important; }}
            .today .day-number {{ color: #2563eb; font-weight: bold; }}
            </style>

            <div class="cal-header">
                <button onclick="changeMonth(-1)">&lt;</button>
                <h3 id="monthYear"></h3>
                <button onclick="changeMonth(1)">&gt;</button>
            </div>
            <div class="cal-grid" id="calGrid"></div>

            <script>
            const holidays = {holidays_json};
            let currentDate = new Date();

            function renderCalendar() {{
                const year = currentDate.getFullYear();
                const month = currentDate.getMonth();
                
                document.getElementById("monthYear").innerText = "Tháng " + (month + 1) + ", " + year;
                
                const firstDay = new Date(year, month, 1).getDay();
                const startDay = firstDay === 0 ? 6 : firstDay - 1; 
                
                const daysInMonth = new Date(year, month + 1, 0).getDate();
                const daysInPrevMonth = new Date(year, month, 0).getDate();
                
                let html = `
                    <div class="day-name">T2</div>
                    <div class="day-name">T3</div>
                    <div class="day-name">T4</div>
                    <div class="day-name">T5</div>
                    <div class="day-name">T6</div>
                    <div class="day-name">T7</div>
                    <div class="day-name">CN</div>
                `;
                
                for (let i = 0; i < startDay; i++) {{
                    const d = daysInPrevMonth - startDay + i + 1;
                    html += `<div class="other-month"><div class="day-number">${{d}}</div></div>`;
                }}
                
                const today = new Date();
                for (let i = 1; i <= daysInMonth; i++) {{
                    const isToday = today.getDate() === i && today.getMonth() === month && today.getFullYear() === year;
                    const cls = isToday ? "today" : "";
                    
                    const m = String(month + 1).padStart(2, '0');
                    const d = String(i).padStart(2, '0');
                    const dateStr = `${{year}}-${{m}}-${{d}}`;
                    
                    let eventsHtml = "";
                    const dayHolidays = holidays.filter(h => h.date === dateStr);
                    dayHolidays.forEach(h => {{
                        eventsHtml += `<div class="holiday-event" title="${{h.reason}}">${{h.reason}}</div>`;
                    }});
                    
                    html += `<div class="${{cls}}"><div class="day-number">${{i}}</div>${{eventsHtml}}</div>`;
                }}
                
                const totalCells = startDay + daysInMonth;
                const nextDays = Math.ceil(totalCells / 7) * 7 - totalCells;
                for (let i = 1; i <= nextDays; i++) {{
                    html += `<div class="other-month"><div class="day-number">${{i}}</div></div>`;
                }}
                
                document.getElementById("calGrid").innerHTML = html;
            }}

            function changeMonth(delta) {{
                currentDate.setMonth(currentDate.getMonth() + delta);
                renderCalendar();
            }}

            renderCalendar();
            </script>
            """
            components.html(html_code, height=650)'''

if old_c2 in content:
    content = content.replace(old_c2, new_c2)
    with open(r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\ot_manual.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done replacement!')
else:
    print('Could not find old_c2 string!')
