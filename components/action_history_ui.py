import streamlit as st
import os
import math
import base64
from logic.i18n import t
from logic.action_log import get_action_logs, clear_all_logs, delete_action_log, cleanup_missing_files

def render_action_history():
    st.markdown("""
        <style>
            .custom-history-card {
                transition: all 0.2s ease-in-out !important;
            }
            .custom-history-card:hover {
                box-shadow: 0 6px 16px rgba(0,0,0,0.1) !important;
                transform: translateY(-2px) !important;
                border-color: #3498db !important;
            }
            h3.history-card-title::after {
                width: 50px !important;
            }
                        [data-testid="stMain"] .stButton button, [data-testid="stMain"] [data-testid="stButton"] button,
            [data-testid="stMain"] .stDownloadButton button, [data-testid="stMain"] [data-testid="stDownloadButton"] button {
                width: 100% !important;
                min-width: 100% !important;
                height: 42px !important;
                min-height: 42px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 0 10px !important;
            }
        </style>
    """, unsafe_allow_html=True)
    title = t("LỊCH SỬ THAO TÁC", "操作履歴")
    st.markdown(f"<h2 style='font-size: 28px; font-weight: 600;'>{title}</h2>", unsafe_allow_html=True)
    st.info(t("Lưu trữ lịch sử tính toán và xuất báo cáo gần đây.", "最近の計算とレポート出力履歴。"))
    
    logs = get_action_logs()
    
    if not logs:
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            from components.ui_utils import render_empty_state
            render_empty_state(
                text=t("Chưa có dữ liệu lịch sử", "操作履歴がありません"),
                subtitle=t("Hãy thực hiện tính toán hoặc xuất báo cáo để xem lịch sử tại đây.", "計算やレポート出力を実行すると、ここに履歴が表示されます。"),
                icon="history",
                height=250
            )
        return
        
    with st.container():
        from components.ui_utils import make_container_white, make_history_cards_white
        make_container_white()
        make_history_cards_white()
        # 1. Search and Filter
        col_search, col_filter, col_clean, col_clear = st.columns([3.2, 1.8, 2.2, 2.2])
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
            if st.button(t(":material/cleaning_services: Dọn file lỗi", ":material/cleaning_services: エラーをクリア"), use_container_width=True):
                cleanup_missing_files()
                st.rerun()
        with col_clear:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button(t(":material/delete: Xóa toàn bộ", ":material/delete: 全履歴クリア"), type="primary", use_container_width=True):
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
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 1.5, 1])
            with col2:
                st.markdown("""
                    <div style='text-align: center; padding: 20px; width: 100%;'>
                        <div style='display: inline-flex; align-items: center; justify-content: center; width: 100px; height: 100px; border-radius: 50%; background-color: #00B0F0; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0, 176, 240, 0.3);'>
                            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="54" height="54">
                                <circle cx="11" cy="11" r="8"></circle>
                                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                <line x1="8" y1="11" x2="14" y2="11"></line>
                            </svg>
                        </div>
                        <div style='color: #2c3e50; font-family: "Times New Roman", serif; font-size: 20px; font-weight: bold; margin: 0 auto; line-height: 1.2;'>""" + t("Không tìm thấy kết quả nào", "一致する結果が見つかりません") + """</div>
                        <div style='color: #7f8c8d; font-size: 15px; margin-top: 10px; line-height: 1.5;'>""" + t("Vui lòng thử lại với từ khóa hoặc bộ lọc khác.", "別のキーワードやフィルターをお試しください。") + """</div>
                    </div>
                """, unsafe_allow_html=True)
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
                const parentDoc = window.parent.document;
                
                // 1. Inject Global CSS if not exists
                if (!parentDoc.getElementById('custom-toolbar-style')) {
                    const style = parentDoc.createElement('style');
                    style.id = 'custom-toolbar-style';
                    style.innerHTML = `                        
                        .custom-toolbar-wrapper {
                            border-radius: 50px !important;
                            padding: 10px 6px !important;
                            margin: 0 !important;
                            display: flex !important;
                            flex-direction: column !important;
                            justify-content: center !important;
                            align-items: center !important;
                            gap: 10px !important;
                            width: 44px !important;
                            height: max-content !important;
                            box-sizing: border-box !important;
                            border: 1px solid rgba(0, 176, 240, 0.2) !important;
                            box-shadow: none !important;
                            position: fixed !important;
                            top: 50% !important;
                            transform: translateY(-50%) !important;
                            z-index: 999999 !important;
                        }
                        .custom-toolbar-wrapper p,
                        .custom-toolbar-wrapper div[data-testid="stMarkdownContainer"] {
                            margin: 0 !important; padding: 0 !important;
                            display: flex !important; align-items: center !important; justify-content: center !important;
                            height: 100% !important;
                        }
                        [data-testid="stMain"] .custom-toolbar-wrapper button,
                        [data-testid="stMain"] .custom-toolbar-wrapper .stButton button,
                        [data-testid="stMain"] .custom-toolbar-wrapper .stDownloadButton button,
                        .custom-toolbar-wrapper button {
                            background-color: #ffffff !important; color: #00B0F0 !important;
                            border: 1.5px solid #00B0F0 !important; box-shadow: none !important; border-radius: 50% !important;
                            width: 32px !important; height: 32px !important; min-width: 32px !important; min-height: 32px !important; max-width: 32px !important; max-height: 32px !important;
                            margin: 0 !important; padding: 0 !important;
                            display: flex !important; justify-content: center !important; align-items: center !important;
                            transition: all 0.2s !important;
                        }
                        .custom-toolbar-wrapper button:hover,
                        [data-testid="stMain"] .custom-toolbar-wrapper button:hover { 
                            background-color: #00B0F0 !important; color: #ffffff !important; border-color: #00B0F0 !important;
                        }
                        .custom-toolbar-wrapper button p,
                        .custom-toolbar-wrapper button span,
                        .custom-toolbar-wrapper button div { display: none !important; }
                        .custom-toolbar-wrapper .toolbar-btn-container {
                            width: auto !important; flex: 0 1 auto !important; min-width: 0 !important;
                            margin: 0 !important; padding: 0 !important;
                            display: flex !important; align-items: center !important; justify-content: center !important;
                            height: 32px !important;
                        }
                        .custom-toolbar-wrapper .toolbar-hidden-container {
                            display: none !important; height: 0 !important; margin: 0 !important; padding: 0 !important;
                        }
                        [data-testid="stMain"] .custom-toolbar-wrapper div.stButton,
                        [data-testid="stMain"] .custom-toolbar-wrapper div[data-testid="stButton"],
                        [data-testid="stMain"] .custom-toolbar-wrapper div.stDownloadButton,
                        [data-testid="stMain"] .custom-toolbar-wrapper div[data-testid="stDownloadButton"],
                        .custom-toolbar-wrapper div.stButton,
                        .custom-toolbar-wrapper div[data-testid="stButton"] {
                            margin: 0 !important; padding: 0 !important; height: 32px !important; width: 32px !important; min-width: 32px !important;
                            display: flex !important; align-items: center !important; justify-content: center !important;
                        }
                    `;
                    parentDoc.head.appendChild(style);
                    // Setup cleanup logic when the iframe unmounts (e.g., page navigation)
                    const cleanup = () => {
                        parentDoc.querySelectorAll('.custom-toolbar-wrapper').forEach(el => {
                            // Only clean up if the marker is actually gone or we are unloading
                            el.classList.remove('custom-toolbar-wrapper');
                            el.style.removeProperty('background-color');
                            el.style.removeProperty('left');
                            const badge = el.querySelector('.selection-badge');
                            if (badge) badge.remove();
                            Array.from(el.children).forEach(child => {
                                child.classList.remove('toolbar-btn-container');
                                child.classList.remove('toolbar-hidden-container');
                            });
                        });
                    };
                    
                    window.addEventListener('unload', cleanup);
                    
                    // Also observe in case Streamlit rerenders parts without destroying the iframe
                    const observer = new MutationObserver(() => {
                        parentDoc.querySelectorAll('.custom-toolbar-wrapper').forEach(el => {
                            if (!el.querySelector('.bulk-marker')) {
                                el.classList.remove('custom-toolbar-wrapper');
                                el.style.removeProperty('background-color');
                                el.style.removeProperty('left');
                                const badge = el.querySelector('.selection-badge');
                                if (badge) badge.remove();
                                Array.from(el.children).forEach(child => {
                                    child.classList.remove('toolbar-btn-container');
                                    child.classList.remove('toolbar-hidden-container');
                                });
                            }
                        });
                    });
                    observer.observe(parentDoc.body, { childList: true, subtree: true });
                }

                // 2. Setup toolbar
                const markers = parentDoc.querySelectorAll('.bulk-marker');
                markers.forEach(marker => {
                    const markerContainer = marker.closest('div.element-container');
                    if (!markerContainer) return;
                    
                    markerContainer.style.display = 'none';
                    const wrapper = markerContainer.parentNode;
                    
                    if (wrapper) {
                        wrapper.classList.add('custom-toolbar-wrapper');
                        
                        let infoBg = 'rgba(0, 176, 240, 0.15)';
                        const stAlertChild = parentDoc.querySelector('[data-testid="stAlert"] > div');
                        if (stAlertChild) {
                            const bg = window.parent.getComputedStyle(stAlertChild).backgroundColor;
                            if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') infoBg = bg;
                        }
                        wrapper.style.setProperty('background-color', infoBg, 'important');
                        
                        function updateLeftPos() {
                            let leftPos = 10;
                            const blockContainer = parentDoc.querySelector('.block-container') || parentDoc.querySelector('div[data-testid="stAppViewBlockContainer"]');
                            const sidebarEdge = blockContainer ? blockContainer.getBoundingClientRect().left : 0; 
                            const whiteCard = wrapper.parentElement.closest('[data-testid="stVerticalBlock"]');
                            if (whiteCard) {
                                const whiteCardEdge = whiteCard.getBoundingClientRect().left;
                                leftPos = whiteCardEdge - 56;
                                if (leftPos < sidebarEdge + 5) {
                                    leftPos = sidebarEdge + (whiteCardEdge - sidebarEdge) / 2 - 22;
                                }
                            }
                            if (leftPos < sidebarEdge + 2) leftPos = sidebarEdge + 2; 
                            wrapper.style.setProperty('left', `${leftPos}px`, 'important');
                        }
                        updateLeftPos();
                        const posInterval = setInterval(() => {
                            if (!parentDoc.contains(wrapper)) {
                                clearInterval(posInterval);
                            } else {
                                updateLeftPos();
                            }
                        }, 50);

                        const count = marker.getAttribute('data-count') || '0';
                        let badge = wrapper.querySelector('.selection-badge');
                        if (!badge) {
                            badge = parentDoc.createElement('div');
                            badge.className = 'selection-badge';
                            badge.style.cssText = 'background-color: #ffffff !important; color: #0284c7 !important; font-weight: bold !important; font-size: 14px !important; width: 32px !important; height: 32px !important; border-radius: 50% !important; display: flex !important; justify-content: center !important; align-items: center !important; box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important; flex-shrink: 0 !important; margin: 0 !important;';
                            wrapper.insertBefore(badge, wrapper.firstChild);
                        }
                        badge.innerText = count;

                        const children = Array.from(wrapper.children);
                        children.forEach(child => {
                            if (child.classList.contains('element-container')) {
                                if (child.querySelector('button') || child.querySelector('div[data-testid="stButton"]')) {
                                    child.classList.add('toolbar-btn-container');
                                } else {
                                    child.classList.add('toolbar-hidden-container');
                                }
                            }
                        });

                        const btns = wrapper.querySelectorAll('button');
                        let dlBtn, delBtn, unBtn;
                        if (btns.length === 3) { dlBtn = btns[0]; delBtn = btns[1]; unBtn = btns[2]; }
                        else if (btns.length === 2) { delBtn = btns[0]; unBtn = btns[1]; }
                        else if (btns.length === 1) { unBtn = btns[0]; } // fallback
                        
                        if (dlBtn && !dlBtn.querySelector('svg')) {
                            dlBtn.insertAdjacentHTML('beforeend', `<svg style="pointer-events: none;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`);
                        }
                        if (delBtn && !delBtn.querySelector('svg')) {
                            delBtn.insertAdjacentHTML('beforeend', `<svg style="pointer-events: none;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`);
                        }
                        if (unBtn && !unBtn.querySelector('svg')) {
                            unBtn.insertAdjacentHTML('beforeend', `<svg style="pointer-events: none;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`);
                        }
                        
                        if (window.frameElement) {
                            window.frameElement.style.display = 'none';
                            if (window.frameElement.parentElement) window.frameElement.parentElement.style.display = 'none';
                        }
                    }
                });
            }, 50);
            </script>
            """ + f"<!-- {len(selected_ids)}_{__import__('time').time()} -->", height=0, width=0)

        # 4. Render Logs
        for i, log in enumerate(paginated_logs):
            log_id = log.get("id")
            file_b64 = log.get("file_b64")
            is_missing = file_b64 is None

            action_type_vn = log.get('action_type_vn', log.get('action_type', ''))
            action_type_jp = log.get('action_type_jp', log.get('action_type', ''))
            action_type = action_type_vn if st.session_state.get('lang', 'VN') == 'VN' else action_type_jp

            desc = log.get("description_vn") if st.session_state.get('lang', 'VN') == 'VN' else log.get("description_jp")
            
            # Determine color based on action type
            dot_color = "#00B0F0"
            at_vn_lower = action_type_vn.lower()
            if "excel" in at_vn_lower: dot_color = "#27ae60"
            elif "ot" in at_vn_lower: dot_color = "#2980b9"
            elif "incentive" in at_vn_lower: dot_color = "#8e44ad"
            elif "sửa" in at_vn_lower: dot_color = "#f39c12"

            with st.container(border=True):
                c_chk, c_head, c_preview, c_dl, c_del = st.columns([0.5, 5.5, 1.5, 1.5, 1.5], vertical_alignment="center")
                with c_chk:
                    st.checkbox(" ", key=f"chk_sel_{log_id}", value=st.session_state['selected_logs'].get(log_id, False), on_change=toggle_log, args=(log_id,))
                with c_head:
                    if is_missing: dot_color = "#e74c3c"
                    filename_html = f"<span style='font-size:15px; font-weight:normal; color:#3498db; margin-left:12px;'>📄 {log.get('original_filename')}</span>" if log.get('original_filename') else ""
                    st.markdown(f"<h3 class='history-card-title' style='margin:0; padding:0; color:#2c3e50; font-size:18px; font-weight:bold;'>{action_type}{filename_html}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin:0; padding:0; color:#7f8c8d; font-size:13px; font-weight:bold;'>{log.get('timestamp')}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin-top:8px; margin-bottom:5px; color:#34495e; font-size:15px;'>{desc}</p>", unsafe_allow_html=True)
                with c_preview:
                    if not is_missing:
                        preview_key = f"preview_{log_id}"
                        if st.button(":material/visibility: " + t("XEM TRƯỚC", "プレビュー"), key=preview_key, use_container_width=True):
                            st.session_state[f'show_preview_{log_id}'] = not st.session_state.get(f'show_preview_{log_id}', False)
                            st.rerun()
                    else:
                        st.empty()
                with c_dl:
                    if not is_missing:
                        file_bytes = base64.b64decode(file_b64)
                        st.download_button(
                            label=t(":material/download: TẢI LẠI", ":material/download: 再DL"),
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
                    if st.button(t(":material/delete: XÓA", ":material/delete: 削除"), key=f"del_{log_id}", use_container_width=True):
                        delete_action_log(log_id)
                        st.rerun()

                if st.session_state.get(f'show_preview_{log_id}', False) and not is_missing:
                    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                    st.markdown(t("**Xem trước dữ liệu (5 dòng đầu):**", "**データプレビュー (最初の5行):**"))
                    try:
                        import pandas as pd
                        import io
                        file_bytes = base64.b64decode(file_b64)
                        original_filename = log.get("original_filename", "")
                        
                        if original_filename.endswith(".xlsx"):
                            # Heuristic to find the actual header row
                            df_temp = pd.read_excel(io.BytesIO(file_bytes), nrows=15, header=None)
                            header_idx = 0
                            max_non_nulls = 0
                            for idx, row_data in df_temp.iterrows():
                                non_nulls = row_data.dropna().count()
                                if non_nulls > max_non_nulls:
                                    max_non_nulls = non_nulls
                                    header_idx = idx
                            
                            df_preview = pd.read_excel(io.BytesIO(file_bytes), skiprows=header_idx, nrows=5)
                            
                            # Format numbers with commas (handling mixed type columns)
                            for col in df_preview.columns:
                                df_preview[col] = df_preview[col].apply(
                                    lambda x: f"{int(x):,}" if pd.notna(x) and isinstance(x, (int, float)) and x == int(x) else (f"{x:,}" if pd.notna(x) and isinstance(x, (int, float)) else x)
                                )
                                
                            st.dataframe(df_preview, use_container_width=True)
                        elif original_filename.endswith(".zip"):
                            st.info(t("Đây là file ZIP tổng hợp nhiều báo cáo, vui lòng tải về để giải nén và xem chi tiết.", "これは複数のレポートを含むZIPファイルです。ダウンロードして展開してください。"))
                        else:
                            st.info(t("Định dạng file không hỗ trợ xem trước.", "プレビューがサポートされていないファイル形式です。"))
                    except Exception as e:
                        st.error(t(f"Không thể đọc file để xem trước: {e}", f"プレビュー用ファイルの読み込みに失敗しました: {e}"))


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

        if selected_ids:
            with st.container():
                st.markdown(f"<span class='bulk-marker' style='display:none' data-count='{len(selected_ids)}'></span>", unsafe_allow_html=True)

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

                def _do_bulk_delete():
                    for lid in selected_ids:
                        delete_action_log(lid)
                        if f"chk_sel_{lid}" in st.session_state:
                            st.session_state[f"chk_sel_{lid}"] = False
                    st.session_state['selected_logs'] = {}

                if st.button(t("XÓA", "削除"), key="bulk_delete", on_click=_do_bulk_delete):
                    pass

                def _do_bulk_uncheck():
                    for lid in selected_ids:
                        if f"chk_sel_{lid}" in st.session_state:
                            st.session_state[f"chk_sel_{lid}"] = False
                    st.session_state['selected_logs'] = {}

                if st.button(t("BỎ CHỌN", "選択解除"), key="bulk_uncheck", on_click=_do_bulk_uncheck):
                    pass

        else:
            # CLEANUP SCRIPT: Sử dụng CSS Class an toàn.
            # Thay vì thao tác trực tiếp lên inline styles (điều gây ra xung đột với Streamlit),
            # ta chỉ việc xóa bỏ class `.custom-toolbar-wrapper`, mọi CSS !important sẽ tự biến mất!
            import streamlit.components.v1 as components
            components.html("""
            <script>
            setTimeout(() => {
                // React có thể đã xóa mất class 'custom-toolbar-wrapper' khi tái chế thẻ DOM.
                // Do đó, ta tìm thẻ DOM bị lỗi thông qua 'selection-badge' (phần tử JS ta chèn tay vào mà React không biết để xóa).
                const badges = window.parent.document.querySelectorAll('.selection-badge');
                badges.forEach(badge => {
                    const tb = badge.parentNode;
                    if (tb) {
                        tb.classList.remove('custom-toolbar-wrapper');
                        tb.style.removeProperty('left');
                        tb.style.removeProperty('background-color');
                        
                        Array.from(tb.children).forEach(child => {
                            child.classList.remove('toolbar-btn-container', 'toolbar-hidden-container');
                        });
                    }
                    badge.remove();
                });
            }, 50);
            </script>
            """ + f"<!-- {__import__('time').time()} -->", height=0, width=0)

        from components.ui_utils import make_history_cards_white
        make_history_cards_white()
