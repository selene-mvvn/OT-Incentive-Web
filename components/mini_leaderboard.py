import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from logic.history_records import get_records, save_all_records
from logic.i18n import t

@st.dialog(t("✏️ SỬA DỮ LIỆU NHANH", "✏️ 簡易データ編集"), width="large")
def show_mini_edit_dialog(data_type, df):
    st.markdown(f"""
        <style>
            div[role="dialog"] {{
                transform: translateY(8vh);
            }}
            [role="dialog"] [data-testid="stDialogHeader"],
            [data-testid="stDialog"] [data-testid="stDialogHeader"] {{
                padding-bottom: 0px !important;
                margin-bottom: 0px !important;
            }}
            [role="dialog"] [data-testid="stDialogTitle"],
            [data-testid="stDialog"] [data-testid="stDialogTitle"],
            [role="dialog"] h2:first-of-type,
            [data-testid="stDialog"] h2:first-of-type {{
                background-color: #00B0F0 !important;
                color: #ffffff !important;
                padding: 14px 22px !important;
                border-radius: 8px !important;
                font-weight: 700 !important;
                font-size: 22px !important;
                margin-top: 0px !important;
                margin-bottom: 0px !important;
                width: 100% !important;
                box-sizing: border-box !important;
                display: block !important;
                box-shadow: 0 4px 6px rgba(0, 176, 240, 0.25) !important;
            }}
            [role="dialog"] [data-testid="stDialogTitle"] *,
            [data-testid="stDialog"] [data-testid="stDialogTitle"] *,
            [role="dialog"] h2:first-of-type *,
            [data-testid="stDialog"] h2:first-of-type * {{
                color: #ffffff !important;
            }}
            div[role="dialog"] .stButton button[kind="secondary"],
            div[role="dialog"] div[data-testid="stButton"] button[kind="secondary"],
            div[data-testid="stModal"] .stButton button[kind="secondary"],
            div[data-testid="stDialog"] .stButton button[kind="secondary"] {{
                border-radius: 30px !important;
                font-weight: bold !important;
                text-transform: uppercase !important;
                padding: 10px 30px !important;
                font-size: 13px !important;
                border: 2px solid #00B0F0 !important;
                background-color: #ffffff !important;
                color: #00B0F0 !important;
                transition: all 0.3s ease !important;
            }}
            div[role="dialog"] .stButton button[kind="secondary"]:hover,
            div[role="dialog"] div[data-testid="stButton"] button[kind="secondary"]:hover,
            div[data-testid="stModal"] .stButton button[kind="secondary"]:hover,
            div[data-testid="stDialog"] .stButton button[kind="secondary"]:hover {{
                background-color: #00B0F0 !important;
                color: #ffffff !important;
                border-color: #00B0F0 !important;
                box-shadow: 0 5px 15px rgba(0, 176, 240, 0.3) !important;
                transform: translateY(-2px) !important;
            }}
            div[role="dialog"] .stButton button[kind="primary"],
            div[role="dialog"] div[data-testid="stButton"] button[kind="primary"],
            div[data-testid="stModal"] .stButton button[kind="primary"],
            div[data-testid="stDialog"] .stButton button[kind="primary"] {{
                border-radius: 30px !important;
                font-weight: bold !important;
                text-transform: uppercase !important;
                padding: 10px 30px !important;
                font-size: 13px !important;
                background: linear-gradient(135deg, #00B0F0 0%, #007bff 100%) !important;
                color: #ffffff !important;
                border: none !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 6px rgba(0, 176, 240, 0.3) !important;
            }}
            div[role="dialog"] .stButton button[kind="primary"]:hover,
            div[role="dialog"] div[data-testid="stButton"] button[kind="primary"]:hover,
            div[data-testid="stModal"] .stButton button[kind="primary"]:hover,
            div[data-testid="stDialog"] .stButton button[kind="primary"]:hover {{
                box-shadow: 0 6px 12px rgba(0, 176, 240, 0.4) !important;
                transform: translateY(-2px) !important;
                background: linear-gradient(135deg, #007bff 0%, #00B0F0 100%) !important;
            }}
            div[role="dialog"] .stButton button p,
            div[role="dialog"] div[data-testid="stButton"] button p,
            [role="dialog"] [data-testid="stDialogBody"] > div > div:first-child,
            [data-testid="stDialog"] [data-testid="stDialogBody"] > div > div:first-child {{
                margin-top: -10px !important;
                padding-top: 0px !important;
            }}
            div[data-testid="stModal"] .stButton button p,
            div[data-testid="stDialog"] .stButton button p {{
                color: inherit !important;
                font-weight: bold !important;
            }}

            .edit-info {{
                background-color: #e0f2fe;
                color: #0369a1;
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                font-size: 14px;
                font-weight: 500;
            }}
        </style>
        <div class="edit-info">
            <span class="material-symbols-rounded" style="margin-right: 8px; font-size: 20px;">info</span>
            {t("Chỉnh sửa trực tiếp trên bảng và nhấn Lưu thay đổi.", "表上で直接編集し、変更を保存ボタンを押してください。")}
        </div>
    """, unsafe_allow_html=True)
    
    date_col = 'ot_date' if data_type == 'ot' else 'date'
    if date_col in df.columns:
        df['date_obj_edit'] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
        years = sorted(df['date_obj_edit'].dt.year.dropna().astype(int).unique().tolist(), reverse=True)
    else:
        years = []
    
    c_y, c_m, c_s = st.columns([1.5, 1.5, 2.5], vertical_alignment="bottom")
    
    def fmt_year(y):
        return f"{y}年" if st.session_state.get('lang', 'VN') == 'JP' and str(y).isdigit() else str(y)
        
    def fmt_month(m):
        return f"{m}月" if st.session_state.get('lang', 'VN') == 'JP' and str(m).isdigit() else (f"Tháng {m}" if str(m).isdigit() else str(m))

    with c_y:
        year_options = [t("Tất cả", "すべて")] + years
        sel_year = st.selectbox(t(":material/calendar_month: Chọn năm", ":material/calendar_month: 年を選択"), options=year_options, format_func=fmt_year, key=f"dialog_year_{data_type}")
    
    if sel_year not in ["Tất cả", "すべて"]:
        edit_df = df[df['date_obj_edit'].dt.year == sel_year].copy()
    else:
        edit_df = df.copy()
        
    if date_col in df.columns:
        months = sorted(edit_df['date_obj_edit'].dt.month.dropna().astype(int).unique().tolist())
    else:
        months = []
        
    with c_m:
        month_options = [t("Tất cả", "すべて")] + months
        sel_month = st.selectbox(t(":material/calendar_today: Chọn tháng", ":material/calendar_today: 月を選択"), options=month_options, format_func=fmt_month, key=f"dialog_month_{data_type}")
        
    if sel_month not in ["Tất cả", "すべて"]:
        edit_df = edit_df[edit_df['date_obj_edit'].dt.month == sel_month].copy()
        
    with c_s:
        search_term = st.text_input(t(":material/search: Tìm kiếm nhanh", ":material/search: クイック検索"), key=f"dialog_search_{data_type}")
        
    if search_term:
        mask = edit_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)
        edit_df = edit_df[mask].copy()

    if data_type == "ot":
        col_order = ["payment_period", "ot_date", "employee_name", "manager_name", "project_type", "order_name", "order_id", "client_order_id", "ot_reason", "ot_hours", "hourly_rate"] + [c for c in df.columns if str(c).endswith("%")]
        col_order = [c for c in col_order if c in df.columns] + [c for c in df.columns if c not in col_order]
        col_cfg = {
            "ot_date": st.column_config.TextColumn(t("Ngày OT", "残業日")),
            "employee_name": st.column_config.TextColumn(t("Nhân sự", "担当者")),
            "ot_hours": st.column_config.NumberColumn(t("Giờ OT", "残業時間")),
            "ot_reason": st.column_config.TextColumn(t("Lý do", "残業理由")),
            "manager_name": st.column_config.TextColumn(t("Quản lý", "PM")),
            "project_type": st.column_config.TextColumn(t("Loại dự án", "プロジェクト種別")),
            "order_id": st.column_config.TextColumn(t("Mã dự án", "注文番号")),
            "order_name": st.column_config.TextColumn(t("Tên dự án", "注文名")),
            "client_order_id": st.column_config.TextColumn(t("Mã đơn khách", "客先注文番号")),
            "hourly_rate": st.column_config.NumberColumn(t("Lương/h", "時給"), format="%,.0f"),
            "payment_period": st.column_config.TextColumn(t("Kỳ thanh toán", "支払期間")),
            "standard_days": st.column_config.NumberColumn(t("Số ngày chuẩn", "基準日数")),
            "gross_salary": st.column_config.NumberColumn(t("Lương Gross", "総支給額"))
        }
        for c in df.columns:
            if str(c).endswith("%"):
                col_cfg[c] = st.column_config.NumberColumn(c, format="%,.0f")
    else:
        col_order = ["date", "employee_name", "project_name", "target_hours", "actual_hours", "unit_price", "company_charge", "profit", "standard_incentive", "final_incentive", "notes"]
        col_order = [c for c in col_order if c in df.columns] + [c for c in df.columns if c not in col_order]
        col_cfg = {
            "date": st.column_config.TextColumn(t("Ngày ghi nhận", "記録日")),
            "employee_name": st.column_config.TextColumn(t("Nhân sự", "担当者")),
            "project_name": st.column_config.TextColumn(t("Tên dự án", "案件名")),
            "target_hours": st.column_config.NumberColumn(t("Giờ công KH", "目標工数")),
            "actual_hours": st.column_config.NumberColumn(t("Giờ công TT", "実工数")),
            "unit_price": st.column_config.NumberColumn(t("Đơn giá", "単価"), format="%,.0f"),
            "company_charge": st.column_config.NumberColumn(t("Company Charge", "会社運用ﾁｬｰｼﾞ"), format="%,.0f"),
            "profit": st.column_config.NumberColumn(t("Lợi nhuận", "利益"), format="%,.0f"),
            "standard_incentive": st.column_config.NumberColumn(t("Incentive TC", "基準金額"), format="%,.0f"),
            "final_incentive": st.column_config.NumberColumn(t("Nhận được", "受取額"), format="%,.0f"),
            "notes": st.column_config.TextColumn(t("Ghi chú", "備考"))
        }
        
    col_cfg["date_obj"] = None
    col_cfg["date_obj_edit"] = None

    preview_key = f"dialog_preview_{data_type}"
    staged_key = f"dialog_staged_{data_type}"

    if st.session_state.get(preview_key, False):
        st.markdown(f"### {t(':material/warning: Xem trước thay đổi', ':material/warning: 変更のプレビュー')}")
        staged_df = st.session_state[staged_key]
        
        diff_count = 0
        added_idx = staged_df.index.difference(edit_df.index)
        deleted_idx = edit_df.index.difference(staged_df.index)
        added = len(added_idx)
        deleted = len(deleted_idx)
        
        def format_row_name(row_df, idx):
            row_parts = []
            if 'ot_date' in row_df.columns: row_parts.append(str(row_df.loc[idx, 'ot_date']))
            elif 'date' in row_df.columns: row_parts.append(str(row_df.loc[idx, 'date']))
            if 'employee_name' in row_df.columns: row_parts.append(str(row_df.loc[idx, 'employee_name']))
            if 'order_id' in row_df.columns and 'order_name' in row_df.columns:
                row_parts.append(f"{row_df.loc[idx, 'order_id']} ({row_df.loc[idx, 'order_name']})")
            elif 'project_name' in row_df.columns:
                row_parts.append(str(row_df.loc[idx, 'project_name']))
            if 'ot_hours' in row_df.columns:
                row_parts.append(f"{t('Giờ OT', '残業時間')}: {row_df.loc[idx, 'ot_hours']}")
            elif 'actual_hours' in row_df.columns:
                row_parts.append(f"{t('Giờ TT', '実働時間')}: {row_df.loc[idx, 'actual_hours']}")
            return " | ".join(row_parts) if row_parts else t(f"Dòng {idx}", f"{idx}行目")

        details = []
        if added > 0:
            st.success(t(f"Thêm mới {added} dòng", f"{added}行を追加"))
            diff_count += added
            for idx in added_idx:
                details.append(f"- :material/add_circle: **{t('Thêm mới', '追加')}**: <span style='color: #10b981;'>{format_row_name(staged_df, idx)}</span>")
                
        if deleted > 0:
            st.error(t(f"Xóa {deleted} dòng", f"{deleted}行を削除"))
            diff_count += deleted
            for idx in deleted_idx:
                details.append(f"- :material/cancel: **{t('Đã xóa', '削除')}**: <span style='text-decoration: line-through; color: #ef4444;'>{format_row_name(edit_df, idx)}</span>")
            
        common_idx = edit_df.index.intersection(staged_df.index)
        if len(common_idx) > 0:
            mod_mask = (edit_df.loc[common_idx] != staged_df.loc[common_idx]) & ~(edit_df.loc[common_idx].isnull() & staged_df.loc[common_idx].isnull())
            num_mods = mod_mask.any(axis=1).sum()
            if num_mods > 0:
                st.info(t(f"Chỉnh sửa {num_mods} dòng", f"{num_mods}行を編集"))
                diff_count += num_mods
                
                col_label_map = {
                    "ot_date": t("Ngày OT", "残業日"), "employee_name": t("Nhân sự", "担当者"),
                    "ot_hours": t("Giờ OT", "残業時間"), "ot_reason": t("Lý do", "残業理由"),
                    "manager_name": t("Quản lý", "PM"), "project_type": t("Loại dự án", "プロジェクト種別"),
                    "order_id": t("Mã dự án", "注文番号"), "order_name": t("Tên dự án", "注文名"),
                    "client_order_id": t("Mã đơn khách", "客先注文番号"), "hourly_rate": t("Lương/h", "時給"),
                    "payment_period": t("Kỳ thanh toán", "支払期間"), "standard_days": t("Số ngày chuẩn", "基準日数"),
                    "gross_salary": t("Lương Gross", "総支給額"), "date": t("Ngày ghi nhận", "記録日"),
                    "project_name": t("Tên dự án", "案件名"), "target_hours": t("Giờ công KH", "目標工数"),
                    "actual_hours": t("Giờ công TT", "実工数"), "unit_price": t("Đơn giá", "単価"),
                    "company_charge": t("Company Charge", "会社運用ﾁｬｰｼﾞ"), "profit": t("Lợi nhuận", "利益"),
                    "standard_incentive": t("Incentive TC", "基準金額"), "final_incentive": t("Nhận được", "受取額"),
                    "notes": t("Ghi chú", "備考")
                }
                for idx in common_idx[mod_mask.any(axis=1)]:
                    changed_cols = mod_mask.columns[mod_mask.loc[idx]].tolist()
                    row_name = format_row_name(edit_df, idx)
                    changes_str = []
                    for c in changed_cols:
                        if c in ['date_obj_edit', 'date_obj']: continue
                        col_label = col_label_map.get(c, str(c))
                        old_val = edit_df.loc[idx, c]
                        new_val = staged_df.loc[idx, c]
                        changes_str.append(f"**{col_label}**: <span style='color: #ef4444; font-weight: bold; font-size: 15px;'>{old_val}</span> ➔ <span style='color: #10b981; font-weight: bold; font-size: 15px;'>{new_val}</span>")
                    if changes_str:
                        details.append(f"- :material/edit: **{row_name}**: " + ", ".join(changes_str))
                        
        if details:
            with st.expander(t("Xem chi tiết thay đổi", "変更の詳細を表示"), expanded=True):
                st.markdown("\n".join(details), unsafe_allow_html=True)
                
        if diff_count == 0:
            st.write(t("Không có thay đổi nào.", "変更はありません。"))
            
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(t(":material/close: Hủy bỏ", ":material/close: キャンセル"), use_container_width=True):
                st.session_state[preview_key] = False
                st.rerun(scope="fragment")
        with col_btn2:
            if st.button(t(":material/check_circle: Xác nhận Lưu", ":material/check_circle: 保存を確認"), type="primary", use_container_width=True):
                untouched_df = df.loc[~df.index.isin(edit_df.index)].copy()
                save_df = pd.concat([untouched_df, staged_df], ignore_index=True)
                
                if 'date_obj_edit' in save_df.columns:
                    save_df = save_df.drop(columns=['date_obj_edit'])
                if 'date_obj' in save_df.columns:
                    save_df = save_df.drop(columns=['date_obj'])
                    
                if save_all_records(data_type, save_df.to_dict('records')):
                    st.session_state['pending_toast'] = t("Đã lưu thành công!", "保存しました！")
                    st.session_state[preview_key] = False
                    st.rerun()
    else:
        edited_df = st.data_editor(edit_df, use_container_width=True, num_rows="dynamic", column_order=col_order, column_config=col_cfg, key=f"dialog_edit_{data_type}")
        if st.button(t("Lưu Thay Đổi", "変更を保存"), use_container_width=True, type="primary", icon=":material/save:"):
            st.session_state[staged_key] = edited_df
            st.session_state[preview_key] = True
            st.rerun(scope="fragment")

