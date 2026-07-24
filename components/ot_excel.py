import streamlit as st
import pandas as pd
import io
from logic.ot_calculator import calculate_ot_pay, export_ot_to_excel, get_payroll_period
from logic.action_log import save_action_log
from components.ui_utils import text_input_with_history
from logic.history import add_to_history
from logic.i18n import t

def render_ot_excel():
    from components.ot_manual import init_session_state
    init_session_state()
    col_main, col_rank = st.columns([7.5, 2.5], gap="large")
    with col_rank:
        from components.mini_leaderboard import render_mini_leaderboard
        render_mini_leaderboard("ot")
    with col_main:
        if 'ot_excel_records' not in st.session_state:
            st.session_state['ot_excel_records'] = []
        
        title = t("TÍNH TIỀN TĂNG CA HÀNG LOẠT (File Excel)", "残業代一括計算（Excelファイル）")
        st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{title}</h2>", unsafe_allow_html=True)
    
        from logic.ot_calculator import export_ot_to_excel
        import base64
        
        desc_text = t("Tải lên file Excel từ hệ thống của bạn. File cần có ít nhất các cột mang tên: <b>Ngày</b>, <b>Tên nhân viên</b>, <b>OT</b>, <b>Lý do tăng ca</b>.", "システムからExcelファイルをアップロードしてください。必要な列：<b>日付</b>、<b>社員名</b>、<b>OT</b>、<b>残業理由</b>")
        import os
        template_filename = t("Bảng tổng hợp tăng ca (OT)_Mẫu.xlsx", "残業・費用集計表(OT)_テンプレート.xlsx")
        custom_template_path = os.path.join("data", "custom_ot_template.xlsx")
        
        if os.path.exists(custom_template_path):
            with open(custom_template_path, "rb") as f:
                file_bytes = f.read()
            b64 = base64.b64encode(file_bytes).decode()
            template_filename = t("Bảng tổng hợp tăng ca (OT)_Mẫu (Tùy chỉnh).xlsx", "残業・費用集計表(OT)_カスタムテンプレート.xlsx")
            name_path = os.path.join("data", "custom_ot_template_name.txt")
            if os.path.exists(name_path):
                with open(name_path, "r", encoding="utf-8") as f:
                    template_filename = f.read().strip()
        else:
            template_buffer = export_ot_to_excel([], allow_merge=False, filename=template_filename, is_template=True)
            b64 = base64.b64encode(template_buffer.getvalue()).decode()
            
        href = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
        
        st.markdown(f"""
            <style>
            .custom-dl-btn {{
                background-color: #00B0F0 !important;
                color: white !important;
                padding: 10px 20px;
                border-radius: 8px;
                text-decoration: none !important;
                font-size: 14px;
                font-weight: 500;
                display: inline-block;
                transition: all 0.2s ease;
                white-space: nowrap;
                box-shadow: 0 4px 10px rgba(0, 176, 240, 0.3) !important;
            }}
            .custom-dl-btn:hover {{
                background-color: #0099D6 !important;
                color: white !important;
                box-shadow: 0 6px 14px rgba(0, 176, 240, 0.4) !important;
            }}
            </style>
            <div style='background-color: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); padding: 15px 20px; border: 1px solid rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; gap: 20px;'>
                <div style='font-size: 14.5px; flex: 1;'>
                    {desc_text}
                </div>
                <div>
                    <a href="{href}" download="{template_filename}" class="custom-dl-btn">{t("TẢI FILE EXCEL MẪU", "テンプレートをダウンロード")}</a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
        # Placeholder for stepper UI
        stepper_placeholder = st.empty()
    
        st.divider()

    
        from logic.employee_data import get_employees_df
        emp_df = get_employees_df()
    
        if emp_df.empty:
            st.warning(t("Vui lòng thêm ít nhất 1 nhân sự trong phần CÀI ĐẶT CHUNG trước khi import file.", "一般設定でスタッフを1名以上追加してください。"), icon=":material/warning:")
            return
        
        base = st.session_state['ot_base_data']
        st.info(t(f"Hệ thống sẽ sử dụng Mức lương cơ bản từ Danh sách Nhân sự và Ngày nghỉ/Lễ để tính toán tự động. (Số ngày chuẩn: {base.get('standard_days', 22.0)})", f"システムはスタッフリストの基本給と休日を使用して自動計算します。（標準日数: {base.get('standard_days', 22.0)}）"), icon=":material/lightbulb:")
    
        # Removed Project Overrides expander

        st.markdown("""
            <style>
                [data-testid="stFileUploader"] {
                    padding: 0 !important;
                    margin-top: -12px !important;
                    margin-bottom: 4px !important;
                }
                [data-testid="stFileUploaderDropzone"] {
                    border: 2px dashed #3498db !important;
                    border-radius: 12px !important;
                    background-color: #ffffff !important;
                    padding: 16px 20px !important;
                    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
                }
                [data-testid="stFileUploaderDropzone"]:hover {
                    background-color: #ebf5ff !important;
                    border-color: #2980b9 !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 8px 24px rgba(52, 152, 219, 0.15) !important;
                }
                /* Prevent styling the uploaded file SVGs by excluding them */
                [data-testid="stFileUploaderDropzone"] div > svg:first-child {
                    color: #3498db !important;
                    transition: all 0.3s ease !important;
                }
                @keyframes bounceCloud {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-5px); }
                }
                [data-testid="stFileUploaderDropzone"]:hover div > svg:first-child {
                    animation: bounceCloud 1.5s infinite ease-in-out !important;
                    color: #2980b9 !important;
                }

                /* Tighten uploaded data table below its label */
                div.element-container:has([data-testid="stFileUploader"]) ~ div.element-container:has([data-testid="stDataFrame"]) {
                    margin-top: -36px !important;
                    margin-bottom: 6px !important;
                }
                div.element-container:has([data-testid="stFileUploader"]) ~ div.element-container:has([data-testid="stDataFrame"]) [data-testid="stDataFrame"] {
                    padding-top: 4px !important;
                }
                div.element-container:has([data-testid="stFileUploader"]) ~ div.element-container:has([data-testid="stDataFrame"]) [data-testid="stElementToolbar"] {
                    display: none !important;
                }

                /* Tighten spacing around radio options and info alerts */
                [data-testid="stRadio"] {
                    margin-bottom: -12px !important;
                }
                div.element-container:has([data-testid="stRadio"]) + div.element-container:has([data-testid="stAlert"]) {
                    margin-top: -8px !important;
                }
            </style>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader(t("Upload File Dữ Liệu Tăng Ca", "残業データファイルをアップロード"), type=['xlsx', 'xls'])
        
        if uploaded_file is None:
            st.session_state['ot_excel_records'] = []
            st.session_state['ot_excel_downloaded'] = False
            
        if uploaded_file is not None:
            try:
                df_raw = pd.read_excel(uploaded_file, header=None)
            
                # Auto-detect header row
                header_idx = 0
                for i, row in df_raw.iterrows():
                    row_str = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
                    # check if row contains at least some of our keywords
                    if ("ngày" in row_str or "date" in row_str) and ("nhân" in row_str or "tên" in row_str or "name" in row_str) and ("ot" in row_str or "giờ" in row_str):
                        header_idx = i
                        break
                    
                df = df_raw.copy()
                if header_idx >= 0 and header_idx < len(df):
                    df.columns = df.iloc[header_idx]
                    df = df.iloc[header_idx+1:].reset_index(drop=True)
            
                # Remove any columns where the header is NaN
                df = df.loc[:, df.columns.notna()]
                
                st.markdown(f"<div style='font-size: 15px; font-weight: 500; margin-bottom: -24px;'>{t(f'Dữ liệu đã tải lên (Bắt đầu từ dòng {header_idx + 1}):', f'アップロードされたデータ (行 {header_idx + 1} から開始):')}</div>", unsafe_allow_html=True)
                st.dataframe(df, height=150)
            
                st.markdown(f"<h4 style='font-size: 18px; font-weight: 600; color: #444; margin-top: 26px; margin-bottom: 12px;'>{t('BƯỚC 1: CHẾ ĐỘ GHÉP CỘT DỮ LIỆU', 'ステップ 1: 列マッピングモード')}</h4>", unsafe_allow_html=True)
            
                col_lbl, col_rad = st.columns([0.9, 5])
                with col_lbl:
                    st.markdown(f"<div style='margin-top: 10px; font-size: 14px; color: #444; white-space: nowrap;'>{t('Tùy chọn ghép cột:', 'マッピングオプション:')}</div>", unsafe_allow_html=True)
                with col_rad:
                    mapping_mode = st.radio(
                        t("Tùy chọn ghép cột:", "マッピングオプション:"),
                        [t("Tự động nhận diện thông minh", "スマート自動認識"), t("Ghép cột thủ công", "手動マッピング")],
                        horizontal=True,
                        label_visibility="collapsed"
                    )
            
                # Multi-tier prioritized intelligent column detection
                col_map_auto = {
                    "ot": None, "ngay": None, "ten": None, "lydo": None,
                    "loai_da": None, "ma_dh": None, "ma_dh_kh": None, "ten_dh": None, "quan_ly": None
                }
                cols = df.columns

                # 1. Cột Ngày OT (P1: Ngày OT/tăng ca/làm việc/thực hiện -> P2: Ngày/Date loại trừ ngày sinh, ngày tạo...)
                for c in cols:
                    c_low = str(c).strip().lower()
                    if any(k in c_low for k in ["ngày ot", "ngày tăng ca", "ot date", "overtime date", "ngày làm việc", "ngày thực hiện"]):
                        col_map_auto["ngay"] = c
                        break
                if col_map_auto["ngay"] is None:
                    for c in cols:
                        c_low = str(c).strip().lower()
                        if ("ngày" in c_low or "date" in c_low) and not any(ex in c_low for ex in ["sinh", "tạo", "cập nhật", "vào làm", "bắt đầu", "kết thúc", "lý do"]):
                            col_map_auto["ngay"] = c
                            break

                # 2. Cột Số giờ OT (P1: Số giờ OT/Giờ OT/Tăng ca -> P2: OT/Overtime loại trừ ngày, lý do)
                for c in cols:
                    c_low = str(c).strip().lower()
                    if any(k in c_low for k in ["số giờ ot", "giờ ot", "giờ tăng ca", "ot hours", "tổng giờ ot"]):
                        col_map_auto["ot"] = c
                        break
                if col_map_auto["ot"] is None:
                    for c in cols:
                        c_low = str(c).strip().lower()
                        if ("ot" in c_low or "tăng ca" in c_low or "overtime" in c_low) and not any(ex in c_low for ex in ["lý do", "ngày", "date", "reason", "loại"]):
                            col_map_auto["ot"] = c
                            break

                # 3. Cột Tên nhân viên
                for c in cols:
                    c_low = str(c).strip().lower()
                    if any(k in c_low for k in ["tên nhân viên", "họ và tên", "người thực hiện", "staff name", "employee name"]):
                        col_map_auto["ten"] = c
                        break
                if col_map_auto["ten"] is None:
                    for c in cols:
                        c_low = str(c).strip().lower()
                        if any(k in c_low for k in ["người", "nhân viên", "nhân sự", "employee", "tên"]) and not any(ex in c_low for ex in ["mã", "code", "id", "đơn", "dự án", "quản lý", "khách", "file"]):
                            col_map_auto["ten"] = c
                            break

                # 4. Cột Lý do OT
                for c in cols:
                    c_low = str(c).strip().lower()
                    if any(k in c_low for k in ["lý do", "reason", "ghi chú", "note", "mô tả"]):
                        col_map_auto["lydo"] = c
                        break

                # 5. Các cột dự án bổ sung
                for c in cols:
                    c_low = str(c).strip().lower()
                    if col_map_auto["loai_da"] is None and "loại" in c_low and "dự án" in c_low:
                        col_map_auto["loai_da"] = c
                    elif col_map_auto["ma_dh_kh"] is None and "mã" in c_low and "đơn" in c_low and "khách" in c_low:
                        col_map_auto["ma_dh_kh"] = c
                    elif col_map_auto["ma_dh"] is None and "mã" in c_low and "đơn" in c_low and "khách" not in c_low:
                        col_map_auto["ma_dh"] = c
                    elif col_map_auto["ten_dh"] is None and "tên" in c_low and "đơn" in c_low:
                        col_map_auto["ten_dh"] = c
                    elif col_map_auto["quan_ly"] is None and ("quản lý" in c_low or "pm" in c_low):
                        col_map_auto["quan_ly"] = c
                    
                if mapping_mode == t("Tự động nhận diện thông minh", "スマート自動認識"):
                    st.info(t(
                        "Hệ thống sẽ tự động quét và nhận diện các cột dữ liệu (Ngày, Tên, Số giờ OT...). Bạn chỉ cần bấm Xử lý.",
                        "システムはデータ列を自動的にスキャンして認識します。処理をクリックするだけです。"
                    ), icon=":material/lightbulb:")
                    col_map = col_map_auto
                else:
                    col_opts = ["--- Bỏ qua ---"] + list(df.columns)
                    def get_idx(val):
                        return col_opts.index(val) if val in col_opts else 0
                    # Khối Cột Bắt Buộc
                    with st.container():
                        st.markdown(f"""
                        <div class='req-mapping-inner-marker' style='display: none;'></div>
                        <style>
                            /* Loại bỏ padding thừa của container và ép nó sát lên trên */
                            [data-testid="stVerticalBlock"]:has(> .element-container .req-mapping-inner-marker) {{
                                background-color: #ffffff !important;
                                border: 2px solid #00B0F0 !important;
                                border-radius: 10px !important;
                                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
                                padding: 2px 15px 20px 15px !important;
                                margin-bottom: 15px !important;
                            }}
                            
                            /* Giảm khoảng cách gap của chính flexbox chứa các phần tử bên trong container */
                            [data-testid="stVerticalBlock"]:has(> .element-container .req-mapping-inner-marker) > div[data-testid="stVerticalBlock"] {{
                                gap: 0.5rem !important;
                            }}
                            
                            /* Thêm dấu (*) màu đỏ vào cuối tên các cột bắt buộc bằng CSS tinh khiết */
                            [data-testid="stVerticalBlock"]:has(> .element-container .req-mapping-inner-marker) div[data-testid="stSelectbox"] label p::after {{
                                content: ' (*)';
                                color: #ef4444 !important; /* Màu đỏ */
                                font-weight: bold;
                            }}
                        </style>
                        <div style='font-size: 14.5px; font-weight: 700; color: #334155; margin-bottom: 8px; margin-top: 4px;'>{t('Các cột BẮT BUỘC', '必須列')}</div>
                        """, unsafe_allow_html=True)
                        m_col1, m_col2, m_col3 = st.columns(3)
                        with m_col1:
                            sel_ngay = st.selectbox(t(":material/calendar_month: Cột Ngày", ":material/calendar_month: 日付列"), col_opts, index=get_idx(col_map_auto["ngay"]))
                            if sel_ngay == "--- Bỏ qua ---":
                                st.markdown(f"<div style='color: #f97316; font-size: 13px; font-weight: 500; margin-top: -10px; margin-bottom: 8px;'>⚠️ {t('Vui lòng chọn', '選択してください')}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='color: #10b981; font-size: 13px; font-weight: 500; margin-top: -10px; margin-bottom: 8px;'>✅ {t('Hợp lệ', '有効')}</div>", unsafe_allow_html=True)
                        with m_col2:
                            sel_ten = st.selectbox(t(":material/person: Cột Tên", ":material/person: 名前列"), col_opts, index=get_idx(col_map_auto["ten"]))
                            if sel_ten == "--- Bỏ qua ---":
                                st.markdown(f"<div style='color: #f97316; font-size: 13px; font-weight: 500; margin-top: -10px; margin-bottom: 8px;'>⚠️ {t('Vui lòng chọn', '選択してください')}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='color: #10b981; font-size: 13px; font-weight: 500; margin-top: -10px; margin-bottom: 8px;'>✅ {t('Hợp lệ', '有効')}</div>", unsafe_allow_html=True)
                        with m_col3:
                            sel_ot = st.selectbox(t(":material/schedule: Cột Số Giờ OT", ":material/schedule: OT時間列"), col_opts, index=get_idx(col_map_auto["ot"]))
                            if sel_ot == "--- Bỏ qua ---":
                                st.markdown(f"<div style='color: #f97316; font-size: 13px; font-weight: 500; margin-top: -10px; margin-bottom: 8px;'>⚠️ {t('Vui lòng chọn', '選択してください')}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='color: #10b981; font-size: 13px; font-weight: 500; margin-top: -10px; margin-bottom: 8px;'>✅ {t('Hợp lệ', '有効')}</div>", unsafe_allow_html=True)
                    
                    # Khối Cột Tùy Chọn
                    with st.expander(t("⚙️ Cột mở rộng / Tùy chọn (Không bắt buộc)", "⚙️ 拡張列 / オプション (任意)")):
                        opt_col1, opt_col2, opt_col3 = st.columns(3)
                        with opt_col1:
                            sel_lydo = st.selectbox(t(":material/edit_note: Cột Lý do OT", ":material/edit_note: 理由列"), col_opts, index=get_idx(col_map_auto["lydo"]))
                            sel_ma_dh_kh = st.selectbox(t(":material/sell: Cột Mã ĐH khách", ":material/sell: 顧客注文番号列"), col_opts, index=get_idx(col_map_auto["ma_dh_kh"]))
                        with opt_col2:
                            sel_loai_da = st.selectbox(t(":material/category: Cột Loại dự án", ":material/category: プロジェクトタイプ列"), col_opts, index=get_idx(col_map_auto["loai_da"]))
                            sel_quan_ly = st.selectbox(t(":material/manage_accounts: Cột Người quản lý", ":material/manage_accounts: 管理者列"), col_opts, index=get_idx(col_map_auto["quan_ly"]))
                        with opt_col3:
                            sel_ma_dh = st.selectbox(t(":material/tag: Cột Mã đơn hàng", ":material/tag: 注文番号列"), col_opts, index=get_idx(col_map_auto["ma_dh"]))
                            
                    st.markdown("<hr style='margin: 10px 0 15px 0;'>", unsafe_allow_html=True)
            
                # Render Smart AI Scanner & Live Mapping Preview Card
                is_auto = (mapping_mode == t("Tự động nhận diện thông minh", "スマート自動認識"))
                preview_ngay = col_map_auto.get("ngay") if is_auto else (sel_ngay if sel_ngay != "--- Bỏ qua ---" else None)
                preview_ten = col_map_auto.get("ten") if is_auto else (sel_ten if sel_ten != "--- Bỏ qua ---" else None)
                preview_ot = col_map_auto.get("ot") if is_auto else (sel_ot if sel_ot != "--- Bỏ qua ---" else None)
                preview_lydo = col_map_auto.get("lydo") if is_auto else (sel_lydo if sel_lydo != "--- Bỏ qua ---" else None)
                
                badge_ok = f'<span style="background: #ebfbee; color: #1b7a3d; border: 1px solid #b7ebd1; padding: 2.5px 9px; border-radius: 12px; font-size: 11.5px; font-weight: 600;">{t("🟢 Khớp chính xác", "🟢 一致")}</span>'
                badge_missing = f'<span style="background: #fef3f2; color: #b91c1c; border: 1px solid #fecdd3; padding: 2.5px 9px; border-radius: 12px; font-size: 11.5px; font-weight: 600;">{t("⚠️ Cần kiểm tra", "⚠️ 要確認")}</span>'
                badge_opt = f'<span style="background: #f0f9ff; color: #0369a1; border: 1px solid #bae6fd; padding: 2.5px 9px; border-radius: 12px; font-size: 11.5px; font-weight: 600;">{t("ℹ️ Tùy chọn", "ℹ️ オプション")}</span>'
                
                card_title = t("BẢNG KIỂM TRA & ĐỐI CHIẾU CỘT DỮ LIỆU TỰ ĐỘNG", "データ列自動認識・検証プレビュー") if is_auto else t("BẢNG KIỂM TRA CẤU HÌNH GHÉP CỘT DỮ LIỆU", "列マッピング設定検証プレビュー")
                
                st.markdown(f"""
                <h4 style="font-size: 18px; font-weight: 600; color: #444; margin: 0 0 6px 0;">{t('BƯỚC 2: XỬ LÝ', 'ステップ 2: 処理')}</h4>
                <div style="background: #00b0f0; border: 1px solid rgba(255,255,255,0.3); border-radius: 12px; padding: 18px 22px; margin: 0 0 20px 0; box-shadow: 0 6px 18px rgba(0, 176, 240, 0.25);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.25); padding-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 19px;">📋</span>
                            <span style="font-weight: 700; font-size: 14.5px; color: #ffffff;">{card_title}</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.2); color: #ffffff; border: 1px solid rgba(255,255,255,0.4); padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                            ✓ {t('Dữ liệu hợp lệ:', '有効データ:')} {len(df)} {t('bản ghi', 'レコード')}
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;">
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                            <div style="font-size: 12px; color: #64748b; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;"><span class="material-symbols-rounded" style="font-size: 15px; color: #0284c7;">calendar_month</span> {t('Cột Ngày Tăng Ca', '残業日列')}</div>
                            <div style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{preview_ngay or t('Chưa nhận diện', '未検出')}</div>
                            <div>{badge_ok if preview_ngay else badge_missing}</div>
                        </div>
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                            <div style="font-size: 12px; color: #64748b; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;"><span class="material-symbols-rounded" style="font-size: 15px; color: #0284c7;">person</span> {t('Cột Tên Nhân Viên', 'スタッフ名列')}</div>
                            <div style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{preview_ten or t('Chưa nhận diện', '未検出')}</div>
                            <div>{badge_ok if preview_ten else badge_missing}</div>
                        </div>
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                            <div style="font-size: 12px; color: #64748b; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;"><span class="material-symbols-rounded" style="font-size: 15px; color: #0284c7;">schedule</span> {t('Cột Số Giờ OT', '残業時間列')}</div>
                            <div style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{preview_ot or t('Chưa nhận diện', '未検出')}</div>
                            <div>{badge_ok if preview_ot else badge_missing}</div>
                        </div>
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
                            <div style="font-size: 12px; color: #64748b; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;"><span class="material-symbols-rounded" style="font-size: 15px; color: #0284c7;">edit_note</span> {t('Cột Lý Do OT', '残業理由列')}</div>
                            <div style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{preview_lydo or t('Mặc định (Trống)', 'デフォルト/空')}</div>
                            <div>{badge_ok if preview_lydo else badge_opt}</div>
                        </div>
                    </div>
                    <div style="font-size: 12.5px; color: #ffffff; margin-top: 14px; display: flex; align-items: center; gap: 6px;">
                        <span>💡</span>
                        <span>{t('Hệ thống đã đối chiếu dữ liệu thành công. Vui lòng kiểm tra thông tin cột phía trên và nhấn nút <b>Xử Lý Dữ Liệu Tăng Ca</b> bên dưới.', '列認識をご確認の上、下の <b>データ処理</b> ボタンを押して計算を開始してください。')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
                if st.button(t("Xử Lý Dữ Liệu Tăng Ca", "データ処理"), type="primary"):
                    st.session_state['ot_excel_downloaded'] = False
                    if mapping_mode == t("Ghép cột thủ công", "手動マッピング"):
                        # Update map based on user selection
                        col_map = col_map_auto.copy()
                        col_map["ngay"] = sel_ngay if sel_ngay != "--- Bỏ qua ---" else None
                        col_map["ten"] = sel_ten if sel_ten != "--- Bỏ qua ---" else None
                        col_map["ot"] = sel_ot if sel_ot != "--- Bỏ qua ---" else None
                        col_map["lydo"] = sel_lydo if sel_lydo != "--- Bỏ qua ---" else None
                        col_map["loai_da"] = sel_loai_da if sel_loai_da != "--- Bỏ qua ---" else None
                        col_map["ma_dh"] = sel_ma_dh if sel_ma_dh != "--- Bỏ qua ---" else None
                        col_map["ma_dh_kh"] = sel_ma_dh_kh if sel_ma_dh_kh != "--- Bỏ qua ---" else None
                        col_map["quan_ly"] = sel_quan_ly if sel_quan_ly != "--- Bỏ qua ---" else None
                    else:
                        st.success(t(
                            f"Đã tự động nhận diện thành công: Ngày -> `{col_map['ngay']}`, Tên -> `{col_map['ten']}`, OT -> `{col_map['ot']}`, Lý do -> `{col_map['lydo']}`",
                            f"自動認識成功：日付 -> `{col_map['ngay']}`、名前 -> `{col_map['ten']}`、OT -> `{col_map['ot']}`、理由 -> `{col_map['lydo']}`"
                        ), icon=":material/check_circle:")
                
                
                    # Prepare holidays list
                    holidays_list = []
                    if 'holidays_df' in base and isinstance(base['holidays_df'], pd.DataFrame) and len(base['holidays_df']) > 0:
                        holidays_list = pd.to_datetime(base['holidays_df']["Ngày nghỉ"], errors="coerce").dropna().tolist()
                
                    # Handle merged cells by forward-filling Name and Project columns
                    cols_to_ffill = [
                        col_map["ten"], col_map["loai_da"], col_map["ma_dh"], 
                        col_map["ma_dh_kh"], col_map["ten_dh"], col_map["quan_ly"]
                    ]
                    for c in cols_to_ffill:
                        if c and c in df.columns:
                            df[c] = df[c].ffill()
                
                    results = []
                    from logic.ot_calculator import breakdown_ot_hours
                    from logic.project_data import get_projects_df
                    projects_df = get_projects_df()
                
                    for index, row in df.iterrows():
                        ot_val = row.get(col_map["ot"], 0) if col_map["ot"] else 0
                    
                        if pd.isna(ot_val) or str(ot_val).strip() == "":
                            continue
                        
                        try:
                            ot_hours = float(ot_val)
                        except (ValueError, TypeError):
                            continue
                        
                        if pd.isna(ot_hours) or ot_hours <= 0:
                            continue
                        
                        # Parse date
                        ot_date_val = row.get(col_map["ngay"], "") if col_map["ngay"] else ""
                        if pd.isna(ot_date_val) or str(ot_date_val).strip() == "":
                            continue
                        
                        try:
                            date_obj = pd.to_datetime(ot_date_val, dayfirst=True).date()
                        except:
                            continue
                        
                        # Format date to dd/mm/yyyy to match user's expected output
                        ot_date_str = date_obj.strftime("%d/%m/%Y")
                    
                        # Split buckets
                        buckets = breakdown_ot_hours(date_obj, ot_hours, holidays_list)
                    
                        emp_name = str(row.get(col_map["ten"], "")) if col_map["ten"] and pd.notna(row.get(col_map["ten"])) else ""
                        emp_gross = 0.0
                        
                        if not emp_name:
                            continue
                            
                        emp_name_clean = str(emp_name).strip().lower()
                        emp_row = emp_df[emp_df['Tên NV'].astype(str).str.strip().str.lower() == emp_name_clean]
                      
                        if emp_row.empty and len(emp_name_clean) > 1:
                            if " " not in emp_name_clean:
                                matches = emp_df[emp_df['Tên NV'].astype(str).str.strip().str.lower().str.endswith(f" {emp_name_clean}")]
                                if not matches.empty:
                                    emp_row = matches.head(1)
                            else:
                                matches = emp_df[emp_df['Tên NV'].astype(str).str.lower().str.contains(emp_name_clean, na=False)]
                                if not matches.empty:
                                    starts = matches[matches['Tên NV'].astype(str).str.lower().str.startswith(emp_name_clean)]
                                    if not starts.empty:
                                        emp_row = starts.head(1)
                                    else:
                                        emp_row = matches.head(1)
                          
                        if not emp_row.empty:
                            emp_name = str(emp_row.iloc[0]['Tên NV'])
                            raw_gross = str(emp_row.iloc[0].get('Lương Gross', '0')).replace(',', '')
                            try:
                                emp_gross = float(raw_gross)
                            except ValueError:
                                emp_gross = 0.0
                        else:
                            continue
                    
                        manager_name = str(row.get(col_map["quan_ly"], "")) if col_map["quan_ly"] and pd.notna(row.get(col_map["quan_ly"])) else ""
                        if manager_name and not projects_df.empty:
                            manager_name_clean = str(manager_name).strip().lower()
                            pm_row = projects_df[projects_df['Tên PM'].astype(str).str.strip().str.lower() == manager_name_clean]
                            if pm_row.empty:
                                import re
                                parts = [p.strip() for p in re.split(r'[/,&]+', manager_name_clean) if p.strip()]
                                if parts:
                                    def match_all_parts(pm_val):
                                        pm_val_clean = str(pm_val).lower()
                                        return all(part in pm_val_clean for part in parts)
                                    pm_matches = projects_df[projects_df['Tên PM'].apply(match_all_parts)]
                                    if not pm_matches.empty:
                                        best_match = min(
                                            pm_matches['Tên PM'].tolist(),
                                            key=lambda x: abs(len([p for p in re.split(r'[/,&]+', str(x).lower()) if p.strip()]) - len(parts))
                                        )
                                        pm_row = projects_df[projects_df['Tên PM'] == best_match]
                            if not pm_row.empty:
                                manager_name = str(pm_row.iloc[0]['Tên PM']) if isinstance(pm_row, pd.DataFrame) else str(pm_row.iloc[0])
                    
                        std_days = float(base.get('standard_days', 22.0))
                    
                        entry = {
                            "payment_period": get_payroll_period(date_obj),
                            "project_type": str(row.get(col_map["loai_da"], "")) if col_map["loai_da"] and pd.notna(row.get(col_map["loai_da"])) else "",
                            "client_order_id": str(row.get(col_map["ma_dh_kh"], "")) if col_map["ma_dh_kh"] and pd.notna(row.get(col_map["ma_dh_kh"])) else "",
                            "order_id": str(row.get(col_map["ma_dh"], "")) if col_map["ma_dh"] and pd.notna(row.get(col_map["ma_dh"])) else "",
                            "order_name": str(row.get(col_map["ten_dh"], "")) if col_map["ten_dh"] and pd.notna(row.get(col_map["ten_dh"])) else "",
                            "manager_name": manager_name,
                            "employee_name": emp_name,
                            "ot_reason": str(row.get(col_map["lydo"], "")) if col_map["lydo"] and pd.notna(row.get(col_map["lydo"])) else "",
                            "ot_date": ot_date_str,
                            "ot_hours": ot_hours,
                            "hourly_rate": int(emp_gross / std_days / 8) if std_days > 0 else 0
                        }
                    
                        # Look up project info
                        matched_project = {}
                        order_n = entry["order_name"]
                        order_i = entry["order_id"]
                    
                        if not projects_df.empty:
                            # Try to match by order_id or order_name
                            for _, p in projects_df.iterrows():
                                if (order_i and str(p.get("Mã đơn hàng", "")) == order_i) or \
                                   (order_n and str(p.get("Tên dự án", "")) == order_n):
                                    matched_project = {
                                        "project_type": str(p.get("Loại dự án", "")),
                                        "client_order_id": str(p.get("Mã KH", "")),
                                        "order_id": str(p.get("Mã đơn hàng", "")),
                                        "order_name": str(p.get("Tên dự án", "")),
                                        "manager_name": str(p.get("Tên PM", ""))
                                    }
                                    break
                    
                        # Override with master data project info if the Excel file didn't provide it
                        entry["project_type"] = entry["project_type"] or matched_project.get("project_type", "")
                        entry["client_order_id"] = entry["client_order_id"] or matched_project.get("client_order_id", "")
                        entry["order_id"] = entry["order_id"] or matched_project.get("order_id", "")
                        entry["order_name"] = entry["order_name"] or matched_project.get("order_name", "")
                        entry["manager_name"] = entry["manager_name"] or matched_project.get("manager_name", "")
                    
                        has_buckets = False
                        for bucket_name, b_hours in buckets.items():
                            if b_hours > 0:
                                has_buckets = True
                                multiplier = float(bucket_name)
                                calc = calculate_ot_pay(emp_gross, std_days, b_hours, multiplier)
                                k_name = f"{int(multiplier)}%" if float(multiplier).is_integer() else f"{multiplier}%"
                                entry[k_name] = int(calc["ot_pay"])
                            
                        if has_buckets:
                            results.append(entry)
                
                    if len(results) > 0:
                        st.session_state['ot_excel_records'] = results
                    else:
                        st.warning(t("Không tìm thấy dữ liệu OT hợp lệ (giờ OT > 0 và Ngày đúng định dạng) để xử lý.", "有効なOTデータが見つかりませんでした（OT時間 > 0 かつ正しい日付形式）。"))
                        st.session_state['ot_excel_records'] = []
                
            except Exception as e:
                st.error(f"{t('Đã xảy ra lỗi khi đọc/xử lý file', 'ファイル読み込み・処理エラー')}: {e}")
            
        # Show Data Editor if there are records
        if st.session_state.get('ot_excel_records') and len(st.session_state['ot_excel_records']) > 0:
            st.markdown("<hr style='margin: 14px 0 10px 0;'>", unsafe_allow_html=True)
            col_title, col_clear = st.columns([7.5, 2.5])
            with col_title:
                st.markdown(
                    f"<h3 style='font-size: 20px; font-weight: 600; margin: 0 0 6px 0;'>{t('BẢNG DỮ LIỆU KẾT QUẢ', '処理結果データ')}</h3>"
                    f"<div style='font-size: 13.5px; color: #64748b; margin-bottom: 18px; line-height: 1.5;'>{t('Bảng kết quả đã được tô màu theo hệ số để bạn dễ dàng kiểm tra. Nếu cần sửa dữ liệu, hãy mở bảng Sửa Dữ Liệu bên dưới.', '係数ごとに色分けされた結果表です。データを修正する場合は下の「データ編集」を開いてください。')}</div>",
                    unsafe_allow_html=True
                )
            with col_clear:
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                if st.button(":material/delete: " + t("Xóa kết quả này", "結果をクリア"), use_container_width=True):
                    st.session_state['ot_excel_records'] = []
                    st.rerun()
        
            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
            # Style the dataframe
            df_display = pd.DataFrame(st.session_state['ot_excel_records'])
        
            rename_dict = {
                "payment_period": t("Kỳ Tính Lương", "給与計算期間"),
                "project_type": t("Loại Dự Án", "プロジェクト種別"),
                "order_id": t("Mã Đơn Hàng", "注文番号"),
                "client_order_id": t("Mã ĐH Khách", "客先注文番号"),
                "order_name": t("Tên Đơn Hàng", "注文名"),
                "manager_name": t("Tên Quản Lý", "PM名"),
                "employee_name": t("Người Thực Hiện", "社員名"),
                "ot_reason": t("Lý Do OT", "残業理由"),
                "ot_date": t("Ngày OT", "残業日"),
                "ot_hours": t("Tổng Giờ OT", "総残業時間"),
                "hourly_rate": t("Số Lương/H (VND)", "時給"),
            }
            for col in df_display.columns:
                if col.endswith("%"):
                    rename_dict[col] = f"{t('Tiền', '金額')} {col}"
                
            df_display = df_display.rename(columns=rename_dict)
        
            def color_ot_cols(s):
                name = str(s.name)
                if "150" in name:
                    return ['background-color: #e8f5e9; color: #2e7d32; font-weight: bold; text-align: right;'] * len(s)
                elif "200" in name:
                    return ['background-color: #fff3e0; color: #ef6c00; font-weight: bold; text-align: right;'] * len(s)
                elif "270" in name:
                    return ['background-color: #ffe0b2; color: #e65100; font-weight: bold; text-align: right;'] * len(s)
                elif "300" in name or "400" in name:
                    return ['background-color: #ffebee; color: #c62828; font-weight: bold; text-align: right;'] * len(s)
                return [''] * len(s)
            
            format_dict = {}
            for col in df_display.columns:
                if t("Lương/H", "時給") in col or t("Tiền", "金額") in col:
                    format_dict[col] = "{:,.0f}"
                elif t("Giờ OT", "残業時間") in col:
                    format_dict[col] = "{:,.2f}"
                
            styled_df = df_display.style.apply(color_ot_cols, axis=0).format(format_dict, na_rep="")
            st.dataframe(styled_df, use_container_width=True)
        
            with st.expander("✏️ " + t("Sửa dữ liệu thủ công (Nếu cần)", "手動でデータ編集（必要に応じて）")):
                from components.ui_utils import make_expander_blue
                make_expander_blue()
                col_cfg = {
                    "payment_period": t("Kỳ Tính Lương", "給与計算期間"),
                    "project_type": t("Loại Dự Án", "プロジェクト種別"),
                    "order_id": t("Mã Đơn Hàng", "注文番号"),
                    "client_order_id": t("Mã ĐH Khách", "客先注文番号"),
                    "order_name": t("Tên Đơn Hàng", "注文名"),
                    "manager_name": t("Tên Quản Lý", "PM名"),
                    "employee_name": t("Người Thực Hiện", "社員名"),
                    "ot_reason": t("Lý Do OT", "残業理由"),
                    "ot_date": t("Ngày OT", "残業日"),
                    "ot_hours": t("Tổng Giờ OT", "総残業時間"),
                    "hourly_rate": st.column_config.TextColumn(t("Số Lương/H (VND)", "時給")),
                }
            
                for record in st.session_state['ot_excel_records']:
                    for key in record.keys():
                        if key.endswith("%") and key not in col_cfg:
                            col_cfg[key] = st.column_config.TextColumn(f"{t('Tiền', '金額')} {key}")
                        
                import copy
                import math
                display_records = copy.deepcopy(st.session_state['ot_excel_records'])
                for r in display_records:
                    if 'hourly_rate' in r and pd.notna(r['hourly_rate']) and str(r['hourly_rate']).strip() != '':
                        try:
                            r['hourly_rate'] = f"{int(r['hourly_rate']):,}"
                        except ValueError:
                            pass
                    for key in r.keys():
                        if key.endswith('%') and pd.notna(r[key]) and str(r[key]).strip() != '':
                            try:
                                r[key] = f"{int(r[key]):,}"
                            except ValueError:
                                pass

                df_display_records = pd.DataFrame(display_records)

                edited_df_raw = st.data_editor(
                    df_display_records,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="ot_excel_records_editor_v2",
                    column_config=col_cfg
                )
                edited_records = edited_df_raw.to_dict('records')
                # Clean commas and save back
                import math
                for r in edited_records:
                    if 'hourly_rate' in r and isinstance(r['hourly_rate'], str):
                        r['hourly_rate'] = int(r['hourly_rate'].replace(',', ''))
                    for key in r.keys():
                        if key.endswith('%') and isinstance(r[key], str):
                            r[key] = int(r[key].replace(',', ''))
                        
                st.session_state['ot_excel_records'] = edited_records
        
            st.markdown("<hr class='custom-hr-divider' style='margin: 6px 0 10px 0 !important; border: 0; border-top: 1.5px solid #94a3b8 !important;'>", unsafe_allow_html=True)
            st.caption(t("📌 **Lưu ý:** Bạn cần bấm nút **Tải File Excel Kết Quả** thì Bảng xếp hạng mới được cập nhật.", "📌 **注意:** ランキングを更新するには「結果ファイルダウンロード」ボタンを押してください。"))
            c_name, c_btn = st.columns([6, 4])
            with c_name:
                default_name = t("Bảng tổng hợp tăng ca (OT).xlsx", "残業集計表_OT.xlsx")
                export_name = st.text_input(
                    "📝 " + t("Tên file tải xuống:", "ダウンロードファイル名:"), 
                    value=default_name, 
                    key=f"ot_excel_filename_{st.session_state.get('lang', 'VN')}",
                    help=t("Nhấn Enter (↵) sau khi gõ xong để hoàn tất việc đổi tên.", "ファイル名を変更した後、Enter（↵）キーを押して確定してください。")
                )
                if not export_name.endswith(".xlsx"):
                    export_name += ".xlsx"
                
            # Extract general period for excel export
            try:
                fd = st.session_state['ot_base_data'].get('from_date', '')
                td = st.session_state['ot_base_data'].get('to_date', '')
                if fd and td:
                    import datetime
                    fd_val = datetime.datetime.strptime(fd, "%Y-%m-%d")
                    td_val = datetime.datetime.strptime(td, "%Y-%m-%d")
                    gp = f"{fd_val.strftime('%d/%m/%Y')} - {td_val.strftime('%d/%m/%Y')}"
                else:
                    gp = ""
            except Exception:
                gp = ""

            excel_buffer = export_ot_to_excel(st.session_state['ot_excel_records'], allow_merge=True, filename=export_name, general_period=gp)
        
            with c_btn:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            
                def download_and_save_ot_excel(*args):
                    save_action_log(*args)
                    from logic.history_records import add_records
                    add_records("ot", st.session_state['ot_excel_records'])
                    st.session_state['ot_excel_downloaded'] = True
                
                st.download_button(
                    label=t("TẢI FILE EXCEL KẾT QUẢ", "結果ファイルダウンロード"),
                    data=excel_buffer,
                    file_name=export_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                    on_click=download_and_save_ot_excel,
                    args=("OT Excel (Hàng Loạt)", "残業代一括計算 (Excel)", f"Tính OT hàng loạt ({len(st.session_state['ot_excel_records'])} bản ghi)", f"残業一括計算 ({len(st.session_state['ot_excel_records'])} レコード)", excel_buffer, export_name)
                )
        
        # Update stepper UI placeholder at the end
        current_step = 1
        if uploaded_file is not None:
            current_step = 2
        if st.session_state.get('ot_excel_records') and len(st.session_state['ot_excel_records']) > 0:
            current_step = 3
        if st.session_state.get('ot_excel_downloaded'):
            current_step = 4
        
        stepper_placeholder.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0 20px 0; background: #ffffff; padding: 15px 20px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <div style="text-align: center; flex: 1; opacity: {'1' if current_step >= 1 else '0.4'};">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: {'#00B0F0' if current_step >= 1 else '#ccc'}; color: white; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem; margin-bottom: 3px;">1</div>
                    <div style="font-size: 0.75rem; font-weight: bold; color: {'#00B0F0' if current_step >= 1 else '#777'};">{t("Tải File", "ファイルUP")}</div>
                </div>
                <div style="flex: 0.5; height: 2px; background: {'rgba(0, 176, 240, 0.5)' if current_step >= 2 else '#eaeaea'};"></div>
                <div style="text-align: center; flex: 1; opacity: {'1' if current_step >= 2 else '0.4'};">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: {'#00B0F0' if current_step >= 2 else '#ccc'}; color: white; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem; margin-bottom: 3px;">2</div>
                    <div style="font-size: 0.75rem; font-weight: bold; color: {'#00B0F0' if current_step >= 2 else '#777'};">{t("Xử Lý Dữ Liệu", "データ処理")}</div>
                </div>
                <div style="flex: 0.5; height: 2px; background: {'rgba(0, 176, 240, 0.5)' if current_step >= 3 else '#eaeaea'};"></div>
                <div style="text-align: center; flex: 1; opacity: {'1' if current_step >= 3 else '0.4'};">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: {'#00B0F0' if current_step >= 3 else '#ccc'}; color: white; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem; margin-bottom: 3px;">3</div>
                    <div style="font-size: 0.75rem; font-weight: bold; color: {'#00B0F0' if current_step >= 3 else '#777'};">{t("Kiểm Tra Bảng", "データ確認")}</div>
                </div>
                <div style="flex: 0.5; height: 2px; background: {'rgba(0, 176, 240, 0.5)' if current_step >= 4 else '#eaeaea'};"></div>
                <div style="text-align: center; flex: 1; opacity: {'1' if current_step >= 4 else '0.4'};">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: {'#00B0F0' if current_step >= 4 else '#ccc'}; color: white; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem; margin-bottom: 3px;">4</div>
                    <div style="font-size: 0.75rem; font-weight: bold; color: {'#00B0F0' if current_step >= 4 else '#777'};">{t("Xuất Báo Cáo", "出力")}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
