import streamlit as st
import os
import base64
from logic.i18n import t

def get_image_as_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

def render_welcome():
    # Hide sidebar, header, and footer specifically for this page
    # And apply the wave background to the entire app container
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        
        /* The main app container gets the wave background */
        .stApp {
            background-color: #ffffff;
            background-image: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg"><path fill="%2300B0F0" fill-opacity="1" d="M0,224L80,213.3C160,203,320,181,480,181.3C640,181,800,203,960,213.3C1120,224,1280,224,1360,224L1440,224L1440,320L1360,320C1280,320,1120,320,960,320C800,320,640,320,480,320C320,320,160,320,80,320L0,320Z"></path></svg>');
            background-position: bottom;
            background-repeat: no-repeat;
            background-size: 100vw 100vh; /* Force exact full viewport fill */
            font-family: 'Times New Roman', serif;
        }
        
        .block-container { 
            padding-top: 0vh !important;
            margin-top: -5vh !important; /* Adjusted to keep language switcher visible */
            padding-left: 6vw !important; /* Shift to center */
            max-width: 100% !important;
        }
        
        .welcome-content-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            margin-top: -4vh !important;
        }
        
        .logo-container {
            text-align: center;
            margin-top: -20px;
            margin-bottom: 80px;
        }
        .logo-container img {
            max-width: 240px;
        }
        
        .title {
            color: #00B0F0;
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            line-height: 1.3;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .divider {
            width: 300px;
            height: 2px;
            background-color: #00B0F0;
            margin: 0 auto 15vh auto;
        }
        
        /* Streamlit button overrides for the welcome screen */
        div.stButton {
            display: flex;
            justify-content: center;
        }
        
        div.stButton > button {
            background-color: #ffffff !important;
            color: #00B0F0 !important;
            border: none !important;
            border-radius: 50px !important;
            width: 280px !important;
            padding: 15px 20px !important;
            font-family: 'Times New Roman', serif !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
            height: auto !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        }
        
        div.stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
        }
        
        div.stButton > button p {
            font-size: 16px !important;
            font-weight: bold !important;
            margin: 0 !important;
            line-height: 1.4 !important;
            white-space: pre-wrap !important;
        }
        
        .footer-text {
            color: #ffffff;
            text-align: center;
            font-size: 14px;
            margin-top: 6vh;
            line-height: 1.5;
            letter-spacing: 0.5px;
        }
        
        /* Subtle Geometric Decorations */
        .decor-grid-left {
            position: fixed;
            top: 15vh;
            left: 5vw;
            width: 150px;
            height: 250px;
            background-image: radial-gradient(#00B0F0 2.5px, transparent 2.5px);
            background-size: 25px 25px;
            opacity: 0.35;
            z-index: 0;
            pointer-events: none;
        }
        
        .decor-grid-right {
            position: fixed;
            top: 25vh;
            right: 5vw;
            width: 200px;
            height: 200px;
            background-image: radial-gradient(#00B0F0 2.5px, transparent 2.5px);
            background-size: 25px 25px;
            opacity: 0.35;
            z-index: 0;
            pointer-events: none;
        }
        
        @keyframes float-pulse {
            0% { transform: scale(1) translateY(0); opacity: 0.25; }
            50% { transform: scale(1.05) translateY(-15px); opacity: 0.15; }
            100% { transform: scale(1) translateY(0); opacity: 0.25; }
        }
        
        .decor-circle-1 {
            position: fixed;
            top: -10vh;
            left: -5vw;
            width: 450px;
            height: 450px;
            border: 2px solid #00B0F0;
            border-radius: 50%;
            opacity: 0.25;
            z-index: 0;
            pointer-events: none;
            animation: float-pulse 8s ease-in-out infinite;
        }
        
        .decor-circle-2 {
            position: fixed;
            bottom: 35vh;
            right: -8vw;
            width: 550px;
            height: 550px;
            border: 3px solid #00B0F0;
            border-radius: 50%;
            opacity: 0.2;
            z-index: 0;
            pointer-events: none;
            animation: float-pulse 10s ease-in-out infinite reverse;
        }
        .info-card {
            position: fixed;
            left: 3vw;
            top: 50vh;
            transform: translateY(-50%);
            width: 280px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            border-left: 4px solid #00B0F0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            font-size: 0.95rem;
            line-height: 1.6;
            color: #333;
            z-index: 1000;
        }
        </style>
        
        <!-- Render Decorations -->
        <div class="decor-grid-left"></div>
        <div class="decor-grid-right"></div>
        <div class="decor-circle-1"></div>
        <div class="decor-circle-2"></div>
    """, unsafe_allow_html=True)
    
    lang = st.session_state.get('lang', 'VN')
    info_text_vn = "Nền tảng tập trung giúp quản lý OT, incentive và công số dự án của Công ty TNHH Viet.mos. Tự động hóa việc tính toán, tổng hợp dữ liệu và xuất báo cáo, giúp tiết kiệm thời gian và nâng cao độ chính xác trong công tác quản lý nhân sự và dự án."
    info_text_jp = "Viet.mos株式会社のOT、インセンティブ、プロジェクト工数を一元管理するプラットフォーム。計算、データ集計、レポート出力を自動化し、人事・プロジェクト管理の時間を節約して精度を向上させます。"
    info_text = info_text_jp if lang == 'JP' else info_text_vn


    
    # Wrap the content in our flex container
    st.markdown('<div class="welcome-content-container">', unsafe_allow_html=True)
    
    # 2. Company Logo
    if os.path.exists("logo.png"):
        logo_b64 = get_image_as_base64("logo.png")
        if logo_b64:
            st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}" style="width: 250px; max-width: 100%;"></div>', unsafe_allow_html=True)
    elif os.path.exists("logo.jpg"):
        logo_b64 = get_image_as_base64("logo.jpg")
        if logo_b64:
            st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{logo_b64}" style="width: 250px; max-width: 100%;"></div>', unsafe_allow_html=True)
    else: 
        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

    import html
    import random
    import json
    
    if 'daily_quotes_jp' not in st.session_state:
        quotes_jp = [
            {"text": "継続は力なり", "author": "日本のことわざ"},
            {"text": "千里の道も一歩から", "author": "老子"},
            {"text": "石の上にも三年", "author": "日本のことわざ"},
            {"text": "七転び八起き", "author": "日本のことわざ"},
            {"text": "初心忘るべからず", "author": "世阿弥"},
            {"text": "努力は必ず報われる", "author": "王貞治"},
            {"text": "為せば成る、為さねば成らぬ何事も", "author": "上杉鷹山"}
        ]
        selected_jp = random.sample(quotes_jp, 3)
        st.session_state['daily_quotes_jp'] = {
            "morning": f"「{selected_jp[0]['text']}」 - {selected_jp[0]['author']}",
            "afternoon": f"「{selected_jp[1]['text']}」 - {selected_jp[1]['author']}",
            "evening": f"「{selected_jp[2]['text']}」 - {selected_jp[2]['author']}"
        }
        
    if 'daily_quotes_vn' not in st.session_state:
        quotes_vn = [
            {"text": "Mẹo nhỏ: Hãy áp dụng quy tắc 20-20-20! Mỗi 20 phút, nhìn xa 6m trong 20 giây để bảo vệ mắt nhé.", "author": "Góc sức khỏe"},
            {"text": "Đừng làm việc chăm chỉ, hãy làm việc thông minh.", "author": "Khuyết danh"},
            {"text": "Uống đủ nước chưa? Hãy đứng lên vươn vai và uống một ngụm nước đi nào!", "author": "Góc sức khỏe"},
            {"text": "Code không có bug chỉ là code chưa được test đủ thôi!", "author": "Châm ngôn Dev"},
            {"text": "OT là nghệ thuật, người làm OT chắc chắn là người rất kiên nhẫn.", "author": "Góc giải trí"},
            {"text": "Thành công không đến từ những gì bạn thỉnh thoảng làm, mà từ những gì bạn kiên trì làm mỗi ngày.", "author": "Marie Forleo"},
            {"text": "Hôm nay là một ngày tuyệt vời để bug tự nhiên biến mất.", "author": "Góc giải trí"}
        ]
        selected_vn = random.sample(quotes_vn, 3)
        st.session_state['daily_quotes_vn'] = {
            "morning": f"{selected_vn[0]['text']} ({selected_vn[0]['author']})",
            "afternoon": f"{selected_vn[1]['text']} ({selected_vn[1]['author']})",
            "evening": f"{selected_vn[2]['text']} ({selected_vn[2]['author']})"
        }
        
    daily_quotes_jp_js = json.dumps(st.session_state['daily_quotes_jp'])
    daily_quotes_vn_js = json.dumps(st.session_state['daily_quotes_vn'])
    lang = st.session_state.get('lang', 'VN')

    
    clock_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {{
        margin: 0; padding: 0; 
        font-family: 'Times New Roman', serif;
        display: flex;
        justify-content: center;
        align-items: center;
        background: transparent;
        overflow: hidden;
    }}
    .clock-widget {{
        background: rgba(0, 176, 240, 0.1);
        border: 1px solid rgba(0, 176, 240, 0.3);
        border-radius: 12px;
        padding: 6px 18px;
        color: #00B0F0;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .time-display {{
        font-weight: bold;
        font-size: 1.05rem;
        font-family: monospace;
        letter-spacing: 1px;
        background: rgba(0, 176, 240, 0.2);
        padding: 3px 8px;
        border-radius: 6px;
    }}
    .greeting-text {{
        font-style: italic;
    }}
    </style>
    </head>
    <body>
        <div class="clock-widget">
            <div class="time-display" id="time">00:00:00</div>
            <div class="greeting-text" id="greeting">Loading...</div>
        </div>
        <script>
            const quotes_jp = {daily_quotes_jp_js};
            const quotes_vn = {daily_quotes_vn_js};
            const lang = "{lang}";
            const offset = lang === "JP" ? 9 : 7;
            function updateTime() {{
                const now = new Date();
                const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
                const local = new Date(utc + (3600000 * offset));
                let h = local.getHours(); let m = local.getMinutes(); let s = local.getSeconds();
                
                let quotes = lang === "JP" ? quotes_jp : quotes_vn;
                let greeting = "";
                if (h >= 5 && h < 12) greeting = quotes["morning"];
                else if (h >= 12 && h < 18) greeting = quotes["afternoon"];
                else greeting = quotes["evening"];
                
                h = h < 10 ? "0" + h : h; m = m < 10 ? "0" + m : m; s = s < 10 ? "0" + s : s;
                document.getElementById("time").innerText = h + ":" + m + ":" + s;
                document.getElementById("greeting").innerText = greeting;
            }}
            setInterval(updateTime, 1000);
            updateTime();
        </script>
    </body>
    </html>
    """
    clock_html_escaped = html.escape(clock_html.replace('\n', ' '))
    st.markdown(f"""
        <div class="title">
            OVERTIME & INCENTIVE<br>MANAGEMENT SYSTEM
        </div>
        <div class="divider"></div>
        <div style="position: relative; height: 0; width: 100%;">
            <div style="position: absolute; top: -13vh; width: 100%; display: flex; justify-content: center;">
                <iframe srcdoc="{clock_html_escaped}" style="width: 100%; height: 50px; border: none; overflow: hidden; background: transparent;"></iframe>
            </div>
        </div>
        <div class="info-card">
            <div style="font-size: 0.95rem; line-height: 1.6; color: #555; text-align: justify; font-family: 'Times New Roman', serif; font-style: italic; padding-bottom: 30px;">
                {info_text}
            </div>
            <div style="position: absolute; bottom: -35px; right: -30px; pointer-events: none;">
                <iframe srcdoc="<!DOCTYPE html><html><head><style>body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; display: flex; justify-content: center; align-items: center; }} @keyframes float {{ 0% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-10px); }} 100% {{ transform: translateY(0px); }} }} @keyframes flicker {{ 0% {{ transform: scaleY(1); opacity: 1; }} 50% {{ transform: scaleY(1.3); opacity: 0.8; }} 100% {{ transform: scaleY(1); opacity: 1; }} }}</style></head><body><svg viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg' style='width: 90px; height: 90px; animation: float 2s ease-in-out infinite;'><defs><linearGradient id='rocketGrad' x1='0%' y1='0%' x2='100%' y2='100%'><stop offset='0%' style='stop-color:#00B0F0;stop-opacity:1' /><stop offset='100%' style='stop-color:#0075a0;stop-opacity:1' /></linearGradient><linearGradient id='fireGrad' x1='0%' y1='0%' x2='0%' y2='100%'><stop offset='0%' style='stop-color:#FF8C00;stop-opacity:1' /><stop offset='100%' style='stop-color:#FF0000;stop-opacity:1' /></linearGradient></defs><path d='M 45 70 Q 50 95 55 70 Q 50 80 45 70' fill='url(#fireGrad)' style='transform-origin: 50% 70%; animation: flicker 0.1s infinite alternate;' /><path d='M 25 50 L 25 75 L 35 65 L 35 50 Z' fill='#0075a0' /><path d='M 75 50 L 75 75 L 65 65 L 65 50 Z' fill='#0075a0' /><path d='M 35 45 C 35 15, 50 5, 50 5 C 50 5, 65 15, 65 45 L 65 70 L 35 70 Z' fill='url(#rocketGrad)' /><circle cx='50' cy='35' r='8' fill='#FFF' /><circle cx='50' cy='35' r='5' fill='#00B0F0' /></svg></body></html>" style="width: 100px; height: 100px; border: none; overflow: hidden; background: transparent; pointer-events: auto;"></iframe>
            </div>
        </div>
    """, unsafe_allow_html=True)
    # Empty space to push buttons down
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    
    # Render Buttons using standard Streamlit columns
    # Increase the outer spacers to push the buttons closer to the center
    col_spacer_left, col1, col_spacer_mid, col2, col_spacer_right = st.columns([3, 1.5, 0.2, 1.5, 3])
    
    with col1:
        if st.button(t("TÍNH LƯƠNG TĂNG CA", "残業代計算"), key="btn_ot"):
            st.session_state['current_page'] = 'ot_calc'
            st.session_state['menu_selection'] = t(":material/timer: **OVERTIME**", ":material/timer: **残業代計算**")
            st.session_state['ot_menu_expanded'] = True
            st.rerun()
            
    with col2:
        if st.button(t("TÍNH LƯƠNG INCENTIVE", "インセンティブ計算"), key="btn_inc"):
            st.session_state['current_page'] = 'incentive_calc'
            st.session_state['menu_selection'] = t(":material/payments: **INCENTIVE**", ":material/payments: **インセンティブ**")
            st.session_state['ot_menu_expanded'] = False
            st.rerun()

    # 5. Instructional Text
    st.markdown(f'''
        <div style="text-align: center; color: #ffffff; margin-top: 30px; font-style: italic; font-size: 1.1rem; letter-spacing: 0.5px;">
            {t("Vui lòng chọn một trong các chức năng trên để tiếp tục.", "上記の機能からいずれかを選択して続行してください。")}
        </div>
    ''', unsafe_allow_html=True)

    # Render Footer text
    # 6. Version Note
    st.markdown("""
        <div class="footer-text">
            © 2024 VIET.MOS COMPANY LIMITED<br>
            <i>Internal Management Tool v1.0</i>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
