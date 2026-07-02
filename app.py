import streamlit as st

st.set_page_config(page_title="OT & Incentive Calculator", layout="wide", initial_sidebar_state="expanded")

if 'pending_toast' in st.session_state:
    st.toast(st.session_state['pending_toast'], icon=":material/check_circle:")
    del st.session_state['pending_toast']



# Custom CSS for a beautiful corporate look (White & Blue)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');

    /* Global Font */
    html, body, [class*="css"]  {
        font-family: 'Times New Roman', serif !important;
    }
    
    /* Hide default streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Adjust spacing for horizontal rules */
    hr {
        margin-top: 15px !important;
        margin-bottom: 15px !important;
        border-top: 1px solid rgba(0, 176, 240, 0.2) !important;
    }
    
    /* Custom CSS for Toast notifications */
    [data-testid="stToast"] {
        background-color: #10b981 !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 5px 20px rgba(16, 185, 129, 0.4) !important;
        padding: 15px 20px !important;
    }
    [data-testid="stToast"] * {
        color: white !important;
    }
    [data-testid="stToast"] svg {
        fill: white !important;
    }

    /* Metric cards styling - matching the clean soft shadow design */
    [data-testid="stMetric"] {
        background: #00B0F0 !important;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        padding: 10px 15px !important;
    }
    [data-testid="stMetric"] * {
        color: #ffffff !important;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
    }
    
    /* Metric Delta (e.g. Thưởng) */
    [data-testid="stMetricDelta"] {
        margin-top: 8px !important;
    }
    [data-testid="stMetricDelta"] > div {
        background: transparent !important;
        background-color: transparent !important;
    }
    [data-testid="stMetricDelta"] * {
        background: transparent !important;
        background-color: transparent !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 500 !important;
        font-size: 15px !important;
    }
    [data-testid="stMetricDelta"] svg {
        fill: #ffffff !important;
        width: 16px !important;
        height: 16px !important;
    }
    
    /* -----------------------------------------
       SOLID BLOCK TABS
       ----------------------------------------- */
    [data-testid="stTabs"] {
        margin-bottom: 20px;
    }
    [data-testid="stTabs"] div[role="tablist"] {
        background-color: transparent !important;
        border-radius: 0 !important;
        padding: 0 !important;
        gap: 8px !important;
        border-bottom: 3px solid #00B0F0 !important;
        display: flex !important;
        width: 100% !important;
        flex-wrap: wrap !important;
        box-shadow: none !important;
    }
    
    [data-testid="stTabs"] button[data-baseweb="tab"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-bottom: none !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 28px !important;
        margin: 0 !important;
        color: #475569 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        margin-bottom: -3px !important;
    }
    
    [data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        color: #00B0F0 !important;
        background-color: #f1f5f9 !important;
    }
    
    [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #00B0F0 !important;
        color: #ffffff !important;
        border: 1px solid #00B0F0 !important;
        border-bottom: 3px solid #00B0F0 !important;
        box-shadow: none !important;
    }

    [data-testid="stTabs"] div[data-baseweb="tab-highlight"],
    [data-testid="stTabs"] div[data-baseweb="tab-border"] {
        display: none !important;
    }

    h1, h2, h3 {
        color: #2c3e50;
        text-transform: uppercase;
        font-weight: bold !important;
        position: relative;
        padding-bottom: 12px;
        margin-bottom: 40px;
        width: fit-content;
    }
    
    /* Add a custom blue line under h2 and h3 like the reference image */
    h2::after, h3::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: 0;
        height: 3px;
        width: calc(100% - 15px);
        background-color: #00B0F0;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 30px !important;
        font-weight: bold;
        text-transform: uppercase;
        padding: 10px 30px;
        font-size: 13px !important;
        border: 2px solid #00B0F0 !important;
        background-color: transparent !important;
        color: #00B0F0 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #00B0F0 !important;
        color: white !important;
        box-shadow: 0 5px 15px rgba(0, 176, 240, 0.3);
    }

    /* Download Buttons */
    [data-testid="stDownloadButton"] > button {
        border-radius: 30px !important;
        font-weight: bold;
        text-transform: uppercase;
        padding: 10px 20px;
        font-size: 13px !important;
        border: 2px solid #00B0F0 !important;
        background-color: #00B0F0 !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background-color: #008CBA !important;
        border-color: #008CBA !important;
        box-shadow: 0 5px 15px rgba(0, 176, 240, 0.4);
    }

    /* File Uploader */
    [data-testid="stFileUploaderDropzone"] {
        background-color: #ffffff !important;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px dashed rgba(0, 176, 240, 0.5) !important;
        padding: 20px !important;
    }
    
    [data-testid="stFileUploaderDropzone"] button {
        border-radius: 30px !important;
        font-weight: bold;
        text-transform: uppercase;
        padding: 10px 30px !important;
        font-size: 13px !important;
        border: 2px solid #00B0F0 !important;
        background-color: #00B0F0 !important;
        color: #ffffff !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #008CBA !important;
        border-color: #008CBA !important;
        box-shadow: 0 5px 15px rgba(0, 176, 240, 0.4);
    }
    
    /* Material Icons in Main Body */
    [data-testid="stMainBlockContainer"] .material-symbols-rounded,
    [data-testid="stMainBlockContainer"] label[data-testid="stWidgetLabel"] .st-icon,
    [data-testid="stMainBlockContainer"] label[data-testid="stWidgetLabel"] span[translate="no"],
    [data-testid="stMainBlockContainer"] label[data-testid="stWidgetLabel"] i {
        color: #00B0F0 !important;
    }

    /* Input Fields */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #f8fafc !important;
        transition: all 0.3s ease !important;
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #00B0F0 !important;
        box-shadow: 0 0 0 2px rgba(0, 176, 240, 0.2) !important;
        background-color: #ffffff !important;
    }

    /* Dropdown Hover Effects */
    [role="option"]:hover,
    [role="option"][aria-selected="true"],
    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] li:hover {
        background-color: #00B0F0 !important;
        color: #ffffff !important;
    }
    [role="option"]:hover *,
    [role="option"][aria-selected="true"] *,
    [data-baseweb="popover"] li:hover *,
    [data-baseweb="menu"] li:hover * {
        color: #ffffff !important;
    }
    
    /* Highlight Data Editor Delete Button (Trash Can) */
    [data-testid="stDataEditor"] button[aria-label*="delete" i],
    [data-testid="stDataEditor"] button[title*="delete" i],
    [data-testid="stElementToolbar"] button[aria-label*="delete" i],
    [data-testid="stElementToolbar"] button[title*="delete" i] {
        border: 2px solid #ff4b4b !important;
        background-color: #fff0f0 !important;
        border-radius: 6px !important;
        box-shadow: 0 0 8px rgba(255,75,75,0.3) !important;
    }
    
    [data-testid="stDataEditor"] button[aria-label*="delete" i] svg,
    [data-testid="stDataEditor"] button[title*="delete" i] svg,
    [data-testid="stElementToolbar"] button[aria-label*="delete" i] svg,
    [data-testid="stElementToolbar"] button[title*="delete" i] svg {
        fill: #ff4b4b !important;
        color: #ff4b4b !important;
    }
    
    /* === SIDEBAR STYLING === */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        box-shadow: 4px 0 25px rgba(0,0,0,0.12);
    }

    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: #2c3e50 !important;
        font-family: 'Times New Roman', serif !important;
    }

    /* Radio buttons in sidebar */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: transparent;
        padding: 12px 15px;
        border-radius: 8px;
        border: 1px solid transparent;
        margin: 4px 15px;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #f8f9fa !important;
        transform: translateX(3px);
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover p {
        color: #0090d0 !important;
    }

    /* Selected Menu Item */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: #00a8e8 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 168, 232, 0.3) !important;
        transform: translateX(5px);
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 900 !important;
    }

    /* Hide radio button circles */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:not(:has(p)):not([data-testid="stMarkdownContainer"]) {
        display: none !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p {
        font-weight: bold;
        font-size: 15px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    /* Flamingo-style collapsible sidebar */
    [data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(0px) !important;
        width: 100px !important;
        min-width: 100px !important;
        max-width: 100px !important;
        overflow-x: hidden !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stApp"]:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stMain"] {
        /* Removed padding-left to prevent shifting */
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p strong {
        display: none !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p {
        font-size: 26px !important;
        text-align: center;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] span {
        font-size: 26px !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] {
        margin-top: -30px !important;
        width: 100px !important;
        margin-left: -1rem !important; /* override Streamlit sidebar padding */
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label {
        margin: 5px 15px !important;
        width: 70px !important;
        padding: 10px 0 !important;
        border-left: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transform: none !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label:hover,
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label:has(input:checked) {
        transform: none !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] {
        width: 100% !important;
        text-align: center !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] img,
    [data-testid="stSidebar"][aria-expanded="false"] h2,
    [data-testid="stSidebar"][aria-expanded="false"] .sidebar-footer-text,
    [data-testid="stSidebar"][aria-expanded="false"] .stButton {
        display: none !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label:nth-child(1) p::after {
        display: none !important;
    }
    
    /* Main category styling for the first item (now clickable) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1):not(:has(input:checked)) {
        border-bottom: 1px solid rgba(0,0,0,0.1) !important;
        padding-bottom: 10px;
        margin-bottom: 10px;
        border-radius: 0;
        background-color: transparent !important;
        box-shadow: none !important;
        transform: none !important;
        cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1):not(:has(input:checked)) p {
        text-shadow: none !important;
        font-size: 16px;
        color: #2c3e50 !important;
        font-weight: bold;
        transition: all 0.3s;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1):not(:has(input:checked)):hover p {
        color: #00a8e8 !important;
        text-shadow: none !important;
    }
    
    /* 5. PAGE FADE-IN TRANSITION */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Make the title area cleaner */
    .block-container {
        animation: fadeIn 0.4s ease-out;
        padding-top: 1rem !important;
        margin-top: -1.5rem;
        padding-bottom: 5rem;
    }
    
    /* 4. GLASSMORPHISM CARDS FOR TABLES & METRICS & CONTAINERS */


    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        overflow: visible !important;
        width: 100% !important;
        position: relative !important;
    }

    /* Đưa toàn bộ viền xanh và bo góc vào div chứa bảng thực sự bên trong (trừ Toolbar) */
    [data-testid="stDataFrame"] > div:not([data-testid="stElementToolbar"]),
    [data-testid="stDataEditor"] > div:not([data-testid="stElementToolbar"]) {
        background: #ffffff !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(0, 176, 240, 0.1) !important;
        border: 2px solid #00B0F0 !important;
        box-sizing: border-box !important;
        width: calc(100% - 6px) !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
    }

    /* Bảng nằm trong Expander thì bỏ viền xanh vì Expander đã có viền */
    [data-testid="stExpander"] [data-testid="stDataFrame"] > div:not([data-testid="stElementToolbar"]),
    [data-testid="stExpander"] [data-testid="stDataEditor"] > div:not([data-testid="stElementToolbar"]) {
        border: 1px solid rgba(0,0,0,0.1) !important;
        box-shadow: none !important;
    }
    [data-testid="stDataFrame"] th, [data-testid="stDataEditor"] th {
        background-color: #00a8e8 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }
    [data-testid="stDataFrame"]:hover, [data-testid="stDataEditor"]:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    

    
    /* Compact popover for history delete */
    [data-testid="stPopoverBody"] {
        max-width: 280px !important;
    }
    [data-testid="stPopoverBody"] button {
        font-size: 11px !important;
        padding: 4px 8px !important;
        min-height: 24px !important;
        height: auto !important;
        line-height: 1.2 !important;
        border-radius: 4px !important;
        width: 100% !important;
        white-space: nowrap !important;
    }
    [data-testid="stPopoverBody"] button p,
    [data-testid="stPopoverBody"] button div,
    [data-testid="stPopoverBody"] button span {
        white-space: nowrap !important;
        font-size: 11px !important;
        line-height: 1.2 !important;
    }
    [data-testid="stPopover"] > button {
        font-size: 12px !important;
        padding: 2px 10px !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

from components.ot_manual import render_base_data, render_project_data
from components.ot_excel import render_ot_excel
from components.incentive_ui import render_incentive
from components.welcome import render_welcome
from components.action_history_ui import render_action_history
from logic.i18n import t

@st.dialog(t("📖 HƯỚNG DẪN SỬ DỤNG", "📖 使い方ガイド"))
def show_user_guide():
        st.markdown(t("""
### 1. OVERTIME
- **Dữ liệu dự án**: Nhập thủ công thời gian tăng ca cho từng dự án. Dữ liệu nhân sự và lương được tự động đồng bộ từ Cài đặt chung.
- **Nhập hàng loạt (Excel)**: Upload trực tiếp file dữ liệu để hệ thống tự động nhận diện và tính toán thời gian tăng ca hàng loạt cực kỳ nhanh chóng.

### 2. INCENTIVE
- Tự động trích xuất và gợi ý dữ liệu từ các dự án đã thực hiện.
- Đánh giá hiệu suất làm việc dựa trên số giờ làm việc thực tế so với kế hoạch, từ đó quy đổi chính xác ra mức tiền thưởng (Incentive).
- **Ước tính Incentive**: Kéo thanh trượt để giả lập và xem trước mức tiền thưởng thay đổi thế nào khi Giờ công thực tế thay đổi.

### 3. LỊCH SỬ THAO TÁC
- Các file Excel dữ liệu đã xuất ra sẽ được tự động lưu trữ an toàn.
- Dễ dàng xem lại, tải xuống file cũ hoặc xóa bỏ dữ liệu thừa.

### 4. CÀI ĐẶT CHUNG
- Thiết lập thông tin nhân sự, mức lương cơ bản (Gross) và các cấu hình hệ thống.
- **Lưu ý**: Vui lòng thiết lập dữ liệu tại đây trước để hệ thống có cơ sở tính toán chính xác nhất.
    """, """
### 1. 残業代計算 (OVERTIME)
- **プロジェクト**: 各プロジェクトの残業時間を手動で入力します。スタッフデータや給与情報は一般設定から自動的に同期されます。
- **一括入力 (Excel)**: Excelデータをアップロードするだけで、システムが自動的に認識し、スマートかつ迅速に一括計算します。

### 2. インセンティブ (INCENTIVE)
- 実行済みのプロジェクトからデータを自動的に抽出・提案します。
- 計画工数と実績工数の差に基づいてパフォーマンスを評価し、獲得インセンティブを正確に算出します。
- **予想インセンティブ**: スライダーを動かして、実工数の変化に伴う獲得インセンティブの変動をシミュレーションできます。

### 3. 操作履歴
- 出力されたすべてのExcelファイルは自動的かつ安全に保存されます。
- いつでも過去のファイルの確認、再ダウンロード、不要なファイルの削除が可能です。

### 4. 一般設定
- スタッフ情報、基本給（Gross）、およびシステムの基本構成を設定します。
- **注意**: 他のセクションで正確な計算を行うために、まずここで初期データを設定してください。
    """))

# --- Creative Language Switcher (Always visible) ---
st.markdown("""
<style>
/* Creative Pill Toggle for Language Switcher */
div[role="radiogroup"][aria-label="LangToggle_123"] {
    background-color: rgba(0, 176, 240, 0.08) !important;
    border-radius: 30px !important;
    padding: 5px !important;
    display: inline-flex !important;
    gap: 0 !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.05) !important;
    float: right;
}

/* SAFELY hide radio circles: Hide any div inside the label that is NOT the text container */
div[role="radiogroup"][aria-label="LangToggle_123"] label > div:not(:has(p)):not([data-testid="stMarkdownContainer"]) {
    display: none !important;
}
div[role="radiogroup"][aria-label="LangToggle_123"] input[type="radio"] {
    display: none !important;
}

div[role="radiogroup"][aria-label="LangToggle_123"] label {
    padding: 6px 18px !important;
    margin: 0 !important;
    border-radius: 25px !important;
    cursor: pointer !important;
    background-color: transparent !important;
    transition: all 0.3s ease !important;
    border: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0 !important;
    color: transparent !important;
}

/* The active label */
div[role="radiogroup"][aria-label="LangToggle_123"] label[data-checked="true"],
div[role="radiogroup"][aria-label="LangToggle_123"] label:has(input:checked) {
    background-color: #00B0F0 !important;
    box-shadow: 0 3px 10px rgba(0, 176, 240, 0.4) !important;
}

/* Target specifically the text paragraphs inside the label */
div[role="radiogroup"][aria-label="LangToggle_123"] label p {
    font-weight: 800 !important;
    font-size: 14px !important;
    color: #00B0F0 !important;
    margin: 0 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    letter-spacing: 0.5px !important;
    line-height: 1 !important;
}

div[role="radiogroup"][aria-label="LangToggle_123"] label[data-checked="true"] p,
div[role="radiogroup"][aria-label="LangToggle_123"] label:has(input:checked) p {
    color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)

# Dynamically adjust position based on current page
current_page = st.session_state.get('current_page', 'welcome')
lang_top_pos = "45px" if current_page == "welcome" else "2px"
st.markdown(f"""
<style>
/* Floating Language Switcher Container */
.lang-switcher-container {{
    position: fixed !important;
    top: {lang_top_pos} !important;
    right: 20px !important;
    z-index: 9999 !important;
}}
</style>
""", unsafe_allow_html=True)

col_space, col_lang = st.columns([8, 2])
with col_lang:
    st.markdown("<div class='lang-switcher-container'>", unsafe_allow_html=True)
    def update_lang():
        val = st.session_state['lang_radio']
        st.session_state['lang'] = 'VN' if 'VN' in val else 'JP'
        
    st.radio(
        "LangToggle_123", 
        options=["VN", "JP"], 
        index=0 if st.session_state.get('lang', 'VN') == 'VN' else 1,
        horizontal=True,
        key="lang_radio",
        on_change=update_lang,
        label_visibility="hidden"
    )
    st.markdown("</div>", unsafe_allow_html=True)


if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'welcome'

if st.session_state['current_page'] == 'welcome':
    render_welcome()
else:
    # Main App specific CSS
    st.markdown("""
    <style>
        .stApp {
            background: #f4f7f9 !important;
            background-color: #f4f7f9 !important;
        }
        .stButton>button {
            background-color: #ffffff !important;
        }
        /* Make Lang toggle background white in main app */
        div[role="radiogroup"][aria-label="LangToggle_123"] {
            background-color: #ffffff !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    # Sidebar Menu
    with st.sidebar:
        import os
        logo_menu_path = "logo_menu.png" if os.path.exists("logo_menu.png") else ("logo_menu.jpg" if os.path.exists("logo_menu.jpg") else None)
        logo_path = logo_menu_path or ("logo.png" if os.path.exists("logo.png") else ("logo.jpg" if os.path.exists("logo.jpg") else None))
        if logo_path:
            import base64
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            ext = "png" if logo_path.endswith(".png") else "jpeg"
            st.markdown(f"""
            <style>
            [data-testid="stSidebar"] .stButton:first-of-type button {{
                background-image: url("data:image/{ext};base64,{encoded}");
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                height: 80px;
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }}
            [data-testid="stSidebar"] .stButton:first-of-type button p {{
                visibility: hidden;
            }}
            [data-testid="stSidebar"] .stButton:first-of-type button:hover {{
                transform: scale(1.05);
                transition: transform 0.3s;
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }}
            </style>
            """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 4, 1])
            with col2:
                if st.button("HOME", use_container_width=True):
                    st.session_state['current_page'] = 'welcome'
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            if st.button(t("QUAY LẠI TRANG CHỦ", "ホームに戻る"), use_container_width=True):
                st.session_state['current_page'] = 'welcome'
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
        
        menu_title = t("MENU", "管理メニュー")
        st.markdown(f"<h2 style='text-align: center; width: 100%; margin-bottom: 5px; font-weight: bold; letter-spacing: 2px;'>{menu_title}</h2>", unsafe_allow_html=True)
        
        options = [
            t(":material/timer: **OVERTIME**", ":material/timer: **残業代計算**"),
            t(":material/folder: **DỮ LIỆU DỰ ÁN**", ":material/folder: **プロジェクト**"),
            t(":material/edit_document: **NHẬP HÀNG LOẠT (EXCEL)**", ":material/edit_document: **一括入力**"),
            t(":material/payments: **INCENTIVE**", ":material/payments: **インセンティブ**"),
            t(":material/history: **LỊCH SỬ THAO TÁC**", ":material/history: **操作履歴**"),
            t(":material/settings: **CÀI ĐẶT CHUNG**", ":material/settings: **一般設定**")
        ]
        
        if 'ot_menu_expanded' not in st.session_state:
            st.session_state['ot_menu_expanded'] = True
            
        header_text = t(":material/timer: **OVERTIME**", ":material/timer: **残業代計算**")
        
        options = [
            header_text,
            t(":material/folder: **DỮ LIỆU DỰ ÁN**", ":material/folder: **プロジェクト**"),
            t(":material/edit_document: **NHẬP HÀNG LOẠT (EXCEL)**", ":material/edit_document: **一括入力**"),
            t(":material/payments: **INCENTIVE**", ":material/payments: **インセンティブ**"),
            t(":material/history: **LỊCH SỬ THAO TÁC**", ":material/history: **操作履歴**"),
            t(":material/settings: **CÀI ĐẶT CHUNG**", ":material/settings: **一般設定**")
        ]
        
        if st.session_state['ot_menu_expanded']:
            st.markdown("""
            <style>
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1) p::after {
                    content: " ▼";
                    color: #00a8e8 !important;
                }
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1):has(input:checked) p::after {
                    color: #FFFFFF !important;
                }
                /* Sub-menu items (2, 3) */
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(2),
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(3) {
                    margin-left: 30px;
                    padding-left: 10px;
                    border-left: 2px solid rgba(0, 0, 0, 0.1) !important;
                    border-radius: 0 8px 8px 0;
                }
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(2):hover,
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(3):hover {
                    border-left: 2px solid #00a8e8 !important;
                }
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(2):has(input:checked),
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(3):has(input:checked) {
                    border-left: none !important;
                }
                /* Main items 4, 5, 6, 7 styling */
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(4),
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(5),
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(6),
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(7) {
                    margin-top: 15px;
                }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1) p::after {
                    content: " ▶";
                    color: #00a8e8 !important;
                }
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1):has(input:checked) p::after {
                    color: #FFFFFF !important;
                }
                /* Hide sub-items when collapsed */
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(2),
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(3),
                [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label:nth-child(2),
                [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] > label:nth-child(3) {
                    display: none !important;
                }
                
                /* Main items 4, 5, 6, 7 styling when collapsed */
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(4),
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(5),
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(6),
                [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(7) {
                    margin-top: 15px;
                }
            </style>
            """, unsafe_allow_html=True)
            
        # We need to map English internal keys to options to persist selection across language changes
        if 'menu_selection' not in st.session_state:
            st.session_state['menu_selection'] = t(":material/folder: **DỮ LIỆU DỰ ÁN**", ":material/folder: **プロジェクト**")
        elif st.session_state['menu_selection'] not in options:
            old_sel = st.session_state['menu_selection']
            vn_opts = [
                ":material/timer: **OVERTIME**",
                ":material/folder: **DỮ LIỆU DỰ ÁN**",
                ":material/edit_document: **NHẬP HÀNG LOẠT (EXCEL)**",
                ":material/payments: **INCENTIVE**",
                ":material/history: **LỊCH SỬ THAO TÁC**",
                ":material/settings: **CÀI ĐẶT CHUNG**"
            ]
            jp_opts = [
                ":material/timer: **残業代計算**",
                ":material/folder: **プロジェクト**",
                ":material/edit_document: **一括入力**",
                ":material/payments: **インセンティブ**",
                ":material/history: **操作履歴**",
                ":material/settings: **一般設定**"
            ]
            try:
                if old_sel in vn_opts:
                    idx = vn_opts.index(old_sel)
                    st.session_state['menu_selection'] = jp_opts[idx] if st.session_state.get('lang', 'VN') == 'JP' else vn_opts[idx]
                elif old_sel in jp_opts:
                    idx = jp_opts.index(old_sel)
                    st.session_state['menu_selection'] = vn_opts[idx] if st.session_state.get('lang', 'VN') == 'VN' else jp_opts[idx]
                else:
                    st.session_state['menu_selection'] = options[1]
            except Exception:
                st.session_state['menu_selection'] = options[1]
            
        def on_menu_change():
            sel = st.session_state['menu_selection']
            if sel == t(":material/timer: **OVERTIME**", ":material/timer: **残業代計算**"):
                st.session_state['ot_menu_expanded'] = not st.session_state['ot_menu_expanded']
                st.session_state['menu_selection'] = st.session_state.get('prev_ot_selection', t(":material/folder: **DỮ LIỆU DỰ ÁN**", ":material/folder: **プロジェクト**"))
            else:
                st.session_state['prev_ot_selection'] = sel
            
        st.radio(
            "Điều hướng",
            options,
            key="menu_selection",
            on_change=on_menu_change,
            label_visibility="collapsed"
        )
        
        menu_selection = st.session_state['menu_selection']
        
        st.markdown("""
    <div class='sidebar-footer-container'>
        <div id='sidebar-clock' style='
            text-align: center;
            margin: 0 auto 20px auto;
            width: 80%;
            background: linear-gradient(145deg, #ffffff, #f0f8ff);
            border: 1px solid rgba(0, 168, 232, 0.3);
            border-radius: 16px;
            padding: 12px 10px;
            box-shadow: 0 4px 15px rgba(0, 168, 232, 0.15);
            color: #00a8e8;
            transition: all 0.3s ease;
        '>
            <div id='clock-time' style='font-family: "Courier New", monospace; font-size: 26px; font-weight: 900; letter-spacing: 2px; text-shadow: 0 2px 4px rgba(0, 168, 232, 0.2);'>00:00:00</div>
            <div id='clock-date' style='font-size: 11px; font-weight: 700; opacity: 0.8; letter-spacing: 1px; margin-top: 5px; color: #34495e;'>---</div>
        </div>
        <div class='sidebar-footer-text' style='text-align: center; opacity: 0.9; font-size: 12px; font-weight: bold; letter-spacing: 1px; color: #34495e;'>
            VIET.MOS COMPANY LIMITED<br><br>INTERNAL TOOL V1.0
        </div>
    </div>
""", unsafe_allow_html=True)
        import streamlit.components.v1 as components
        components.html("""
        <script>
            window.parent.requestAnimationFrame(() => {
                const doc = window.parent.document;
                const footer = doc.querySelector('.sidebar-footer-container');
                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                if (footer && sidebar) {
                    let elContainer = footer;
                    while(elContainer && !elContainer.classList.contains('element-container')) {
                        elContainer = elContainer.parentElement;
                        if(elContainer && elContainer.tagName === 'BODY') break;
                    }
                    if(elContainer && elContainer.classList.contains('element-container')) {
                        elContainer.style.position = 'fixed';
                        elContainer.style.bottom = '40px'; /* Raised from 20px */
                        elContainer.style.zIndex = '999';
                        
                        const updateWidth = () => {
                            const rect = sidebar.getBoundingClientRect();
                            elContainer.style.width = rect.width + 'px';
                            elContainer.style.left = rect.left + 'px'; /* Explicitly match sidebar left edge */
                        };
                        
                        updateWidth();
                        const resizeObserver = new window.parent.ResizeObserver(() => {
                            updateWidth();
                        });
                        resizeObserver.observe(sidebar);
                        
                        // Clock Logic
                        const timeEl = doc.getElementById('clock-time');
                        const dateEl = doc.getElementById('clock-date');
                        const updateClock = () => {
                            if (!timeEl || !dateEl) return;
                            const now = new Date();
                            const hrs = String(now.getHours()).padStart(2, '0');
                            const mins = String(now.getMinutes()).padStart(2, '0');
                            const secs = String(now.getSeconds()).padStart(2, '0');
                            timeEl.innerText = `${hrs}:${mins}:${secs}`;
                            
                            const days = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
                            const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
                            const dayName = days[now.getDay()];
                            const date = String(now.getDate()).padStart(2, '0');
                            const month = months[now.getMonth()];
                            const year = now.getFullYear();
                            dateEl.innerText = `${dayName}, ${date} ${month} ${year}`;
                        };
                        updateClock();
                        setInterval(updateClock, 1000);
                    }
                }
            });
        </script>
        """, height=0)

    # Main Content Area
    st.markdown("""
    <div style="text-align: center; color: #00a8e8; font-family: 'Times New Roman', serif !important; font-size: 2.8rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 1px; line-height: 1.2;">
        OVERTIME & INCENTIVE MANAGEMENT SYSTEM
    </div>
    <div style='text-align: center; color: #00a8e8; font-family: "Times New Roman", serif; font-size: 1.2rem; margin-top: 10px; margin-bottom: 30px; font-weight: bold; font-style: italic; letter-spacing: 2px;'>
        VIET.MOS COMPANY LIMITED
    </div>
    """, unsafe_allow_html=True)
    
    # Floating Guide Button (Using CSS adjacent sibling trick to target Streamlit element container)
    st.markdown("""
    <style>
    /* Target the button container that immediately follows the anchor */
    div[data-testid="stElementContainer"]:has(#guide-button-anchor) + div[data-testid="stElementContainer"] {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 9999 !important;
        width: auto !important;
    }
    
    div[data-testid="stElementContainer"]:has(#guide-button-anchor) + div[data-testid="stElementContainer"] button {
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        background-color: #00B0F0 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
        padding: 0 !important;
    }
    div[data-testid="stElementContainer"]:has(#guide-button-anchor) + div[data-testid="stElementContainer"] button p {
        color: white !important;
        font-size: 26px !important;
        font-weight: bold !important;
        margin: 0 !important;
        line-height: 1 !important;
    }
    div[data-testid="stElementContainer"]:has(#guide-button-anchor) + div[data-testid="stElementContainer"] button:hover {
        transform: scale(1.1) !important;
        background-color: #0090d0 !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
    }
    </style>
    <div id="guide-button-anchor"></div>
    """, unsafe_allow_html=True)
    
    if st.button("?", key="floating_guide_btn", help=t("Hướng dẫn sử dụng", "使い方ガイド")):
        show_user_guide()
    
    if "OVERTIME" in menu_selection or "残業代計算" in menu_selection or menu_selection == t(":material/folder: **DỮ LIỆU DỰ ÁN**", ":material/folder: **プロジェクト**"):
        render_project_data()
    elif menu_selection == t(":material/edit_document: **NHẬP HÀNG LOẠT (EXCEL)**", ":material/edit_document: **一括入力**"):
        render_ot_excel()
    elif menu_selection == t(":material/payments: **INCENTIVE**", ":material/payments: **インセンティブ**"):
        render_incentive()
    elif menu_selection == t(":material/history: **LỊCH SỬ THAO TÁC**", ":material/history: **操作履歴**"):
        render_action_history()
    elif menu_selection == t(":material/settings: **CÀI ĐẶT CHUNG**", ":material/settings: **一般設定**"):
        render_base_data()
