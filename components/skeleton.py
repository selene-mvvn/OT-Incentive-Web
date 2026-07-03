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
