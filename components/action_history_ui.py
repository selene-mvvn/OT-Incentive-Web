import streamlit as st
import os
import math
import base64
from logic.i18n import t
from logic.action_log import get_action_logs, clear_all_logs, delete_action_log, cleanup_missing_files

def render_action_history():
    title = t("LỊCH SỬ THAO TÁC", "操作履歴")
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{title}</h2>", unsafe_allow_html=True)
    st.info(t("Lưu trữ lịch sử tính toán và xuất báo cáo gần đây.", "最近の計算とレポート出力履歴。"))
    
    logs = get_action_logs()
    
    if not logs:
        st.info(t("Chưa có lịch sử thao tác nào.", "操作履歴がありません。"))
        return
        
    with st.container():
        from components.ui_utils import make_container_white
        make_container_white()
        # st.markdown("---")

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
        .custom-history-card {
            position: relative;
            margin-bottom: 20px !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
            border-radius: 12px !important;
            background-color: #ffffff !important;
            border: 2px solid transparent !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
            padding: 0px !important;
        }

        .custom-history-card > div[data-testid="stVerticalBlock"] {
            padding: 12px 15px !important;
        }

        .custom-history-card.has-timeline-marker,
        .custom-history-card.has-missing-marker {
            margin-left: 40px !important;
            width: calc(100% - 40px) !important;
        }

        .custom-history-card:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 176, 240, 0.15) !important;
            border-color: rgba(0, 176, 240, 0.5) !important;
        }

        .custom-history-card.has-timeline-marker::before,
        .custom-history-card.has-missing-marker::before {
            content: '';
            position: absolute;
            top: -10px;
            bottom: -30px;
            left: -27px;
            width: 2px;
            background-color: #00B0F0;
            opacity: 0.3;
            z-index: 0;
        }

        .custom-history-card.has-timeline-marker:last-child::before,
        .custom-history-card.has-missing-marker:last-child::before {
            bottom: 50%; /* Stop line at the last dot */
        }

        .custom-history-card.has-timeline-marker::after,
        .custom-history-card.has-missing-marker::after {
            content: '';
            position: absolute;
            top: 50%;
            margin-top: -9px;
            left: -35px;
            width: 18px;
            height: 18px;
            box-sizing: border-box;
            border-radius: 50%;
            background-color: #ffffff;
            border: 4px solid #00B0F0;
            box-shadow: 0 0 0 4px rgba(0, 176, 240, 0.15);
            z-index: 1;
            transition: transform 0.3s ease;
        }

        .custom-history-card.has-timeline-marker:hover::after,
        .custom-history-card.has-missing-marker:hover::after {
            transform: scale(1.2);
        }

        /* Missing file styling */
        .custom-history-card.has-missing-marker {
            opacity: 0.7;
            background-color: #ffffff !important;
            border-radius: 12px !important;
            margin-left: 25px !important;
            margin-bottom: 25px !important;
            border: 1px solid rgba(231, 76, 60, 0.3) !important;
        }
        .custom-history-card.has-missing-marker::after {
            border-color: #e74c3c;
            box-shadow: 0 0 0 4px rgba(231, 76, 60, 0.15);
        }

        /* Custom buttons inside timeline */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.timeline-marker) button {
            border-radius: 6px !important;
            padding: 5px 15px !important;
            font-size: 13px !important;
        }
        /* Override global h3 underline length for history cards */
        h3.history-card-title::after {
            width: 50px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Removed redundant <br> to reduce gap
        if 'selected_logs' not in st.session_state:
            st.session_state['selected_logs'] = {}

        def toggle_log(log_id):
            st.session_state['selected_logs'][log_id] = not st.session_state['selected_logs'].get(log_id, False)

        selected_ids = [k for k, v in st.session_state.get('selected_logs', {}).items() if v]
        if selected_ids:
            import streamlit.components.v1 as components
            components.html("""
            <script>
            setTimeout(() => {
                const markers = window.parent.document.querySelectorAll('.bulk-marker');
                markers.forEach(marker => {
                    const markerContainer = marker.closest('div.element-container');
                    if (!markerContainer) return;

                    // Xóa trắng khoảng trống của marker
                    markerContainer.style.display = 'none';

                    const wrapper = markerContainer.parentNode;
                    if (wrapper) {
                        // Căn chỉnh dòng Text (xóa margin của thẻ p do Streamlit tạo ra)
                        const pTags = wrapper.querySelectorAll('p');
                        pTags.forEach(p => {
                            p.style.setProperty('margin', '0', 'important');
                            p.style.setProperty('padding', '0', 'important');
                        });

                        // Biến stVerticalBlock thành một thanh công cụ (Pill-shaped action bar)
                        wrapper.style.setProperty('background-color', '#ede9fe', 'important');
                        wrapper.style.setProperty('border-radius', '50px', 'important');
                        wrapper.style.setProperty('padding', '4px 8px', 'important');
                        wrapper.style.setProperty('margin-top', '-10px', 'important');
                        wrapper.style.setProperty('margin-bottom', '20px', 'important');
                        wrapper.style.setProperty('display', 'flex', 'important');
                        wrapper.style.setProperty('flex-direction', 'row', 'important');
                        wrapper.style.setProperty('justify-content', 'center', 'important');
                        wrapper.style.setProperty('align-items', 'center', 'important');
                        wrapper.style.setProperty('gap', '4px', 'important');
                        wrapper.style.setProperty('width', 'max-content', 'important');
                        wrapper.style.setProperty('box-shadow', '0 4px 15px rgba(0,0,0,0.06)', 'important');

                        // Co gọn các thành phần bên trong (div.element-container)
                        const children = Array.from(wrapper.children);
                        children.forEach(child => {
                            if (child.classList.contains('element-container')) {
                                child.style.setProperty('width', 'auto', 'important');
                                child.style.setProperty('flex', '0 1 auto', 'important');
                                child.style.setProperty('min-width', '0', 'important');
                                child.style.setProperty('margin', '0', 'important');
                            }
                        });

                        // Định dạng nút bấm (Thiết kế dạng icon tròn)
                        const btns = wrapper.querySelectorAll('button');
                        btns.forEach((btn, index) => {
                            btn.style.setProperty('background-color', 'transparent', 'important');
                            btn.style.setProperty('color', '#4c1d95', 'important');
                            btn.style.setProperty('border', 'none', 'important');
                            btn.style.setProperty('box-shadow', 'none', 'important');
                            btn.style.setProperty('border-radius', '50%', 'important');
                            btn.style.setProperty('width', '36px', 'important');
                            btn.style.setProperty('height', '36px', 'important');
                            btn.style.setProperty('min-height', '36px', 'important');
                            btn.style.setProperty('padding', '0', 'important');
                            btn.style.setProperty('display', 'flex', 'important');
                            btn.style.setProperty('justify-content', 'center', 'important');
                            btn.style.setProperty('align-items', 'center', 'important');
                            btn.style.setProperty('transition', 'all 0.2s', 'important');

                            // Ẩn chữ mặc định
                            const textElements = btn.querySelectorAll('p, span, div');
                            textElements.forEach(el => {
                                if (el.tagName !== 'svg' && el.tagName !== 'path' && el.tagName !== 'polyline' && el.tagName !== 'line') {
                                    el.style.setProperty('display', 'none', 'important');
                                }
                            });

                            btn.addEventListener('mouseenter', () => btn.style.setProperty('background-color', '#ffffff', 'important'));
                            btn.addEventListener('mouseleave', () => btn.style.setProperty('background-color', 'transparent', 'important'));
                        });

                        // Chèn icon SVG cho 2 nút
                        if (btns.length >= 1 && !btns[0].querySelector('svg')) {
                            btns[0].insertAdjacentHTML('beforeend', `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`);
                        }
                        if (btns.length >= 2 && !btns[1].querySelector('svg')) {
                            btns[1].insertAdjacentHTML('beforeend', `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`);
                        }
                    }
                });
            }, 50);
            </script>
            """, height=0, width=0)

            with st.container():
                st.markdown("<span class='bulk-marker' style='display:none'></span>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color:#ffffff; color:#4c1d95; font-weight:bold; font-size:15px; width:36px; height:36px; border-radius:50%; display:flex; justify-content:center; align-items:center; margin:0;'>{len(selected_ids)}</div>", unsafe_allow_html=True)

                valid_logs = [l for l in logs if l.get('id') in selected_ids and l.get('file_b64')]
                if valid_logs:
                    import zipfile
                    import io
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for idx, l in enumerate(valid_logs):
                            file_bytes = base64.b64decode(l.get('file_b64'))
                            safe_name = l.get('original_filename', f'file_{l.get("id")}.xlsx')
                            if sum(1 for x in valid_logs if x.get('original_filename') == safe_name) > 1:
                                safe_name = f"{idx+1}_{safe_name}"
                            zip_file.writestr(safe_name, file_bytes)

                    st.download_button(
                        label=t("TẢI ZIP", "ZIP DL"),
                        data=zip_buffer.getvalue(),
                        file_name="LichSu_DaChon.zip",
                        mime="application/zip",
                        key="bulk_download"
                    )

                if st.button(t("XÓA", "削除"), key="bulk_delete"):
                    for lid in selected_ids:
                        delete_action_log(lid)
                    st.session_state['selected_logs'] = {}
                    st.rerun()

        # 4. Render Logs
        for i, log in enumerate(paginated_logs):
            log_id = log.get("id")
            file_b64 = log.get("file_b64")
            is_missing = file_b64 is None

            action_type_vn = log.get('action_type_vn', log.get('action_type', ''))
            action_type_jp = log.get('action_type_jp', log.get('action_type', ''))
            action_type = action_type_vn if st.session_state.get('lang', 'VN') == 'VN' else action_type_jp

            desc = log.get("description_vn") if st.session_state.get('lang', 'VN') == 'VN' else log.get("description_jp")

            with st.container(border=True):
                c_chk, c_head, c_dl, c_del = st.columns([0.5, 6.5, 2, 1])
                with c_chk:
                    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                    st.checkbox(" ", key=f"chk_sel_{log_id}", value=st.session_state['selected_logs'].get(log_id, False), on_change=toggle_log, args=(log_id,))
                with c_head:
                    marker_class = "missing-marker" if is_missing else "timeline-marker"
                    filename_html = f"<span style='font-size:15px; font-weight:normal; color:#3498db; margin-left:12px;'>📄 {log.get('original_filename')}</span>" if log.get('original_filename') else ""
                    st.markdown(f"<h3 class='history-card-title' style='margin:0; padding:0; color:#2c3e50; font-size:18px; font-weight:bold;'><span class='action-card-marker'></span><span class='white-card-bg'></span><span class='{marker_class}'></span>{action_type}{filename_html}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin:0; padding:0; color:#7f8c8d; font-size:13px; font-weight:bold;'>{log.get('timestamp')}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin-top:8px; margin-bottom:5px; color:#34495e; font-size:15px;'>{desc}</p>", unsafe_allow_html=True)
                with c_dl:
                    if not is_missing:
                        file_bytes = base64.b64decode(file_b64)
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

        # 5. Pagination Controls
        if total_pages > 1:
            st.markdown("<br><hr>", unsafe_allow_html=True)
            pc1, pc2, pc3 = st.columns([1, 2, 1])
            with pc1:
                if st.button("◀ " + t("Trang trước", "前へ"), disabled=(current_page == 1), use_container_width=True):
                    st.session_state['history_page'] -= 1
                    st.rerun()
            with pc2:
                st.markdown(f"<div style='text-align: center; margin-top: 10px; font-size: 16px;'><b>{t('Trang', 'ページ')} {current_page} / {total_pages}</b></div>", unsafe_allow_html=True)
            with pc3:
                if st.button(t("Trang sau", "次へ") + " ▶", disabled=(current_page == total_pages), use_container_width=True):
                    st.session_state['history_page'] += 1
                    st.rerun()

        from components.ui_utils import make_history_cards_white
        make_history_cards_white()
