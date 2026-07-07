import streamlit as st
from logic.history import get_history, remove_from_history
from logic.i18n import t

def make_container_white():
    st.markdown("""
        <div class='custom-white-container-marker' style='display: none;'></div>
        <style>
            [data-testid="stVerticalBlock"]:has(> .element-container .custom-white-container-marker) {
                background-color: #ffffff;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                padding: 20px;
                border: 1px solid rgba(0,0,0,0.05);
            }
        </style>
    """, unsafe_allow_html=True)

def make_history_cards_white():
    import streamlit.components.v1 as components
    components.html("""
    <script>
        const parent = window.parent.document;
        
        function styleCards(container) {
            let cards = container.querySelectorAll('[data-testid="stVerticalBlockBorderWrapper"]');
            cards.forEach(card => {
                if (!card.classList.contains('custom-history-card')) {
                    card.classList.add('custom-history-card');
                    card.style.backgroundColor = '#ffffff';
                    card.style.border = '1px solid #e2e8f0';
                    card.style.borderRadius = '10px';
                    card.style.boxShadow = '0 2px 4px rgba(0,0,0,0.02)';
                    
                    let timelineMarker = card.querySelector('.timeline-marker');
                    let missingMarker = card.querySelector('.missing-marker');
                    
                    if (timelineMarker) {
                        card.classList.add('has-timeline-marker');
                        let color = timelineMarker.getAttribute('data-color') || '#00B0F0';
                        card.style.setProperty('--timeline-color', color);
                        card.style.setProperty('--timeline-shadow', `0 0 0 4px ${color}26`); // 15% opacity hex
                    }
                    if (missingMarker) {
                        card.classList.add('has-missing-marker');
                        card.style.setProperty('--timeline-color', '#e74c3c');
                        card.style.setProperty('--timeline-shadow', `0 0 0 4px rgba(231, 76, 60, 0.15)`);
                    }
                }
            });
        }

        const frames = parent.querySelectorAll('iframe');
        frames.forEach(frame => {
            if (frame.contentWindow === window) {
                let container = frame.closest('[data-testid="stVerticalBlock"]');
                if (container) {
                    styleCards(container);
                    const observer = new parent.MutationObserver((mutations) => {
                        styleCards(container);
                    });
                    observer.observe(container, { childList: true, subtree: true });
                }
            }
        });

        if (window.frameElement) {
            window.frameElement.style.display = 'none';
            if (window.frameElement.parentElement) {
                window.frameElement.parentElement.style.display = 'none';
                window.frameElement.parentElement.style.height = '0px';
                window.frameElement.parentElement.style.margin = '0px';
                window.frameElement.parentElement.style.padding = '0px';
            }
        }
    </script>
    """, height=0)

def make_expander_blue():
    st.markdown("""
        <div class='custom-expander-marker' style='display: none;'></div>
        <style>
            [data-testid="stExpander"]:has(.custom-expander-marker) {
                background-color: #ffffff;
                border: 2px solid #00B0F0;
                border-radius: 8px;
            }
            [data-testid="stExpander"]:has(.custom-expander-marker) summary {
                background-color: #00B0F0;
                color: #ffffff;
                font-weight: bold;
                font-size: 15.5px !important;
                border-radius: 5px 5px 0 0;
            }
            [data-testid="stExpander"]:has(.custom-expander-marker) summary p,
            [data-testid="stExpander"]:has(.custom-expander-marker) summary span {
                font-size: 15.5px !important;
                color: #ffffff !important;
                font-weight: bold !important;
            }
            [data-testid="stExpander"]:has(.custom-expander-marker) summary svg {
                fill: #ffffff;
                color: #ffffff;
            }
            [data-testid="stExpander"]:has(.custom-expander-marker) [data-testid="stExpanderDetails"] {
                padding-top: 0.5rem !important;
                padding-bottom: 1rem !important;
            }
            [data-testid="stExpander"]:has(.custom-expander-marker) .element-container:has(.custom-expander-marker),
            [data-testid="stExpander"]:has(.custom-expander-marker) [data-testid="stVerticalBlock"] > div:has(.custom-expander-marker) {
                position: absolute !important;
                height: 0 !important;
                width: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
            }
        </style>
    """, unsafe_allow_html=True)

def _switch_to_select(mode_key, sel_key):
    """Callback to switch back to select mode."""
    st.session_state[mode_key] = "select"
    # Remove stale selectbox value
    st.session_state.pop(sel_key, None)

def _on_selectbox_change(mode_key, sel_key, new_opt):
    """Callback when selectbox value changes."""
    if st.session_state.get(sel_key) == new_opt:
        st.session_state[mode_key] = "text"

