import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
with open(r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\action_history_ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# 1. Thay thế block JS đầu tiên
old_js_start = '            components.html("""'
old_js_end = '            """ + f"<!-- {len(selected_ids)} -->", height=0, width=0)'

pattern1 = re.compile(re.escape(old_js_start) + r'.*?' + re.escape(old_js_end), re.DOTALL)

new_js1 = '''            components.html("""
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
                        .custom-toolbar-wrapper button {
                            background-color: transparent !important; color: #0284c7 !important;
                            border: none !important; box-shadow: none !important; border-radius: 50% !important;
                            width: 32px !important; height: 32px !important; min-height: 32px !important;
                            margin: 0 !important; padding: 0 !important;
                            display: flex !important; justify-content: center !important; align-items: center !important;
                            transition: all 0.2s !important;
                        }
                        .custom-toolbar-wrapper button:hover { background-color: #ffffff !important; }
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
                        .custom-toolbar-wrapper div.stButton,
                        .custom-toolbar-wrapper div[data-testid="stButton"] {
                            margin: 0 !important; padding: 0 !important; height: 32px !important;
                            display: flex !important; align-items: center !important; justify-content: center !important;
                        }
                    `;
                    parentDoc.head.appendChild(style);
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
                        if (btns.length >= 1 && !btns[0].querySelector('svg')) {
                            btns[0].insertAdjacentHTML('beforeend', `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`);
                        }
                        if (btns.length >= 2 && !btns[1].querySelector('svg')) {
                            btns[1].insertAdjacentHTML('beforeend', `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`);
                        }
                        
                        if (window.frameElement) {
                            window.frameElement.style.display = 'none';
                            if (window.frameElement.parentElement) window.frameElement.parentElement.style.display = 'none';
                        }
                    }
                });
            }, 50);
            </script>
            """ + f"<!-- {len(selected_ids)} -->", height=0, width=0)'''

content = pattern1.sub(new_js1, content)

# 2. Thay thế cleanup script
old_cleanup_start = '            import streamlit.components.v1 as components'
old_cleanup_end = '            """, height=0, width=0)'

pattern2 = re.compile(r'            # CLEANUP SCRIPT:.*?' + re.escape(old_cleanup_end), re.DOTALL)

new_js2 = '''            # CLEANUP SCRIPT: Sử dụng CSS Class an toàn.
            # Thay vì thao tác trực tiếp lên inline styles (điều gây ra xung đột với Streamlit),
            # ta chỉ việc xóa bỏ class `.custom-toolbar-wrapper`, mọi CSS !important sẽ tự biến mất!
            import streamlit.components.v1 as components
            components.html("""
            <script>
            setTimeout(() => {
                const oldToolbars = window.parent.document.querySelectorAll('.custom-toolbar-wrapper');
                oldToolbars.forEach(tb => {
                    // Xóa class để ngắt toàn bộ CSS !important của Global Stylesheet!
                    tb.classList.remove('custom-toolbar-wrapper');
                    
                    // Xóa các thuộc tính inline duy nhất ta đã thêm (left, background)
                    tb.style.removeProperty('left');
                    tb.style.removeProperty('background-color');
                    
                    const badge = tb.querySelector('.selection-badge');
                    if (badge) badge.remove();
                    
                    Array.from(tb.children).forEach(child => {
                        child.classList.remove('toolbar-btn-container', 'toolbar-hidden-container');
                    });
                });
            }, 50);
            </script>
            """, height=0, width=0)'''

content = pattern2.sub(new_js2, content)

with open(r'C:\Users\kifukouza06\Desktop\Website OT-Incentive\OT-Incentive-Web\components\action_history_ui.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done replacement!")
