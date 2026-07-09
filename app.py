import streamlit as st

st.set_page_config(page_title="OT & Incentive Calculator", layout="wide", initial_sidebar_state="expanded")

if st.session_state.pop('show_page_transition', False):
    from components.skeleton import show_page_transition
    show_page_transition()

if 'pending_toast' in st.session_state:
    st.toast(st.session_state['pending_toast'], icon=":material/check_circle:")
    del st.session_state['pending_toast']

from components.ot_manual import init_session_state
init_session_state()



# Custom CSS for a beautiful corporate look (White & Blue)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    /* Global Font - DO NOT OVERRIDE MATERIAL ICONS */
    html, body, [class*="css"], [class*="st-"]:not([data-testid*="Icon"]):not([class*="icon"]):not([class*="Icon"]) {
        font-family: 'Times New Roman', serif !important;
    }
    
    /* COMPREHENSIVE MATERIAL ICON PROTECTION */
    [data-testid="stIconMaterial"], [data-testid="stIcon"], [data-testid*="Icon"], [class*="Icon"], [class*="icon"], .material-symbols-rounded, .material-symbols-outlined, .material-icons, [class*="material-symbols"], [class*="material-icons"], span[translate="no"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', 'Material Icons Round', sans-serif !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased !important;
    }
    
    /* Ensure sidebar typography gets Times New Roman without touching icons */
    [data-testid="stSidebar"] *:not([data-testid*="Icon"]):not([class*="icon"]):not([class*="Icon"]):not([class*="material"]):not(span[translate="no"]) {
        font-family: 'Times New Roman', serif;
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
    
    /* Metric Delta (e.g. Thﾆｰ盻殤g) */
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
    
    [data-testid="stTabs"] div[role="tablist"] > *,
    [data-testid="stTabs"] [role="tab"],
    [data-testid="stTabs"] [data-baseweb="tab"] {
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
        height: auto !important;
        cursor: pointer !important;
    }
    
    [data-testid="stTabs"] div[role="tablist"] > *:hover,
    [data-testid="stTabs"] [role="tab"]:hover,
    [data-testid="stTabs"] [data-baseweb="tab"]:hover {
        color: #00B0F0 !important;
        background-color: #f1f5f9 !important;
    }
    
    [data-testid="stTabs"] div[role="tablist"] > *[aria-selected="true"],
    [data-testid="stTabs"] [role="tab"][aria-selected="true"],
    [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
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
    
    /* Disable global blue line on Streamlit dialog main title, but keep on h3 section headings */
    [role="dialog"] h1::after,
    [role="dialog"] h2::after,
    [data-testid="stDialogTitle"]::after {
        display: none !important;
    }
    
    /* Eliminate awkward top gap between dialog title bar and dialog body content */
    [role="dialog"] > div > div:first-child,
    [data-testid="stDialog"] > div > div:first-child,
    [role="dialog"] [data-testid="stDialogHeader"],
    [data-testid="stDialog"] [data-testid="stDialogHeader"] {
        padding-bottom: 0.25rem !important;
        margin-bottom: 0px !important;
    }
    [role="dialog"] > div > div:nth-child(2),
    [data-testid="stDialog"] > div > div:nth-child(2),
    [role="dialog"] [data-testid="stDialogBody"],
    [data-testid="stDialog"] [data-testid="stDialogBody"],
    [role="dialog"] div[data-testid="stVerticalBlock"],
    [data-testid="stDialog"] div[data-testid="stVerticalBlock"] {
        padding-top: 0.25rem !important;
        margin-top: 0px !important;
    }

    /* Enable blue horizontal underline bar under small headings (h3) inside dialogs like main UI */
    [role="dialog"] h3,
    [data-testid="stDialog"] h3 {
        color: #2c3e50 !important;
        text-transform: uppercase !important;
        font-weight: bold !important;
        position: relative !important;
        padding-bottom: 8px !important;
        margin-top: 20px !important;
        margin-bottom: 12px !important;
        width: fit-content !important;
        font-size: 18px !important;
    }
    [role="dialog"] [data-testid="stVerticalBlock"] > div:first-child h3,
    [data-testid="stDialog"] [data-testid="stVerticalBlock"] > div:first-child h3,
    [role="dialog"] h3:first-of-type,
    [data-testid="stDialog"] h3:first-of-type {
        margin-top: 0px !important;
    }
    [role="dialog"] h3::after,
    [data-testid="stDialog"] h3::after {
        content: "" !important;
        position: absolute !important;
        left: 0 !important;
        bottom: 0 !important;
        height: 3px !important;
        width: calc(100% - 5px) !important;
        background-color: #00B0F0 !important;
        display: block !important;
    }

    /* Style all dialog popup titles with blue frame and white text */
    [role="dialog"] [data-testid="stDialogTitle"],
    [data-testid="stDialog"] [data-testid="stDialogTitle"],
    [role="dialog"] h2:first-of-type,
    [data-testid="stDialog"] h2:first-of-type {
        background-color: #00B0F0 !important;
        color: #ffffff !important;
        padding: 14px 22px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 22px !important;
        margin-top: 0px !important;
        margin-bottom: 12px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        display: block !important;
        box-shadow: 0 4px 6px rgba(0, 176, 240, 0.25) !important;
    }
    [role="dialog"] [data-testid="stDialogTitle"] *,
    [data-testid="stDialog"] [data-testid="stDialogTitle"] *,
    [role="dialog"] h2:first-of-type *,
    [data-testid="stDialog"] h2:first-of-type * {
        color: #ffffff !important;
    }
    
    /* Dialog close button styled as clean circle to stand out against blue banner */
    [role="dialog"] button[aria-label="Close"],
    [data-testid="stDialog"] button[aria-label="Close"],
    [role="dialog"] [data-testid="stDialogCloseButton"],
    [data-testid="stDialog"] [data-testid="stDialogCloseButton"] {
        color: #2c3e50 !important;
        background-color: #ffffff !important;
        border: 2px solid #00B0F0 !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        top: 12px !important;
        right: 12px !important;
        z-index: 9999 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
    }
    [role="dialog"] button[aria-label="Close"] svg,
    [data-testid="stDialog"] button[aria-label="Close"] svg,
    [role="dialog"] [data-testid="stDialogCloseButton"] svg,
    [data-testid="stDialog"] [data-testid="stDialogCloseButton"] svg {
        fill: #00B0F0 !important;
        color: #00B0F0 !important;
    }
    
    /* Buttons */

    [data-testid="stMain"] .stButton button,
    div[role="dialog"] .stButton button,
    div[role="dialog"] div[data-testid="stButton"] button,
    div[data-testid="stModal"] .stButton button,
    div[data-testid="stDialog"] .stButton button {
        border-radius: 30px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        padding: 10px 30px !important;
        font-size: 13px !important;
        border: 2px solid #00B0F0 !important;
        background-color: #ffffff !important;
        color: #00B0F0 !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stMain"] .stButton button:hover,
    div[role="dialog"] .stButton button:hover,
    div[role="dialog"] div[data-testid="stButton"] button:hover,
    div[data-testid="stModal"] .stButton button:hover,
    div[data-testid="stDialog"] .stButton button:hover {
        background-color: #00B0F0 !important;
        color: #ffffff !important;
        border-color: #00B0F0 !important;
        box-shadow: 0 5px 15px rgba(0, 176, 240, 0.3) !important;
    }
    [data-testid="stMain"] .stButton button p,
    div[role="dialog"] .stButton button p,
    div[role="dialog"] div[data-testid="stButton"] button p,
    div[data-testid="stModal"] .stButton button p,
    div[data-testid="stDialog"] .stButton button p {
        color: inherit !important;
        font-weight: bold !important;
    }

    /* Download Buttons */
    [data-testid="stMain"] [data-testid="stDownloadButton"] button {
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
    [data-testid="stMain"] [data-testid="stDownloadButton"] button:hover {
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
    div[data-baseweb="select"] > div,
    div[data-testid="stTextInput"] > div > div,
    div[data-testid="stNumberInput"] > div > div,
    div[data-testid="stSelectbox"] > div > div {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #f8fafc !important;
        transition: all 0.3s ease !important;
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="select"] > div:focus-within,
    div[data-testid="stTextInput"] > div > div:focus-within,
    div[data-testid="stNumberInput"] > div > div:focus-within,
    div[data-testid="stSelectbox"] > div > div:focus-within {
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
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: transparent;
        padding: 12px 15px;
        border-radius: 8px;
        border: 1px solid transparent;
        margin: 4px 15px;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: #f8f9fa !important;
        transform: translateX(3px);
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover p {
        color: #0090d0 !important;
    }

    /* Selected Menu Item */
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: #00a8e8 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 168, 232, 0.3) !important;
        transform: translateX(5px);
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 900 !important;
    }

    /* Hide radio button circles SAFELY without touching material icons */
    [data-testid="stSidebar"] div[role="radiogroup"] label div:not(:has(p)):not([data-testid="stMarkdownContainer"]):not([data-testid="stMarkdownContainer"] *),
    [data-testid="stSidebar"] div[role="radiogroup"] label span:not(:has(p)):not([data-testid="stMarkdownContainer"]):not([data-testid="stMarkdownContainer"] *):not([data-testid*="Icon"]):not([class*="Icon"]):not([class*="icon"]):not([class*="material"]),
    [data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"],
    [data-testid="stSidebar"] div[role="radiogroup"] label [data-baseweb="radio"],
    [data-testid="stSidebar"] div[role="radiogroup"] label [data-testid="stRadioCircle"] {
        display: none !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] {
        padding-bottom: 140px !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p {
        font-weight: bold;
        font-size: 13px !important;
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
    
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p strong {
        display: none !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 26px !important;
        text-align: center;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] span {
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

    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label {
        margin: 5px 15px !important;
        width: 70px !important;
        padding: 10px 0 !important;
        border-left: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transform: none !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label:hover,
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label:has(input:checked) {
        transform: none !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
        width: 100% !important;
        text-align: center !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] img,
    [data-testid="stSidebar"][aria-expanded="false"] h2,
    [data-testid="stSidebar"][aria-expanded="false"] .sidebar-footer-text,
    [data-testid="stSidebar"][aria-expanded="false"] .stButton {
        display: none !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label:nth-child(1) p::after {
        display: none !important;
    }
    
    /* Main category styling for the first item (now clickable) */
    [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1):not(:has(input:checked)) {
        border-bottom: 1px solid rgba(0,0,0,0.1) !important;
        padding-bottom: 10px;
        margin-bottom: 10px;
        border-radius: 0;
        background-color: transparent !important;
        box-shadow: none !important;
        transform: none !important;
        cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1):not(:has(input:checked)) p {
        text-shadow: none !important;
        font-size: 13.5px !important;
        color: #2c3e50 !important;
        font-weight: bold;
        transition: all 0.3s;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1):not(:has(input:checked)):hover p {
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

    /* ﾄ脆ｰa toﾃn b盻・vi盻］ xanh vﾃ bo gﾃｳc vﾃo div ch盻ｩa b蘯｣ng th盻ｱc s盻ｱ bﾃｪn trong (tr盻ｫ Toolbar) */
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

    /* B蘯｣ng n蘯ｱm trong Expander thﾃｬ b盻・vi盻］ xanh vﾃｬ Expander ﾄ妥｣ cﾃｳ vi盻］ */
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
    [data-testid="stPopover"] button {
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

@st.dialog(t("✨ HƯỚNG DẪN SỬ DỤNG", "✨ 使い方ガイド"))
def show_user_guide():
        st.markdown("""<style>
    /* Style big dialog title with blue frame and white text specifically for this dialog */
    [role="dialog"] [data-testid="stDialogTitle"],
    [data-testid="stDialog"] [data-testid="stDialogTitle"],
    [role="dialog"] h2:first-of-type,
    [data-testid="stDialog"] h2:first-of-type {
        background-color: #00B0F0 !important;
        color: #ffffff !important;
        padding: 14px 22px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 22px !important;
        margin-top: 0px !important;
        margin-bottom: 5px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        display: block !important;
        box-shadow: 0 4px 6px rgba(0, 176, 240, 0.25) !important;
    }
    [role="dialog"] [data-testid="stDialogTitle"] *,
    [data-testid="stDialog"] [data-testid="stDialogTitle"] *,
    [role="dialog"] h2:first-of-type *,
    [data-testid="stDialog"] h2:first-of-type * {
        color: #ffffff !important;
    }
    </style>""" + t("""
### 1. OVERTIME
- **Dữ liệu dự án**: Nhập thủ công thời gian tăng ca cho từng dự án. Dữ liệu nhân sự và lương được tự động đồng bộ từ Cài đặt chung.
- **Nhập hàng loạt (Excel)**: Upload trực tiếp file dữ liệu, hệ thống tự động nhận diện và tính toán thời gian tăng ca hàng loạt cực kỳ nhanh chóng.

### 2. INCENTIVE
- Tự động trích xuất và gợi ý dữ liệu từ các dự án đã thực hiện.
- Đánh giá hiệu suất làm việc dựa trên số giờ làm việc thực tế so với kế hoạch, từ đó quy đổi chính xác ra mức tiền thưởng (Incentive).
- **Dự tính Incentive**: Kéo thanh trượt để giả lập và xem trước mức tiền thưởng thay đổi thế nào khi Giờ công thực tế thay đổi.

### 3. LỊCH SỬ THAO TÁC
- Các file Excel dữ liệu đã xuất ra sẽ được tự động lưu trữ an toàn.
- Dễ dàng xem lại, tải xuống file cũ hoặc xóa bỏ dữ liệu thừa.

### 4. CÀI ĐẶT CHUNG
- Thiết lập thông tin nhân sự, mức lương cơ bản (Gross) và các cấu hình hệ thống.
- **Lưu ý**: Vui lòng thiết lập dữ liệu tại đây trước để hệ thống có cơ sở tính toán chính xác nhất.
    """, """
### 1. 残業代計算(OVERTIME)
- **プロジェクト**: 各プロジェクトの残業時間を手動で入力します。スタッフデータや給与情報は一般設定から自動的に同期されます。
- **一括入力(Excel)**: Excelデータをアップロードするだけで、システムが自動的に認識し、スマートかつ迅速に一括計算します。

### 2. インセンティブ(INCENTIVE)
- 実行済みのプロジェクトからデータを自動的に抽出・提案します。
- 計画工数と実績工数の差に基づいてパフォーマンスを評価し、獲得インセンティブを正確に算出します。
- **予想インセンティブ**: スライダーを動かして、実工数の変化に伴う獲得インセンティブの変動をシミュレーションできます。

### 3. 操作履歴
- 出力されたすべてのExcelファイルは自動的かつ安全に保存されます。
- いつでも過去のファイルの確認、再ダウンロード、不要なファイルの削除が可能です。

### 4. 一般設定
- スタッフ情報、基本給（Gross）、およびシステムの基本構成を設定します。
- **注意**: 他のセクションで正確な計算を行うために、まずここで初期データを設定してください。
    """), unsafe_allow_html=True)

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
div[role="radiogroup"][aria-label="LangToggle_123"] label div:not(:has(p)):not([data-testid="stMarkdownContainer"]):not([data-testid="stMarkdownContainer"] *) {
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
    font-family: 'Times New Roman', serif !important;
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
        
        # Reset filename inputs to force default_value to update according to language
        for key in ['ot_manual_filename', 'ot_excel_filename', 'incentive_filename_v2']:
            if key in st.session_state:
                del st.session_state[key]
        
    st.radio(
        "LangToggle_123", 
        options=["VN", "JP"], 
        index=0 if st.session_state.get('lang', 'VN') == 'VN' else 1,
        horizontal=True,
        key="lang_radio",
        on_change=update_lang,
        label_visibility="hidden"
    )
    
    if st.session_state.get('current_page', 'welcome') == 'welcome':
        lang_top_pos = "45px"
        st.markdown(f"""
        <style>
        /* Hide the anchor container */
        div.element-container:has(.settings-btn-anchor) {{
            display: none !important;
        }}
        
        /* Position the settings button container fixed, next to the language toggle */
        div.element-container:has(.settings-btn-anchor) + div.element-container {{
            position: fixed !important;
            top: {lang_top_pos} !important;
            right: 105px !important;
            z-index: 9999 !important;
            width: 40px !important;
            height: 40px !important;
        }}
        
        /* Ensure the inner button div takes the size */
        div.element-container:has(.settings-btn-anchor) + div.element-container > div {{
            width: 100% !important;
            height: 100% !important;
        }}

        /* Style the settings button */
        div.element-container:has(.settings-btn-anchor) + div.element-container button {{
            background-color: #00B0F0 !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
            min-height: 40px !important;
            padding: 0 !important;
            border: none !important;
            color: #ffffff !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 3px 6px rgba(0,0,0,0.1) !important;
            transition: all 0.3s ease !important;
        }}
        
        div.element-container:has(.settings-btn-anchor) + div.element-container button:hover {{
            background-color: #0099D1 !important;
            box-shadow: 0 4px 12px rgba(0, 176, 240, 0.5) !important;
            transform: translateY(-2px);
        }}
        
        div.element-container:has(.settings-btn-anchor) + div.element-container button p {{
            margin: 0 !important;
            font-size: 22px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        </style>
        <div class='settings-btn-anchor'></div>
        """, unsafe_allow_html=True)
        if st.button(":material/settings:", key="welcome_settings_btn", help=t("Cài đặt chung", "一般設定")):
            st.session_state['current_page'] = 'main'
            st.session_state['menu_selection'] = t(":material/settings: **CÀI ĐẶT CHUNG**", ":material/settings: **一般設定**")
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)


@st.dialog(t("📝 KIỂM TRA GHI CHÚ TRƯỚC KHI THOÁT", "📝 終了前のメモ確認"))
def show_sticky_note_exit_modal():
    st.markdown("""<style>
    /* Ensure blue title banner with white text */
    [role="dialog"] [data-testid="stDialogTitle"],
    [data-testid="stDialog"] [data-testid="stDialogTitle"],
    [role="dialog"] h2:first-of-type,
    [data-testid="stDialog"] h2:first-of-type {
        background-color: #00B0F0 !important;
        color: #ffffff !important;
        padding: 14px 22px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 20px !important;
        margin-top: 0px !important;
        margin-bottom: 5px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        display: block !important;
        box-shadow: 0 4px 6px rgba(0, 176, 240, 0.25) !important;
    }
    </style>""", unsafe_allow_html=True)

    note_content = st.session_state.get('sidebar_sticky_note', '').strip()
    if not note_content:
        st.info(t("Hiện tại bạn không có ghi chú nhắc việc nào chưa hoàn thành.", "現在、未完了のメモはありません。"))
        if st.button(t("Đóng", "閉じる"), use_container_width=True):
            st.rerun()
        return

    st.markdown(f"""
        <div style='
            background: #fef9c3;
            border-left: 5px solid #eab308;
            padding: 14px 18px;
            border-radius: 8px;
            margin-bottom: 18px;
            color: #713f12;
            font-size: 14.5px;
            line-height: 1.6;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        '>
            <div style='font-weight: bold; margin-bottom: 6px; color: #854d0e;'>📌 {t('Nội dung ghi chú hiện tại của bạn:', '現在のメモ内容:')}</div>
            <div style='white-space: pre-wrap; font-size: 15px; color: #1e293b;'>{note_content}</div>
        </div>
        <p style='font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 15px;'>
            {t('Bạn đã thực hiện xong công việc trong ghi chú này chưa?', 'こちらの作業は完了しましたか？')}
        </p>
    """, unsafe_allow_html=True)

    col_done, col_later, col_stay = st.columns(3, gap="small")
    with col_done:
        if st.button(t("✅ Xong rồi (Xóa & Tắt web)", "✅ 完了 (終了)"), key="btn_note_done_exit", use_container_width=True, type="primary"):
            st.session_state['sidebar_sticky_note'] = ""
            import streamlit.components.v1 as components
            components.html("""
                <script>
                    window.parent.localStorage.removeItem('ot_sidebar_sticky_note');
                    window.parent.close();
                </script>
            """, height=0)
            st.rerun()
    with col_later:
        if st.button(t("⏳ Để hôm sau (Tiếp tục tắt web)", "⏳ 明日に回す (終了)"), key="btn_note_later_exit", use_container_width=True):
            import streamlit.components.v1 as components
            components.html("""
                <script>
                    window.parent.close();
                </script>
            """, height=0)
    with col_stay:
        if st.button(t("🛑 Chưa (Ở lại trang web)", "🛑 未完了 (戻る)"), key="btn_note_stay", use_container_width=True):
            st.rerun()


@st.dialog(t("📝 GHI CHÚ NHẮC VIỆC CÁ NHÂN", "📝 クイックメモ"))
def show_sticky_note_editor_modal():
    st.markdown("""<style>
    /* Ensure blue title banner with white text */
    [role="dialog"] [data-testid="stDialogTitle"],
    [data-testid="stDialog"] [data-testid="stDialogTitle"],
    [role="dialog"] h2:first-of-type,
    [data-testid="stDialog"] h2:first-of-type {
        background-color: #00B0F0 !important;
        color: #ffffff !important;
        padding: 14px 22px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 20px !important;
        margin-top: 0px !important;
        margin-bottom: 5px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        display: block !important;
        box-shadow: 0 4px 6px rgba(0, 176, 240, 0.25) !important;
    }
    </style>""", unsafe_allow_html=True)

    st.markdown(f"<div style='font-size: 14px; color: #475569; margin-bottom: 8px;'>{t('Ghi chú của bạn được tự động ghi nhớ ngay trong phiên làm việc:', 'メモは自動保存されます:')}</div>", unsafe_allow_html=True)
    note_val = st.text_area(
        t("Nội dung ghi chú", "メモ内容"),
        value=st.session_state.get('sidebar_sticky_note', ''),
        key="txt_popup_sticky_note",
        placeholder=t("Nhập việc cần nhớ (VD: Kiểm tra OT dự án V050010)...", "メモを入力..."),
        height=140,
        label_visibility="collapsed"
    )
    st.session_state['sidebar_sticky_note'] = note_val

    col_save, col_exit = st.columns(2, gap="small")
    with col_save:
        if st.button(t("💾 Lưu & Đóng", "💾 保存して閉じる"), key="btn_save_close_note", use_container_width=True, type="primary"):
            st.rerun()
    with col_exit:
        if st.button(t("🚪 Kiểm tra trước khi tắt web", "🚪 終了前チェック"), key="btn_popup_check_exit", use_container_width=True):
            show_sticky_note_exit_modal()


if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'welcome'

if st.session_state['current_page'] == 'welcome':
    if 'last_rendered_tab' in st.session_state:
        del st.session_state['last_rendered_tab']
    render_welcome()
else:
    # Main App specific CSS
    st.markdown("""
    <style>
        .stApp {
            background: #f4f7f9 !important;
            background-color: #f4f7f9 !important;
        }
    
    [data-testid="stMain"] .stButton button,
    div[role="dialog"] .stButton button,
    div[role="dialog"] div[data-testid="stButton"] button,
    div[data-testid="stModal"] .stButton button,
    div[data-testid="stDialog"] .stButton button {
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
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button {{
                background-image: url("data:image/{ext};base64,{encoded}") !important;
                background-size: contain !important;
                background-repeat: no-repeat !important;
                background-position: center !important;
                height: 80px !important; min-height: 80px !important; width: 100% !important;
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }}
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button p {{
                visibility: hidden !important;
            }}
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button:hover {{
                transform: scale(1.05) !important;
                transition: transform 0.3s !important;
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
                    st.session_state['show_page_transition'] = True
                    if 'last_rendered_tab' in st.session_state:
                        del st.session_state['last_rendered_tab']
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
        else:
            if st.button(t("QUAY LẠI TRANG CHỦ", "ホームに戻る"), use_container_width=True):
                st.session_state['current_page'] = 'welcome'
                st.session_state['show_page_transition'] = True
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
        
        menu_title = t("MENU", "メニュー")
        st.markdown(f"<h2 style='text-align: center; width: 100%; margin-bottom: 5px; font-weight: bold; font-size: 18px !important; letter-spacing: 2px;'>{menu_title}</h2>", unsafe_allow_html=True)
        
        st.markdown("""
        <style>
            [data-testid="stSidebar"] div[role="radiogroup"] span.material-symbols-rounded,
            [data-testid="stSidebar"] div[role="radiogroup"] [data-testid="stIconMaterial"],
            [data-testid="stSidebar"] div[role="radiogroup"] [data-testid="stIcon"],
            [data-testid="stSidebar"] div[role="radiogroup"] [class*="Icon"],
            [data-testid="stSidebar"] div[role="radiogroup"] span[translate="no"] {
                font-size: 1.3em !important;
                vertical-align: middle !important;
                margin-right: 8px !important;
                color: inherit !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
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
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1) p::after {
                    content: " ▼";
                    color: #00a8e8 !important;
                }
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1):has(input:checked) p::after {
                    color: #FFFFFF !important;
                }
                /* Sub-items font size */
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2) p,
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3) p {
                    font-size: 12px !important;
                }
                /* Sub-menu items (2, 3) */
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2),
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3) {
                    margin-left: 30px;
                    padding-left: 10px;
                    border-left: 2px solid rgba(0, 0, 0, 0.1) !important;
                    border-radius: 0 8px 8px 0;
                }
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2):hover,
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3):hover {
                    border-left: 2px solid #00a8e8 !important;
                }
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2):has(input:checked),
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3):has(input:checked) {
                    border-left: none !important;
                }
                /* Main items 4, 5, 6, 7 styling */
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4),
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(5),
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(6),
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(7) {
                    margin-top: 8px;
                }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1) p::after {
                    content: " ▶";
                    color: #00a8e8 !important;
                }
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1):has(input:checked) p::after {
                    color: #FFFFFF !important;
                }
                /* Hide sub-items when collapsed */
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2),
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3),
                [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label:nth-child(2),
                [data-testid="stSidebar"][aria-expanded="false"] div[role="radiogroup"] label:nth-child(3) {
                    display: none !important;
                }
                
                /* Main items 4, 5, 6, 7 styling when collapsed */
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4),
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(5),
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(6),
                [data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(7) {
                    margin-top: 8px;
                }
            </style>
            """, unsafe_allow_html=True)
            
        # We need to map English internal keys to options to persist selection across language changes
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
            if sel == options[0]:
                st.session_state['ot_menu_expanded'] = not st.session_state.get('ot_menu_expanded', True)
                target = st.session_state.get('prev_ot_selection', options[1])
                if target == options[0] or target not in options:
                    target = options[1]
                st.session_state['menu_selection'] = target
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
        
        has_note = bool(st.session_state.get('sidebar_sticky_note', '').strip())
        btn_label = t("📝 GHI CHÚ NHẮC VIỆC 📌", "📝 クイックメモ 📌") if has_note else t("📝 GHI CHÚ NHẮC VIỆC", "📝 クイックメモ")
        st.markdown("""
        <style>
            div.element-container:has(#sticky-note-btn-anchor) + div.element-container button {
                background-color: #f8fafc !important;
                background-image: none !important;
                border: 1px dashed #0284c7 !important;
                color: #0369a1 !important;
                font-weight: 600 !important;
                font-size: 13.5px !important;
                border-radius: 8px !important;
                margin-top: 6px !important;
                padding: 6px 12px !important;
                min-height: 36px !important;
                height: 36px !important;
                box-shadow: none !important;
            }
            div.element-container:has(#sticky-note-btn-anchor) + div.element-container button p {
                visibility: visible !important;
                color: #0369a1 !important;
            }
            div.element-container:has(#sticky-note-btn-anchor) + div.element-container button:hover {
                background-color: #e0f2fe !important;
                border-color: #00a8e8 !important;
                color: #00a8e8 !important;
            }
            div.element-container:has(#sticky-note-btn-anchor) + div.element-container button:hover p {
                color: #00a8e8 !important;
            }
        </style>
        <div id="sticky-note-btn-anchor"></div>
        """, unsafe_allow_html=True)
        if st.button(btn_label, key="btn_open_sticky_note_popup", use_container_width=True):
            show_sticky_note_editor_modal()
        
        lang = st.session_state.get('lang', 'VN')
        st.markdown(f"""
    <div class='sidebar-footer-container' data-lang='{lang}'>
        <div id='sidebar-clock' style='
            text-align: center;
            margin: 0 auto 30px auto; /* Increased bottom margin from 20px to 30px to shift it up */
            width: 65%; /* Reduced width from 80% */
            background: linear-gradient(145deg, #ffffff, #f0f8ff);
            border: 1px solid rgba(0, 168, 232, 0.3);
            border-radius: 12px; /* Smaller border radius */
            padding: 8px 8px; /* Reduced padding */
            box-shadow: 0 3px 10px rgba(0, 168, 232, 0.1);
            color: #00a8e8;
            transition: all 0.3s ease;
        '>
            <div id='clock-time' style='font-family: "Courier New", monospace; font-size: 20px; font-weight: 900; letter-spacing: 1px; text-shadow: 0 1px 2px rgba(0, 168, 232, 0.2);'>00:00:00</div>
            <div id='clock-date' style='font-size: 9px; font-weight: 700; opacity: 0.8; letter-spacing: 1px; margin-top: 3px; color: #34495e;'>---</div>
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
                            if (rect.width < 200) {
                                elContainer.style.display = 'none';
                            } else {
                                elContainer.style.display = 'block';
                                elContainer.style.width = rect.width + 'px';
                                elContainer.style.left = rect.left + 'px';
                            }
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
                            const currentLang = footer.getAttribute('data-lang') || 'VN';
                            
                            let now = new Date();
                            if (currentLang === 'JP') {
                                // Convert to Japan Standard Time (JST)
                                const jstStr = new Date().toLocaleString("en-US", { timeZone: "Asia/Tokyo" });
                                now = new Date(jstStr);
                            } else {
                                // Convert to Vietnam Time (ICT)
                                const vnStr = new Date().toLocaleString("en-US", { timeZone: "Asia/Ho_Chi_Minh" });
                                now = new Date(vnStr);
                            }
                            
                            const hrs = String(now.getHours()).padStart(2, '0');
                            const mins = String(now.getMinutes()).padStart(2, '0');
                            const secs = String(now.getSeconds()).padStart(2, '0');
                            timeEl.innerText = `${hrs}:${mins}:${secs}`;
                            
                            const day = now.getDay();
                            const date = String(now.getDate()).padStart(2, '0');
                            const month = now.getMonth();
                            const year = now.getFullYear();
                            
                            if (currentLang === 'JP') {
                                const daysJP = ['日', '月', '火', '水', '木', '金', '土'];
                                dateEl.innerText = `${year}年${String(month + 1).padStart(2, '0')}月${date}日 (${daysJP[day]}) • JP`;
                            } else {
                                const days = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
                                const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
                                dateEl.innerText = `${days[day]}, ${date} ${months[month]} ${year} • VN`;
                            }
                        };
                        updateClock();
                        setInterval(updateClock, 1000);

                        // Sticky Note Exit Intent Interceptor
                        const docP = window.parent.document;
                        if (!window.parent._otStickyExitListenerInstalled) {
                            window.parent._otStickyExitListenerInstalled = true;
                            docP.addEventListener('mouseleave', (e) => {
                                if (e.clientY <= 5) {
                                    const noteText = window.parent.localStorage.getItem('ot_sidebar_sticky_note');
                                    if (noteText && noteText.trim() !== '') {
                                        let overlay = docP.getElementById('sticky-note-exit-overlay');
                                        if (!overlay) {
                                            overlay = docP.createElement('div');
                                            overlay.id = 'sticky-note-exit-overlay';
                                            overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.55);z-index:999999;display:flex;align-items:center;justify-content:center;font-family:sans-serif;';
                                            docP.body.appendChild(overlay);
                                        }
                                        const cleanNote = noteText.replace(/</g,'&lt;').replace(/>/g,'&gt;');
                                        overlay.innerHTML = `
                                            <div style="background:#fff;border-radius:10px;width:520px;max-width:90vw;box-shadow:0 15px 35px rgba(0,0,0,0.3);overflow:hidden;">
                                                <div style="background:#00B0F0;color:#fff;padding:14px 20px;font-weight:700;font-size:18px;">
                                                    📝 KIỂM TRA GHI CHÚ TRƯỚC KHI THOÁT
                                                </div>
                                                <div style="padding:20px;">
                                                    <div style="background:#fef9c3;border-left:5px solid #eab308;padding:14px;border-radius:6px;margin-bottom:15px;color:#713f12;">
                                                        <div style="font-weight:bold;margin-bottom:6px;color:#854d0e;">📌 Nội dung ghi chú hiện tại của bạn:</div>
                                                        <div style="white-space:pre-wrap;font-size:14.5px;color:#1e293b;">${cleanNote}</div>
                                                    </div>
                                                    <div style="font-size:15px;font-weight:600;color:#1e293b;margin-bottom:18px;">
                                                        Bạn đã thực hiện xong công việc trong ghi chú này chưa?
                                                    </div>
                                                    <div style="display:flex;gap:10px;flex-wrap:wrap;">
                                                        <button id="btn-note-done-exit" style="flex:1;background:#0284c7;color:#fff;border:none;padding:11px;border-radius:6px;font-weight:600;cursor:pointer;font-size:13.5px;">✅ Xong rồi (Xóa & Tắt web)</button>
                                                        <button id="btn-note-later-exit" style="flex:1;background:#f59e0b;color:#fff;border:none;padding:11px;border-radius:6px;font-weight:600;cursor:pointer;font-size:13.5px;">⏳ Để hôm sau (Tắt web)</button>
                                                        <button id="btn-note-stay-exit" style="flex:1;background:#64748b;color:#fff;border:none;padding:11px;border-radius:6px;font-weight:600;cursor:pointer;font-size:13.5px;">🛑 Chưa (Ở lại trang web)</button>
                                                    </div>
                                                </div>
                                            </div>
                                        `;
                                        overlay.style.display = 'flex';

                                        docP.getElementById('btn-note-done-exit').onclick = () => {
                                            window.parent.localStorage.removeItem('ot_sidebar_sticky_note');
                                            overlay.style.display = 'none';
                                            window.parent.close();
                                        };
                                        docP.getElementById('btn-note-later-exit').onclick = () => {
                                            overlay.style.display = 'none';
                                            window.parent.close();
                                        };
                                        docP.getElementById('btn-note-stay-exit').onclick = () => {
                                            overlay.style.display = 'none';
                                        };
                                    }
                                }
                            });
                        }
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
        
    from components.skeleton import show_skeleton_loading
    if 'last_rendered_tab' not in st.session_state:
        st.session_state['last_rendered_tab'] = menu_selection
        show_skeleton_loading(0.8)
    elif st.session_state['last_rendered_tab'] != menu_selection:
        show_skeleton_loading(0.8)
        st.session_state['last_rendered_tab'] = menu_selection
    
    if "OVERTIME" in menu_selection or "残業代計算" in menu_selection or menu_selection == t(":material/folder: **DỮ LIỆU DỰ ÁN**", ":material/folder: **プロジェクト**"):
        import importlib
        import components.ot_manual
        importlib.reload(components.ot_manual)
        components.ot_manual.render_project_data()
    elif menu_selection == t(":material/edit_document: **NHẬP HÀNG LOẠT (EXCEL)**", ":material/edit_document: **一括入力**"):
        render_ot_excel()
    elif menu_selection == t(":material/payments: **INCENTIVE**", ":material/payments: **インセンティブ**"):
        render_incentive()
    elif menu_selection == t(":material/history: **LỊCH SỬ THAO TÁC**", ":material/history: **操作履歴**"):
        render_action_history()
    elif menu_selection == t(":material/settings: **CÀI ĐẶT CHUNG**", ":material/settings: **一般設定**"):
        render_base_data()
# force reload