def text_input_with_history(label, key, category, default_value="", custom_options=None):
    """
    Shows either a selectbox (history mode) or a text_input (new input mode) — 
    never both at the same time, always on a single line.
    """
    if custom_options is not None:
        options = custom_options
    else:
        options = get_history(category)
    new_opt = t("➕ Nhập mới...", "➕ 新規入力...")
    
    lang = st.session_state.get('lang', 'VN')
    if lang == 'VN':
        placeholder = f"--- Chọn {label.lower()} ---"
    else:
        placeholder = f"--- {label}を選択 ---"
    
    mode_key = f"mode_{key}"
    sel_key = f"sel_{key}"
    
    # --- AUTO-FILL OVERRIDE LOGIC ---
    last_default_key = f"last_default_{key}"
    if last_default_key not in st.session_state:
        st.session_state[last_default_key] = default_value
        
    if default_value != st.session_state[last_default_key]:
        # The parent component dynamically changed the default value (e.g., auto-fill triggered)
        st.session_state[last_default_key] = default_value
        st.session_state[sel_key] = default_value if default_value else placeholder
        st.session_state[f"txt_{key}"] = default_value if default_value else ""
        if len(options) > 0:
            st.session_state[mode_key] = "select"
        else:
            st.session_state[mode_key] = "text"
    
    if len(options) == 0:
        st.session_state[mode_key] = "text"
    elif mode_key not in st.session_state:
        st.session_state[mode_key] = "select"
    
    if st.session_state[mode_key] == "text":
        # TEXT INPUT MODE
        val_to_show = default_value if default_value not in options else ""
        result = st.text_input(label, value=val_to_show, key=f"txt_{key}")
        if len(options) > 0:
            st.button(
                t("↩ Chọn từ lịch sử", "↩ 履歴から選択"), 
                key=f"back_{key}", 
                type="secondary",
                on_click=_switch_to_select,
                args=(mode_key, sel_key)
            )
        return result
    else:
        # SELECTBOX MODE
        all_options = [placeholder, new_opt] + options
        if default_value and default_value not in options:
            all_options.append(default_value)
        default_index = 0
        if default_value in all_options:
            default_index = all_options.index(default_value)
        
        selected = st.selectbox(
            label,
            all_options,
            index=default_index,
            key=sel_key,
            on_change=_on_selectbox_change,
            args=(mode_key, sel_key, new_opt)
        )
        
        # Popover for deleting history
        if len(options) > 0:
            with st.popover(t(f":material/delete: Quản lý Lịch sử ({len(options)})", f":material/delete: 履歴管理 ({len(options)})"), use_container_width=False):
                st.markdown("""
                <style>
                /* Elevate the z-index of all baseweb popovers that contain a listbox (multiselect/selectbox dropdowns) */
                div[data-baseweb="popover"] {
                    z-index: 9999999 !important;
                }
                /* Optional: ensure the popover body doesn't clip if rendering inside */
                div[data-testid="stPopoverBody"] {
                    overflow: visible !important;
                }
                </style>
                """, unsafe_allow_html=True)
                st.caption(t("Chọn nhiều mục để xóa hoặc xóa tất cả.", "複数選択して削除、またはすべて削除。"))
                
                items_to_delete = st.multiselect(
                    t("Chọn mục cần xóa", "削除する項目を選択"),
                    options=options,
                    key=f"ms_{key}",
                    label_visibility="collapsed",
                    placeholder=t("Chọn mục để xóa...", "削除する項目を選択...")
                )
                
                b1, b2 = st.columns(2)
                with b1:
                    if st.button(t("Xóa đã chọn", "選択項目を削除"), key=f"del_sel_{key}", use_container_width=True):
                        if items_to_delete:
                            remove_from_history(category, items_to_delete)
                            st.session_state['pending_toast'] = t("Đã xóa các mục đã chọn", "選択した項目を削除しました")
                            st.rerun()
                with b2:
                    if st.button(t("Xóa tất cả", "すべて削除"), key=f"del_all_{key}", type="primary", use_container_width=True):
                        remove_from_history(category, options)
                        st.session_state['pending_toast'] = t("Đã xóa toàn bộ lịch sử", "すべての履歴を削除しました")
                        st.rerun()
        
        # Return the selected value
        if selected == new_opt:
            return default_value if default_value else ""
        if selected == placeholder:
            return ""
        return selected

def render_empty_state(text, subtitle=None, icon="inbox", height=200):
    import streamlit as st
    subtitle_html = f"<div style='font-size: 13px; color: #94a3b8; margin-top: 5px; text-align: center;'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
        </style>
        <div style='
            height: {height}px; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            background: #f8fafc; 
            border: 1px dashed #cbd5e1; 
            border-radius: 12px; 
            color: #94a3b8; 
            margin-bottom: 20px;
            padding: 20px;
        '>
            <span class="material-symbols-rounded" style='font-size: 48px; color: #00a8e8; margin-bottom: 10px;'>{icon}</span>
            <div style='font-size: 15px; font-weight: 500; color: #64748b; text-align: center;'>{text}</div>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)

