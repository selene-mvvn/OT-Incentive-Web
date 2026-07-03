import streamlit as st
import time

def show_skeleton_loading(duration=0.6):
    """
    Displays a premium skeleton loading animation for a specified duration,
    then automatically clears itself.
    """
    placeholder = st.empty()
    placeholder.markdown("""
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
    
    /* MAGIC TRICK: Hide all old elements that get pushed down by Streamlit during transition */
    div[data-testid="stElementContainer"]:has(.skeleton-wrapper) ~ div {
        display: none !important;
        opacity: 0 !important;
    }
    </style>
    <div class="skeleton-wrapper">
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
    
    time.sleep(duration)
    placeholder.empty()

def show_page_transition(duration=0.6):
    """
    Displays a full-screen transition overlay for a specified duration,
    then automatically clears itself. Used for page-to-page navigation.
    """
    ph = st.empty()
    ph.markdown("""
    <style>
    .page-transition-overlay {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #ffffff;
        z-index: 9999999;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        animation: fadeOutTransition 0.6s cubic-bezier(0.65, 0, 0.35, 1) forwards;
        animation-delay: 0.1s;
    }
    @keyframes fadeOutTransition {
        0% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; }
    }
    .transition-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(0, 176, 240, 0.2);
        border-top: 4px solid #00B0F0;
        border-radius: 50%;
        animation: spinTransition 0.8s linear infinite;
    }
    @keyframes spinTransition {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    /* Hide old elements in main block container to prevent pushing down */
    div[data-testid="stElementContainer"]:has(.page-transition-overlay) ~ div {
        display: none !important;
        opacity: 0 !important;
    }
    </style>
    <div class="page-transition-overlay">
        <div class="transition-spinner"></div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(duration)
    ph.empty()
