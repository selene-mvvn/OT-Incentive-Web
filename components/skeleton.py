import streamlit as st
import time

def show_skeleton_loading(duration=0.6):
    """
    Displays a premium skeleton loading animation for a specified duration,
    then automatically clears itself.
    """
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
        <style>
        @keyframes skeleton-shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        .skeleton-box {
            background: linear-gradient(to right, #f6f7f8 8%, #edeef1 18%, #f6f7f8 33%);
            background-size: 2000px 100%;
            animation: skeleton-shimmer 2s linear infinite;
            border-radius: 8px;
        }
        .skeleton-wrapper {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid #eef2f5;
            width: 100%;
        }
        .skeleton-header-box {
            width: 30%; height: 35px; margin-bottom: 30px; border-radius: 8px;
        }
        .skeleton-grid {
            display: flex; gap: 20px; margin-bottom: 30px;
        }
        .skeleton-grid-item {
            flex: 1; height: 110px; border-radius: 12px;
        }
        .skeleton-row-box {
            width: 100%; height: 50px; margin-bottom: 15px; border-radius: 8px;
        }
        </style>
        <div id="skeleton-marker" class="skeleton-wrapper">
            <div class="skeleton-box skeleton-header-box"></div>
            <div class="skeleton-grid">
                <div class="skeleton-box skeleton-grid-item"></div>
                <div class="skeleton-box skeleton-grid-item"></div>
                <div class="skeleton-box skeleton-grid-item"></div>
            </div>
            <div class="skeleton-box skeleton-row-box"></div>
            <div class="skeleton-box skeleton-row-box"></div>
            <div class="skeleton-box skeleton-row-box"></div>
            <div class="skeleton-box skeleton-row-box"></div>
        </div>
        """, unsafe_allow_html=True)
        
        import streamlit.components.v1 as components
        components.html("""
        <script>
            const doc = window.parent.document;
            if (!doc.getElementById('skeleton-hider-script')) {
                let script = doc.createElement('script');
                script.id = 'skeleton-hider-script';
                script.innerHTML = `
                    const hideLoop = () => {
                        const m = document.getElementById('skeleton-marker');
                        if (!m) {
                            // Skeleton removed. Restore styles for reused elements
                            const hiddenElements = document.querySelectorAll('[data-skeleton-hidden="true"]');
                            hiddenElements.forEach(el => {
                                el.style.removeProperty('display');
                                el.style.removeProperty('opacity');
                                el.removeAttribute('data-skeleton-hidden');
                            });
                            
                            const s = document.getElementById('skeleton-hider-script');
                            if (s) s.remove();
                            return;
                        }
                        
                        let c = m;
                        while (c && (!c.getAttribute || c.getAttribute('data-testid') !== 'stElementContainer' || !c.parentElement || c.parentElement.getAttribute('data-testid') !== 'stVerticalBlock')) {
                            c = c.parentElement;
                        }
                        
                        if (c) {
                            let sib = c.nextElementSibling;
                            while (sib) {
                                sib.style.setProperty('display', 'none', 'important');
                                sib.style.setProperty('opacity', '0', 'important');
                                sib.setAttribute('data-skeleton-hidden', 'true');
                                sib = sib.nextElementSibling;
                            }
                        }
                        requestAnimationFrame(hideLoop);
                    };
                    requestAnimationFrame(hideLoop);
                `;
                doc.head.appendChild(script);
            }
        </script>
        """, height=0)
        
    time.sleep(duration)
    placeholder.empty()

def show_page_transition(duration=0.6):
    """
    Displays a full-screen transition overlay that fades out to reveal the new page.
    Uses pure CSS so it doesn't block the server or cause ghosting.
    """
    st.markdown(f"""
    <style>
    .page-transition-overlay {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #ffffff;
        z-index: 9999999;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        animation: fadeOutTransition {duration}s cubic-bezier(0.65, 0, 0.35, 1) forwards;
        animation-delay: 0.1s;
        pointer-events: none; /* Allow clicks through the overlay after it fades */
    }}
    @keyframes fadeOutTransition {{
        0% {{ opacity: 1; pointer-events: all; }}
        100% {{ opacity: 0; visibility: hidden; pointer-events: none; }}
    }}
    .transition-spinner {{
        width: 50px;
        height: 50px;
        border: 4px solid rgba(0, 176, 240, 0.2);
        border-top: 4px solid #00B0F0;
        border-radius: 50%;
        animation: spinTransition 0.8s linear infinite;
    }}
    @keyframes spinTransition {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    <div class="page-transition-overlay">
        <div class="transition-spinner"></div>
    </div>
    """, unsafe_allow_html=True)
