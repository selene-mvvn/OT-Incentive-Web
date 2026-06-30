import streamlit as st
from logic.history import get_history, remove_from_history
from logic.i18n import t

def make_container_white():
    import streamlit.components.v1 as components
    components.html("""
    <script>
        const parent = window.parent.document;
        const frames = parent.querySelectorAll('iframe');
        frames.forEach(frame => {
            if (frame.contentWindow === window) {
                let container = frame.closest('[data-testid="stVerticalBlock"]');
                if (container) {
                    container.style.backgroundColor = '#ffffff';
                    container.style.borderRadius = '12px';
                    container.style.boxShadow = '0 4px 15px rgba(0,0,0,0.05)';
                    container.style.padding = '20px';
                    container.style.border = '1px solid rgba(0,0,0,0.05)';
                }
            }
        });
    </script>
    """, height=0)

def make_history_cards_white():
    import streamlit.components.v1 as components
    components.html("""
    <script>
        const parent = window.parent.document;
        const markers = parent.querySelectorAll('.white-card-bg');
        markers.forEach(marker => {
            let horizontal = marker.closest('[data-testid="stHorizontalBlock"]');
            let outerContainer = null;
            if (horizontal) {
                let p = horizontal.parentElement;
                while (p && p.tagName !== 'BODY' && p.tagName !== 'HTML') {
                    let tid = p.getAttribute('data-testid');
                    if (tid === 'stVerticalBlockBorderWrapper') {
                        outerContainer = p;
                        break;
                    }
                    if (!tid && p.className.includes('st-emotion-cache')) {
                        outerContainer = p;
                        break;
                    }
                    p = p.parentElement;
                }
            }
            if (outerContainer) {
                outerContainer.style.backgroundColor = '#ffffff';
                outerContainer.style.setProperty('background-color', '#ffffff', 'important');
                outerContainer.classList.add('custom-history-card');
                if (outerContainer.querySelector('.timeline-marker')) {
                    outerContainer.classList.add('has-timeline-marker');
                }
                if (outerContainer.querySelector('.missing-marker')) {
                    outerContainer.classList.add('has-missing-marker');
                }
            }
        });

        // Hide the iframe containing this script to prevent the white bar at the bottom
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
    import streamlit.components.v1 as components
    components.html("""
    <script>
        const parent = window.parent.document;
        const frames = parent.querySelectorAll('iframe');
        frames.forEach(frame => {
            if (frame.contentWindow === window) {
                let expander = frame.closest('[data-testid="stExpander"]');
                if (expander) {
                    expander.style.backgroundColor = '#ffffff';
                    expander.style.border = '2px solid #00B0F0';
                    expander.style.borderRadius = '8px';
                    let summary = expander.querySelector('summary');
                    if (summary) {
                        summary.style.backgroundColor = '#00B0F0';
                        summary.style.color = '#ffffff';
                        summary.style.fontWeight = 'bold';
                        summary.style.borderRadius = '5px 5px 0 0';
                        let svg = summary.querySelector('svg');
                        if (svg) {
                            svg.style.fill = '#ffffff';
                            svg.style.color = '#ffffff';
                        }
                    }
                }
            }
        });
    </script>
    """, height=0)

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
            with st.popover(t(f"🗑️ Quản lý Lịch sử ({len(options)})", f"🗑️ 履歴管理 ({len(options)})"), use_container_width=False):
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
                            st.toast(t("Đã xóa các mục đã chọn ✅", "選択した項目を削除しました ✅"))
                            st.rerun()
                with b2:
                    if st.button(t("Xóa tất cả", "すべて削除"), key=f"del_all_{key}", type="primary", use_container_width=True):
                        remove_from_history(category, options)
                        st.toast(t("Đã xóa toàn bộ lịch sử ✅", "すべての履歴を削除しました ✅"))
                        st.rerun()
        
        # Return the selected value
        if selected == new_opt:
            return default_value if default_value else ""
        if selected == placeholder:
            return ""
        return selected