def render_mini_leaderboard(data_type="ot"):
    records = get_records(data_type)
    if not records:
        from components.ui_utils import render_empty_state
        render_empty_state(t('Chưa có dữ liệu', 'データなし'), icon="inbox", height=100)
        return

    df = pd.DataFrame(records)
    if data_type == 'ot':
        if all(c in df.columns for c in ['ot_date', 'employee_name', 'order_name', 'ot_hours']):
            df = df.drop_duplicates(subset=['ot_date', 'employee_name', 'order_name', 'ot_hours'], keep='first')
        else:
            df = df.drop_duplicates()
    else:
        if all(c in df.columns for c in ['date', 'employee_name', 'project_name', 'final_incentive']):
            df = df.drop_duplicates(subset=['date', 'employee_name', 'project_name', 'final_incentive'], keep='first')
        else:
            df = df.drop_duplicates()
    
    date_col = 'ot_date' if data_type == 'ot' else 'date'
    if date_col in df.columns:
        df['date_obj'] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
        years = sorted(df['date_obj'].dt.year.dropna().astype(int).unique().tolist(), reverse=True)
    else:
        years = []
        
    year_options = [t("Tất cả", "すべて")] + years
    border_color = "#00a8e8"
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        from components.ui_utils import make_container_white
        make_container_white()
        icon = "timer" if data_type == "ot" else "payments"
        title_text = "TOP OVERTIME" if data_type == "ot" else "TOP INCENTIVE"
        
        # Gradient Title Block
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 8px;
                border-top: 4px solid {border_color};
                padding: 10px;
                margin-bottom: 15px;
                text-align: center; color: #2c3e50; font-size: 16px; font-weight: bold; text-transform: uppercase;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            '>
                <span class="material-symbols-rounded" style="vertical-align: middle; color: #00a8e8; margin-right: 5px; font-size: 20px;">{icon}</span>
                <span style="vertical-align: middle;">{title_text}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Selectbox (Small and centered)
        col_y, col_m = st.columns(2)
        with col_y:
            sel_year = st.selectbox(
                t("Chọn năm", "年を選択"), 
                options=year_options, 
                format_func=lambda x: f"{x}年" if st.session_state.get('lang', 'VN') == 'JP' and str(x).isdigit() else str(x),
                key=f"mini_year_{data_type}"
            )
        with col_m:
            month_options = [t("Tất cả", "すべて")] + list(range(1, 13))
            sel_month = st.selectbox(
                t("Chọn tháng", "月を選択"),
                options=month_options,
                format_func=lambda x: t(f"Tháng {x}", f"{x}月") if isinstance(x, int) else str(x),
                key=f"mini_month_{data_type}",
                help=t("Mẹo: Khi để Năm là 'Tất cả', hệ thống sẽ gộp chung dữ liệu của tháng này qua các năm.  \n👉 *Tiện lợi để phân tích tính mùa vụ*.", "ヒント: 「年」を「すべて」にすると、全年の該当月のデータを合算して表示します。  \n👉 *季節性の分析に便利です*。")
            )
            
        # Spacing
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
        if sel_year not in ["Tất cả", "すべて"]:
            df_filtered = df[df['date_obj'].dt.year == sel_year].copy()
        else:
            df_filtered = df.copy()

        if sel_month not in ["Tất cả", "すべて"]:
            df_filtered = df_filtered[df_filtered['date_obj'].dt.month == sel_month]

        if df_filtered.empty:
            from components.ui_utils import render_empty_state
            render_empty_state(t('Không có dữ liệu cho năm này', 'データなし'), icon="calendar_today", height=100)
        else:
            if data_type == "ot":
                if 'ot_hours' not in df_filtered.columns: df_filtered['ot_hours'] = 0
                df_filtered['ot_hours'] = pd.to_numeric(df_filtered['ot_hours'], errors='coerce').fillna(0)
                agg_df = df_filtered.groupby('employee_name')['ot_hours'].sum().reset_index()
                agg_df = agg_df.sort_values(by='ot_hours', ascending=False).reset_index(drop=True)
                val_col = 'ot_hours'
                val_suffix = "h"
            else:
                if 'final_incentive' not in df_filtered.columns: df_filtered['final_incentive'] = 0
                df_filtered['final_incentive'] = pd.to_numeric(df_filtered['final_incentive'], errors='coerce').fillna(0)
                agg_df = df_filtered.groupby('employee_name')['final_incentive'].sum().reset_index()
                agg_df = agg_df.sort_values(by='final_incentive', ascending=False).reset_index(drop=True)
                val_col = 'final_incentive'
                val_suffix = "¥"

            agg_df['rank'] = agg_df[val_col].rank(method='min', ascending=False).astype(int)
            top_5 = agg_df.head(5)

            if data_type == "ot":
                colors = [
                    ("linear-gradient(135deg, #ffcdd2 0%, #ffebee 100%)", "#c62828"),
                    ("linear-gradient(135deg, #ffe0b2 0%, #fff3e0 100%)", "#ef6c00"),
                    ("linear-gradient(135deg, #fff9c4 0%, #fffde7 100%)", "#f57f17")
                ]
            else:
                colors = [
                    ("linear-gradient(135deg, #b2ebf2 0%, #e0f7fa 100%)", "#00838f"),
                    ("linear-gradient(135deg, #e0f7fa 0%, #e0f7fa 100%)", "#00bcd4"),
                    ("linear-gradient(135deg, #e0f7fa 0%, #f1fbfc 100%)", "#00acc1")
                ]

            medals_dict = {1: "🥇", 2: "🥈", 3: "🥉", 4: "4️⃣", 5: "5️⃣"}

            html_content = ""
            for i, row in top_5.iterrows():
                emp_name = row['employee_name']
                val = row[val_col]
                rank = row['rank']
                medal = medals_dict.get(rank, "🏅")

                bg_color = "rgba(255,255,255,0.7)"
                text_color = "#00a8e8" 
                
                if rank <= 3:
                    bg_color = colors[rank - 1][0]
                    text_color = colors[rank - 1][1]
                
                formatted_val = f"{val:,.1f}" if data_type == "ot" else f"{int(val):,}"
                
                html_content += f"""
                <div style='
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: {bg_color};
                    padding: 8px 10px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    font-size: 13px;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
                    border-left: 3px solid {text_color};
                '>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span style='font-size: 16px;'>{medal}</span>
                        <span style='font-weight: 600; color: #34495e;' title='{emp_name}'>{emp_name}</span>
                    </div>
                    <span style='font-weight: 700; color: {text_color};'>{formatted_val} {val_suffix}</span>
                </div>
                """
                
            st.markdown(html_content, unsafe_allow_html=True)
            
            if len(top_5) > 0:
                fig = go.Figure(go.Bar(
                    x=top_5[val_col][::-1],
                    y=top_5['employee_name'][::-1],
                    orientation='h',
                    marker=dict(
                        color=top_5[val_col][::-1],
                        colorscale=[[0, '#e1f5fe'], [1, '#00a8e8']],
                    ),
                    text=top_5[val_col][::-1].apply(lambda x: f"{x:,.1f}" if data_type == "ot" else f"{int(x):,}"),
                    textposition='inside',
                    insidetextanchor='end',
                    textfont=dict(
                        color=['#2c3e50'] * (len(top_5) - 1) + ['white'] if len(top_5) > 0 else [],
                        size=11
                    )
                ))
                fig.update_layout(
                    font=dict(family="'Times New Roman', serif"),
                    margin=dict(l=0, r=0, t=5, b=5),
                    height=max(60, len(top_5) * 32),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(visible=False),
                    yaxis=dict(tickfont=dict(size=11, color='#2c3e50')),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    if st.button(t("✏️ Sửa dữ liệu (Nhanh)", "✏️ 簡易編集"), use_container_width=True, key=f"btn_edit_mini_{data_type}"):
        show_mini_edit_dialog(data_type, df)
