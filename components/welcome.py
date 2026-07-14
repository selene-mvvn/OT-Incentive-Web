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
        .stApp, [data-testid="stAppViewContainer"], section.main {
            background-color: #ffffff;
            background-image: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg"><path fill="%2300B0F0" fill-opacity="1" d="M0,224L80,213.3C160,203,320,181,480,181.3C640,181,800,203,960,213.3C1120,224,1280,224,1360,224L1440,224L1440,320L1360,320C1280,320,1120,320,960,320C800,320,640,320,480,320C320,320,160,320,80,320L0,320Z"></path></svg>');
            background-position: bottom;
            background-repeat: no-repeat;
            background-size: 100vw 100vh; /* Force exact full viewport fill */
            background-attachment: fixed;
            font-family: 'Times New Roman', serif;
            overflow: hidden !important;
        }
        
        .block-container { 
            padding-top: 0vh !important;
            padding-bottom: 0vh !important;
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
            margin-bottom: 50px;
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
        
        [data-testid="stApp"] [data-testid="stMain"] div.stButton button,
        [data-testid="stApp"] [data-testid="stMain"] div[data-testid="stButton"] button,
        [data-testid="stMain"] div.stButton button,
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
        
        [data-testid="stApp"] [data-testid="stMain"] div.stButton button:hover,
        [data-testid="stApp"] [data-testid="stMain"] div[data-testid="stButton"] button:hover,
        [data-testid="stMain"] div.stButton button:hover,
        div.stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
            background-color: #ffffff !important;
            color: #0075a0 !important;
            border: none !important;
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
            margin-top: 4vh;
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
    from logic.holiday_utils import get_countdown_info
    
    quotes_jp = [
        "「継続は力なり」 - 日本のことわざ",
        "「千里の道も一歩から」 - 老子",
        "「石の上にも三年」 - 日本のことわざ",
        "「七転び八起き」 - 日本のことわざ",
        "「初心忘るべからず」 - 世阿弥",
        "「努力は必ず報われる」 - 王貞治",
        "「為せば成る、為さねば成らぬ何事も」 - 上杉鷹山",
        "「動機善なりや、私心なかりしか」 - 稲盛和夫",
        "「企業は人なり」 - 松下幸之助",
        "「成功にとらわれるな、成長にとらわれろ」 - 本田宗一郎",
        "「ちりも積もれば山となる」 - 日本のことわざ",
        "「一期一会」 - 千利休",
        "「温故知新」 - 孔子",
        "「急がば回れ」 - 日本のことわざ",
        "「雨降って地固まる」 - 日本のことわざ",
        "「改善に終わりなし」 - トヨタ生産方式",
        "「目先の利益より信頼を積め」 - 松下幸之助",
        "「健康管理も重要な仕事の一部です。水分補給と適度な休息を！」 - 健康アドバイス",
        "「20分おきに遠くを見て、目の疲れを和らげましょう。」 - 健康アドバイス",
        "「素晴らしい仕事をする唯一の方法は、自分の仕事を愛することだ。」 - スティーブ・ジョブズ",
        "「失敗を恐れるな、挑戦しないことを恐れよ。」 - 稲盛和夫",
        "「小さなことを重ねることが、とんでもないところに行くただひとつの道。」 - イチロー",
        "「明日やろうは馬鹿野郎。今できることに全力を尽くそう。」 - 日本のことわざ",
        "「品質とは、誰も見ていないときに正しく行うことである。」 - ヘンリー・フォード",
        "「仕事を楽しむ者は、どんな困難も乗り越えられる。」 - 孔子",
        "「チームの和が、最大の目標を達成させる。」 - 日本のことわざ",
        "「準備よし、結果よし。入念な準備が成功の8割を決定する。」 - ビジネス訓",
        "「整理・整頓・清掃・清潔・躾（5S）は環境づくりの基本。」 - 5S精神",
        "「今日も一日、笑顔と前向きな心で仕事に取り組みましょう！」 - VIET.MOS",
        "「ひとつの成功は、毎日の粘り強い努力の結晶である。」 - 稲盛和夫",
        "「感謝の心が、最大のモチベーションを生む。」 - 経営哲学",
        "「逆境こそが、人を鍛え大きくする最良の道場である。」 - 稲盛和夫",
        "「姿勢を正しく、深呼吸をしてリフレッシュしましょう！」 - 健康アドバイス",
        "「時間こそが最も貴重な資源である。」 - ピーター・ドラッカー",
        "「お互いを尊重し助け合うことで、チームの力は無限大になる。」 - チームワーク"
    ]
    quotes_vn = [
        "Thành công không đến từ những gì bạn thỉnh thoảng làm, mà từ những gì bạn kiên trì làm mỗi ngày. (Marie Forleo)",
        "Đừng làm việc chăm chỉ hơn, hãy làm việc thông minh và có chiến lược hơn. (Khuyết danh)",
        "Cách tốt nhất để dự đoán tương lai là tự mình tạo ra nó. (Peter Drucker)",
        "Chất lượng là làm đúng mọi việc ngay cả khi không có ai đang nhìn. (Henry Ford)",
        "Mẹo sức khỏe: Áp dụng quy tắc 20-20-20! Mỗi 20 phút làm việc, hãy nhìn xa 6m trong 20 giây để thư giãn mắt nhé. (Góc sức khỏe)",
        "Uống đủ nước chưa bạn ơi? Hãy đứng lên vươn vai và uống một cốc nước ấm để nạp lại năng lượng nào! (Góc sức khỏe)",
        "Tư thế ngồi chuẩn: Giữ lưng thẳng, vai thả lỏng và màn hình ngang tầm mắt để bảo vệ cột sống nhé. (Góc sức khỏe)",
        "Một ngày làm việc hiệu quả bắt đầu từ việc sắp xếp thứ tự ưu tiên rõ ràng cho từng nhiệm vụ. (Brian Tracy)",
        "Hợp tác là triết lý dẫn lối cho những thành công vượt trội của một tập thể. (Andrew Carnegie)",
        "Những điều vĩ đại trong kinh doanh không bao giờ được làm bởi một người, chúng được làm bởi một đội ngũ. (Steve Jobs)",
        "Hoàn thành tốt hơn là hoàn hảo. Hãy tiếp tục tiến lên từng bước mỗi ngày! (Sheryl Sandberg)",
        "Sự tập trung là chìa khóa mở ra cánh cửa của năng suất và sáng tạo vượt trội. (Khuyết danh)",
        "Không có áp lực thì không có kim cương. Mọi thử thách đều là cơ hội rèn giũa bản lĩnh. (Thomas Carlyle)",
        "Hãy yêu công việc bạn làm, bạn sẽ không phải làm việc ngày nào trong đời. (Khổng Tử)",
        "Người kiên nhẫn là người có thể xoay chuyển cả thế giới. (Benjamin Franklin)",
        "Thái độ tích cực là nguồn năng lượng mạnh mẽ nhất để giải quyết mọi bài toán khó. (Khuyết danh)",
        "Hãy lắng nghe khách hàng bằng cả trái tim và giải quyết bằng cả trí tuệ. (Konosuke Matsushita)",
        "Nỗ lực thầm lặng hôm nay chính là nền tảng cho sự bứt phá ngoạn mục ngày mai. (Kazuo Inamori)",
        "Đừng sợ thất bại, hãy sợ việc giậm chân tại chỗ và không dám thử thách mới. (Khuyết danh)",
        "Thời gian là tài sản quý giá nhất, hãy đầu tư nó vào những giá trị bền vững. (Khuyết danh)",
        "Code sạch là code được viết bởi một người quan tâm đến từng chi tiết nhỏ. (Robert C. Martin)",
        "Kiểm tra kỹ lưỡng trước khi bàn giao là dấu ấn của một người chuyên nghiệp. (Khuyết danh)",
        "Một nụ cười và tinh thần sẵn sàng giúp đỡ đồng nghiệp sẽ làm bừng sáng cả văn phòng. (Góc văn phòng)",
        "Hãy nghỉ giải lao 5 phút mỗi hai giờ để não bộ tái tạo sự sáng tạo vượt trội. (Góc năng suất)",
        "Đừng chỉ giải quyết vấn đề, hãy tìm tận gốc rễ để nó không bao giờ lặp lại. (Triết lý Kaizen)",
        "Cải tiến liên tục 1% mỗi ngày sẽ mang lại sức mạnh tăng trưởng gấp 37 lần sau một năm! (James Clear)",
        "Uy tín của công ty được xây dựng từ cam kết chất lượng trong từng dự án nhỏ nhất. (Khuyết danh)",
        "Hãy trân trọng thời gian làm việc cùng nhau, bởi đồng đội chính là sức mạnh lớn nhất. (Khuyết danh)",
        "Thực tế luôn là người thầy vĩ đại nhất. Hãy luôn giữ tinh thần học hỏi với tâm thế ly nước rỗng. (Khuyết danh)",
        "Khi bạn cảm thấy mệt mỏi, hãy nhớ lý do vì sao bạn bắt đầu. (Khuyết danh)",
        "Sự chuẩn bị chu đáo quyết định 80% thắng lợi của mọi kế hoạch. (Khuyết danh)",
        "Hôm nay là một cơ hội tuyệt vời để tạo nên những bước đột phá mới! (Khuyết danh)",
        "Hãy giữ cho tinh thần luôn lạc quan, trí tuệ luôn minh mẫn và trái tim luôn nhiệt huyết. (Khuyết danh)",
        "Chúc bạn một ngày làm việc tràn đầy cảm hứng và gặt hái nhiều thành công tốt đẹp! (VIET.MOS)",
        "Sự thấu hiểu và sẻ chia giữa các thành viên tạo nên một tập thể vững mạnh không thể phá vỡ. (Khuyết danh)"
    ]
        
    daily_quotes_jp_js = json.dumps(quotes_jp, ensure_ascii=False)
    daily_quotes_vn_js = json.dumps(quotes_vn, ensure_ascii=False)
    lang = st.session_state.get('lang', 'VN')

    
    countdown_data = get_countdown_info()
    countdown_html = ""
    if countdown_data:
        if countdown_data["type"] == "upcoming":
            days = countdown_data["days_left"]
            target = countdown_data["target_date"].strftime("%d/%m/%Y")
            reason = countdown_data["reason"]
            msg = t(f"Chỉ còn&nbsp;<b>{days} ngày</b>&nbsp;nữa là đến&nbsp;<b>{reason}</b>&nbsp;({target})! Cố lên nào 🚀", f"<b>{reason}</b>&nbsp;({target})まであと&nbsp;<b>{days}日</b>！頑張りましょう🚀")
            bg_color = "rgba(255, 140, 0, 0.15)"
            border_color = "rgba(255, 140, 0, 0.4)"
            text_color = "#d35400"
        elif countdown_data["type"] == "today_single":
            reason = countdown_data["reason"]
            msg = t(f"Hôm nay là ngày nghỉ:&nbsp;<b>{reason}</b>! Chúc bạn một ngày nghỉ ngơi vui vẻ 🎉", f"本日は&nbsp;<b>{reason}</b>&nbsp;でお休みです！よい休日を🎉")
            bg_color = "rgba(46, 204, 113, 0.15)"
            border_color = "rgba(46, 204, 113, 0.4)"
            text_color = "#27ae60"
        elif countdown_data["type"] == "during_block":
            days = countdown_data["days_left"]
            target = countdown_data["target_date"].strftime("%d/%m/%Y")
            reason = countdown_data["reason"]
            msg = t(f"Đang trong kỳ nghỉ&nbsp;<b>{reason}</b>. Còn&nbsp;<b>{days} ngày</b>&nbsp;nữa là đi làm lại ({target}) 🏖️", f"<b>{reason}</b>&nbsp;の休暇中です。出社まで残り&nbsp;<b>{days}日</b>&nbsp;({target}) 🏖️")
            bg_color = "rgba(0, 176, 240, 0.15)"
            border_color = "rgba(0, 176, 240, 0.4)"
            text_color = "#0075a0"
            
        countdown_html = f'<div style="position: absolute; top: calc(-13vh + 54px); width: 100%; display: flex; justify-content: center; z-index: 500; pointer-events: none;"><div style="background: {bg_color}; border: 1px solid {border_color}; backdrop-filter: blur(4px); color: {text_color}; padding: 6px 16px; border-radius: 20px; font-size: 0.9rem; font-family: \'Times New Roman\', serif; font-weight: 500; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; align-items: center; pointer-events: auto;">{msg}</div></div>'
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
        transition: opacity 0.4s ease;
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
            let currentQuoteIdx = -1;
            function updateQuote() {{
                const list = lang === "JP" ? quotes_jp : quotes_vn;
                if (!list || list.length === 0) return;
                let nextIdx = Math.floor(Math.random() * list.length);
                if (list.length > 1 && nextIdx === currentQuoteIdx) {{
                    nextIdx = (nextIdx + 1) % list.length;
                }}
                currentQuoteIdx = nextIdx;
                const el = document.getElementById("greeting");
                el.style.opacity = 0;
                setTimeout(() => {{
                    el.innerText = list[nextIdx];
                    el.style.opacity = 1;
                }}, 400);
            }}
            function updateTime() {{
                const now = new Date();
                const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
                const local = new Date(utc + (3600000 * offset));
                let h = local.getHours(); let m = local.getMinutes(); let s = local.getSeconds();
                h = h < 10 ? "0" + h : h; m = m < 10 ? "0" + m : m; s = s < 10 ? "0" + s : s;
                document.getElementById("time").innerText = h + ":" + m + ":" + s;
            }}
            setInterval(updateTime, 1000);
            updateTime();
            updateQuote();
            setInterval(updateQuote, 18000);
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
        <div style="position: relative; height: 0px; width: 100%; overflow: visible; margin: 0; padding: 0;">
            <div style="position: absolute; top: -13vh; width: 100%; display: flex; justify-content: center;">
                <iframe srcdoc="{clock_html_escaped}" style="width: 100%; height: 50px; border: none; overflow: hidden; background: transparent;"></iframe>
            </div>
            {countdown_html}
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
    # Empty space to position buttons correctly on the wave
    st.markdown("<div style='height: 2.5vh;'></div>", unsafe_allow_html=True)
    
    # Render Buttons using standard Streamlit columns
    # Increase the outer spacers to push the buttons closer to the center
    col_spacer_left, col1, col_spacer_mid, col2, col_spacer_right = st.columns([3, 1.5, 0.2, 1.5, 3])
    
    with col1:
        if st.button(t("TÍNH LƯƠNG TĂNG CA", "残業代計算"), key="btn_ot"):
            st.session_state['current_page'] = 'ot_calc'
            st.session_state['menu_selection'] = t(":material/folder: **DỮ LIỆU DỰ ÁN**", ":material/folder: **プロジェクト**")
            st.session_state['ot_menu_expanded'] = True
            st.session_state['show_page_transition'] = True
            st.rerun()
            
    with col2:
        if st.button(t("TÍNH LƯƠNG INCENTIVE", "インセンティブ計算"), key="btn_inc"):
            st.session_state['current_page'] = 'incentive_calc'
            st.session_state['menu_selection'] = t(":material/payments: **INCENTIVE**", ":material/payments: **インセンティブ**")
            st.session_state['ot_menu_expanded'] = False
            st.session_state['show_page_transition'] = True
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
