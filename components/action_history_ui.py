import streamlit as st
import os
import math
from logic.i18n import t
from logic.action_log import get_action_logs, get_file_bytes, clear_all_logs, delete_action_log, cleanup_missing_files

def render_action_history():
    title = t("LỊCH SỬ THAO TÁC", "操作履歴")
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{title}</h2>", unsafe_allow_html=True)
    st.info(t("Lưu trữ lịch sử tính toán và xuất báo cáo gần đây.", "最近の計算とレポート出力履歴。"))
    
    logs = get_action_logs()
    
    if not logs:
        st.info(t("Chưa có lịch sử thao tác nào.", "操作履歴がありません。"))
        return
        
    st.markdown("---")
    
    # 1. Search and Filter
    col_search, col_filter, col_clean, col_clear = st.columns([3, 2, 2, 2])
    with col_search:
        search_query = st.text_input("🔍 " + t("Tìm kiếm (tên file, mô tả)...", "検索（ファイル名、説明）..."))
    with col_filter:
        action_types_set = set()
        for log in logs:
            at_vn = log.get('action_type_vn', log.get('action_type', ''))
            at_jp = log.get('action_type_jp', log.get('action_type', ''))
            at_display = at_vn if st.session_state.get('lang', 'VN') == 'VN' else at_jp
            if at_display:
                action_types_set.add(at_display)
        action_types = ["All"] + list(action_types_set)
        type_filter = st.selectbox("📂 " + t("Lọc theo thao tác", "操作で絞り込み"), action_types)
    with col_clean:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🧹 " + t("Dọn file lỗi", "エラーをクリア"), help=t("Xóa các lịch sử bị mất file gốc", "見つからないファイルを自動削除"), use_container_width=True):
            cleanup_missing_files()
            st.rerun()
    with col_clear:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button(t("🗑️ Xóa toàn bộ", "🗑️ 全履歴クリア"), type="primary", use_container_width=True):
            clear_all_logs()
            st.rerun()
            
    # Apply filters
    filtered_logs = logs
    if search_query:
        sq = search_query.lower()
        filtered_logs = [log for log in filtered_logs if sq in log.get("original_filename", "").lower() or sq in log.get("description_vn", "").lower() or sq in log.get("description_jp", "").lower()]
        
    if type_filter != "All":
        temp_logs = []
        for log in filtered_logs:
            at_vn = log.get('action_type_vn', log.get('action_type', ''))
            at_jp = log.get('action_type_jp', log.get('action_type', ''))
            at_display = at_vn if st.session_state.get('lang', 'VN') == 'VN' else at_jp
            if at_display == type_filter:
                temp_logs.append(log)
        filtered_logs = temp_logs
        
    if not filtered_logs:
        st.warning(t("Không tìm thấy kết quả nào phù hợp.", "一致する結果が見つかりません。"))
        return
        
    # 2. Pagination
    ITEMS_PER_PAGE = 10
    total_pages = math.ceil(len(filtered_logs) / ITEMS_PER_PAGE)
    
    if 'history_page' not in st.session_state:
        st.session_state['history_page'] = 1
        
    if st.session_state['history_page'] > total_pages:
        st.session_state['history_page'] = 1
        
    current_page = st.session_state['history_page']
    start_idx = (current_page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paginated_logs = filtered_logs[start_idx:end_idx]
    
    # 3. Timeline UI CSS
    st.markdown("""
    <style>
    /* CSS hack to turn st.container(border=True) into a timeline node */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.timeline-marker) {
        position: relative;
        margin-left: 25px !important;
        margin-bottom: 25px !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-radius: 12px !important;
        background-color: #ffffff;
        border: 1px solid rgba(0, 176, 240, 0.2) !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.timeline-marker)::before {
        content: '';
        position: absolute;
        top: -20px;
        bottom: -45px;
        left: -25px;
        width: 2px;
        background-color: #00B0F0;
        opacity: 0.3;
        z-index: 0;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.timeline-marker):last-child::before {
        bottom: 0; /* Stop line at the last item */
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.timeline-marker)::after {
        content: '';
        position: absolute;
        top: 25px;
        left: -33px;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background-color: #ffffff;
        border: 4px solid #00B0F0;
        box-shadow: 0 0 0 4px rgba(0, 176, 240, 0.15);
        z-index: 1;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.timeline-marker):hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 176, 240, 0.12) !important;
        border-color: rgba(0, 176, 240, 0.5) !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.timeline-marker):hover::after {
        transform: scale(1.2);
    }
    
    /* Missing file styling */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.missing-marker) {
        opacity: 0.7;
        border: 1px solid rgba(231, 76, 60, 0.3) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.missing-marker)::after {
        border-color: #e74c3c;
        box-shadow: 0 0 0 4px rgba(231, 76, 60, 0.15);
    }
    
    /* Custom buttons inside timeline */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.timeline-marker) button {
        border-radius: 6px !important;
        padding: 5px 15px !important;
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. Render Logs
    for i, log in enumerate(paginated_logs):
        log_id = log.get("id")
        file_path = log.get("saved_path")
        is_missing = not (file_path and os.path.exists(file_path))
        
        action_type_vn = log.get('action_type_vn', log.get('action_type', ''))
        action_type_jp = log.get('action_type_jp', log.get('action_type', ''))
        action_type = action_type_vn if st.session_state.get('lang', 'VN') == 'VN' else action_type_jp
            
        desc = log.get("description_vn") if st.session_state.get('lang', 'VN') == 'VN' else log.get("description_jp")
        
        with st.container(border=True):
            marker_class = "missing-marker" if is_missing else "timeline-marker"
            st.markdown(f"<div class='{marker_class}'></div>", unsafe_allow_html=True)
            
            c_head, c_dl, c_del = st.columns([7, 2, 1])
            with c_head:
                filename_html = f"<span style='font-size:15px; font-weight:normal; color:#3498db; margin-left:12px;'>📄 {log.get('original_filename')}</span>" if log.get('original_filename') else ""
                st.markdown(f"<h3 style='margin:0; padding:0; color:#2c3e50; font-size:18px;'>{action_type}{filename_html}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin:0; padding:0; color:#7f8c8d; font-size:13px; font-weight:bold;'>{log.get('timestamp')}</p>", unsafe_allow_html=True)
            with c_dl:
                if not is_missing:
                    file_bytes = get_file_bytes(file_path)
                    st.download_button(
                        label=t("TẢI LẠI", "再DL"),
                        data=file_bytes,
                        file_name=log.get("original_filename"),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{log_id}",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.button("⚠️ " + t("Mất file", "なし"), disabled=True, key=f"dl_{log_id}", help=t("File vật lý không còn tồn tại trên hệ thống", "物理ファイルはシステムに存在しません"), use_container_width=True)
            with c_del:
                if st.button(t("XÓA", "削除"), key=f"del_{log_id}", help=t("Xóa mục này", "削除"), use_container_width=True):
                    delete_action_log(log_id)
                    st.rerun()
                    
            st.markdown(f"<p style='margin-top:5px; margin-bottom:5px; color:#34495e; font-size:15px;'>{desc}</p>", unsafe_allow_html=True)
                
    # 5. Pagination Controls
    if total_pages > 1:
        st.markdown("<br><hr>", unsafe_allow_html=True)
        pc1, pc2, pc3 = st.columns([1, 2, 1])
        with pc1:
            if st.button("⬅️ " + t("Trang trước", "前へ"), disabled=(current_page == 1), use_container_width=True):
                st.session_state['history_page'] -= 1
                st.rerun()
        with pc2:
            st.markdown(f"<div style='text-align: center; margin-top: 10px; font-size: 16px;'><b>{t('Trang', 'ページ')} {current_page} / {total_pages}</b></div>", unsafe_allow_html=True)
        with pc3:
            if st.button(t("Trang sau", "次へ") + " ➡️", disabled=(current_page == total_pages), use_container_width=True):
                st.session_state['history_page'] += 1
                st.rerun()
