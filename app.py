import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import urllib.request
import io
import os
import base64
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. Page Configuration & Modern Light SaaS Theme CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="학교시설 비구조요소 내진보강 기반 마련 연구(1차) 계측 대시보드",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def render_html(html_str):
    """
    Streamlit CommonMark가 4칸 들여쓰기를 <pre><code> 코드블록으로 오인하는 현상을
    100% 방지하기 위해 모든 줄의 들여쓰기를 제거하고 인라인 HTML로 렌더링함
    """
    cleaned = "".join([line.strip() for line in html_str.splitlines() if line.strip()])
    st.markdown(cleaned, unsafe_allow_html=True)


css_styles = """
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    .stApp {
        background: linear-gradient(135deg, #f3f5fc 0%, #edf0f8 100%);
        color: #1e293b;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .main .block-container {
        padding: 0.5rem 1.2rem 1.5rem 1.2rem;
        max-width: 1920px;
    }

    /* Top Navigation Header Container */
    .brand-logo-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.98rem;
        font-weight: 800;
        color: #1e293b;
    }
    .brand-icon {
        width: 32px;
        height: 32px;
        min-width: 32px;
        border-radius: 10px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
    }

    /* Modern Nav Pills Styling (LoopAI Style) */
    div[data-testid="stPills"] {
        display: flex;
        justify-content: center;
        background: #f1f5f9;
        padding: 3px 6px;
        border-radius: 9999px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    div[data-testid="stPills"] button {
        border-radius: 9999px !important;
        font-size: 0.80rem !important;
        font-weight: 600 !important;
        padding: 5px 16px !important;
        border: none !important;
        background: transparent !important;
        color: #64748b !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stPills"] button:hover {
        color: #1e293b !important;
        background: rgba(255, 255, 255, 0.7) !important;
    }
    div[data-testid="stPills"] button[aria-selected="true"],
    div[data-testid="stPills"] button[data-selected="true"] {
        background: #ffffff !important;
        color: #4f46e5 !important;
        font-weight: 800 !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15) !important;
    }

    /* Modern Rounded SaaS Card */
    .saas-card {
        background: #ffffff;
        border: 1px solid #eef2f7;
        border-radius: 16px;
        padding: 12px 14px;
        box-shadow: 0 3px 15px rgba(99, 102, 241, 0.03);
        margin-bottom: 10px;
    }
    .saas-card-title {
        font-size: 0.80rem;
        font-weight: 700;
        color: #64748b;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2px;
    }
    .saas-card-num {
        font-size: 1.50rem;
        font-weight: 900;
        color: #0f172a;
        letter-spacing: -0.5px;
        margin: 2px 0;
    }
    .saas-card-sub {
        font-size: 0.70rem;
        color: #94a3b8;
        font-weight: 500;
    }

    /* Pastel Badges */
    .badge-mint {
        background: #dcfce7;
        color: #15803d;
        font-size: 0.70rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .badge-violet {
        background: #ede9fe;
        color: #6d28d9;
        font-size: 0.70rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .badge-rose {
        background: #ffe4e6;
        color: #be123c;
        font-size: 0.70rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .badge-amber {
        background: #fef3c7;
        color: #b45309;
        font-size: 0.70rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
    }

    /* Section Header */
    .sec-header {
        font-size: 0.88rem;
        font-weight: 800;
        color: #0f172a;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
    }

    /* Step Pipeline Cards */
    .step-card {
        background: #f8fafc;
        border: 1px solid #eef2f7;
        border-radius: 12px;
        padding: 9px 12px;
        margin-bottom: 7px;
        transition: all 0.2s ease;
    }
    .step-card:hover {
        background: #ffffff;
        border-color: #cbd5e1;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.05);
    }
    .step-badge {
        font-size: 0.65rem;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 6px;
        display: inline-block;
    }
    .step-b1 { background: #ede9fe; color: #6366f1; }
    .step-b2 { background: #dcfce7; color: #15803d; }
    .step-b3 { background: #f3e8ff; color: #7e22ce; }

    .step-prog-track {
        width: 100%;
        height: 5px;
        background: #e2e8f0;
        border-radius: 9999px;
        overflow: hidden;
        margin-top: 5px;
    }
    .step-prog-bar {
        height: 100%;
        border-radius: 9999px;
    }

    /* Photo Cards & Clickable Lightbox */
    .photo-saas-card {
        background: #ffffff;
        border: 1px solid #eef2f7;
        border-radius: 12px;
        padding: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        cursor: pointer;
        display: block;
        text-decoration: none;
        color: inherit;
    }
    .photo-saas-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.12);
        border-color: #cbd5e1;
    }
    .photo-saas-img {
        width: 100%;
        height: 68px;
        object-fit: cover;
        border-radius: 8px;
        display: block;
    }
    .photo-saas-name {
        font-size: 0.68rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* CSS Lightbox Modal for Photo Enlargement */
    .img-lightbox-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(15, 23, 42, 0.80);
        backdrop-filter: blur(5px);
        z-index: 999999;
        display: none;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    .img-lightbox-modal:target {
        display: flex;
        opacity: 1;
    }
    .img-lightbox-box {
        position: relative;
        background: #ffffff;
        padding: 16px 20px 20px 20px;
        border-radius: 18px;
        max-width: 820px;
        width: 90%;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
        text-align: center;
        animation: lightboxPop 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes lightboxPop {
        from { transform: scale(0.92); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    .img-lightbox-box img {
        max-height: 72vh;
        max-width: 100%;
        border-radius: 12px;
        object-fit: contain;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .img-lightbox-close {
        position: absolute;
        top: 10px;
        right: 14px;
        font-size: 26px;
        font-weight: 700;
        color: #64748b;
        text-decoration: none;
        line-height: 1;
        padding: 4px 10px;
        border-radius: 8px;
        background: #f1f5f9;
        transition: all 0.15s ease;
    }
    .img-lightbox-close:hover {
        color: #0f172a;
        background: #e2e8f0;
    }
    .img-lightbox-bg-close {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        cursor: default;
    }
    
    /* Button Style */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 4px 14px;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
        color: white;
    }

    /* High-Contrast Widget Labels & Filter Visibility (Dark & Bold) */
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] span,
    .stSelectbox label,
    .stTextInput label,
    .stMultiSelect label,
    label[data-testid="stWidgetLabel"] {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 0.82rem !important;
        letter-spacing: -0.2px !important;
        margin-bottom: 2px !important;
    }
    
    /* Expander Header Visibility */
    div[data-testid="stExpander"] details summary span,
    div[data-testid="stExpander"] details summary p {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 0.88rem !important;
    }
</style>
"""
render_html(css_styles)


# -----------------------------------------------------------------------------
# 2. Real-Time Google Sheet Data Loader
# -----------------------------------------------------------------------------
SHEET_ID = "19gDIXWp4Ih03K2aLuN8W8k1IFSZQx060--0L9fJxNKA"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=60)
def load_live_google_sheet():
    try:
        req = urllib.request.Request(CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw_text = resp.read().decode('utf-8')
            df_raw = pd.read_csv(io.StringIO(raw_text), skiprows=1)
            with open("google_sheet_cache.csv", "w", encoding="utf-8") as f:
                f.write(raw_text)
    except Exception:
        if os.path.exists("google_sheet_cache.csv"):
            df_raw = pd.read_csv("google_sheet_cache.csv", skiprows=1)
        elif os.path.exists("google_sheet_data.csv"):
            df_raw = pd.read_csv("google_sheet_data.csv", skiprows=1)
        else:
            return pd.DataFrame()

    cols = [
        '대상주차', '시설물번호', '건물코드', '교육청', '지원청', '학교명', '시설상세명', '시설구분',
        '층수', '지붕구조', '내진설계적용', '내진상태', '성능평가여부', '성능평가결과', '성능평가년도',
        '보강설계여부', '보강설계재평가', '보강공사여부', '성능확보여부1', '성능확보여부2',
        '모델링대상', '보강안모델링', '담당자',
        'Step1_1차모델링', 'Step2_계측완료', 'Step3_캘리브레이션', 'Step4_최종검증'
    ]
    df = df_raw.iloc[:, :len(cols)].copy()
    df.columns = cols

    for c in ['모델링대상', '보강안모델링', 'Step1_1차모델링', 'Step2_계측완료', 'Step3_캘리브레이션', 'Step4_최종검증']:
        df[c] = df[c].astype(str).str.strip().str.upper() == 'TRUE'

    def clean_floor(v):
        v = str(v).strip()
        if v in ['1', '1.0', '1층', '2', '2.0', '2층', '2층 이하', '2층이하']: return '2층 이하'
        if v in ['3', '3.0', '3층']: return '3층'
        if v in ['4', '4.0', '4층']: return '4층'
        if v in ['5', '5.0', '5층']: return '5층'
        return '-' if v in ['', 'nan', '-'] else str(v)

    def clean_roof(v):
        v = str(v).strip()
        if '철골' in v: return '일반철골'
        if '트러스' in v: return '트러스'
        if '스페이스' in v: return '스페이스프레임'
        if '돔' in v or '아치' in v: return '돔·아치'
        return '-' if v in ['', 'nan', '-'] else str(v)

    df['층수'] = df['층수'].apply(clean_floor)
    df['지붕구조'] = df['지붕구조'].apply(clean_roof)

    for c in ['대상주차', '교육청', '지원청', '학교명', '시설상세명', '시설구분', '내진상태', '담당자']:
        df[c] = df[c].fillna('-').astype(str).str.strip()

    return df

df_sheet = load_live_google_sheet()


# -----------------------------------------------------------------------------
# 3. Base64 Image Loader Helper
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)

def get_base64_image(filename):
    p = os.path.join(BASE_DIR, filename)
    if os.path.exists(p):
        with open(p, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"
    return "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=400"


# -----------------------------------------------------------------------------
# 4. Top Interactive Navigation Bar (LoopAI Style)
# -----------------------------------------------------------------------------
cur_time = datetime.now().strftime("%H:%M:%S")

col_brand, col_nav, col_sync = st.columns([2.3, 1.8, 0.9])

with col_brand:
    brand_html = f"""
    <div style="display:flex; align-items:center; gap:8px; height:42px;">
        <div class="brand-icon">⚡</div>
        <div>
            <div style="font-weight:800; font-size:0.95rem; color:#0f172a; letter-spacing:-0.4px; line-height:1.2;">
                학교시설 비구조요소 내진보강 기반 마련 연구(1차) 계측 대시보드
            </div>
        </div>
    </div>
    """
    render_html(brand_html)

with col_nav:
    selected_tab = st.pills(
        "Navigation",
        ["종합 Overview", "교사동·체육관 통계", "주차별 로드맵", "실시간 데이터 시트"],
        default="종합 Overview",
        selection_mode="single",
        required=True,
        label_visibility="collapsed",
        key="main_navbar_tab"
    )

with col_sync:
    c_live, c_btn = st.columns([1.1, 0.9])
    with c_live:
        render_html(f"""
        <div style="display:flex; align-items:center; justify-content:center; height:42px;">
            <span class="badge-mint" style="padding:4px 10px; font-size:0.70rem; font-weight:700;">🟢 Live ({cur_time})</span>
        </div>
        """)
    with c_btn:
        if st.button("🔄 동기화", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


# -----------------------------------------------------------------------------
# 5. Core Metric KPI Calculations (Strictly based on 모델링대상 == True)
# -----------------------------------------------------------------------------
df_target = df_sheet[df_sheet['모델링대상']].copy()
total_target = len(df_target)

sch_cnt = (df_target['시설구분'] == '교사동').sum()
gym_cnt = (df_target['시설구분'] == '체육관').sum()
etc_cnt = len(df_target) - sch_cnt - gym_cnt

step1_cnt = int(df_target['Step1_1차모델링'].sum())
step2_cnt = int(df_target['Step2_계측완료'].sum())
step3_cnt = int(df_target['Step3_캘리브레이션'].sum())

s1_rate = (step1_cnt / total_target * 100) if total_target > 0 else 0
s2_rate = (step2_cnt / total_target * 100) if total_target > 0 else 0
s3_rate = (step3_cnt / total_target * 100) if total_target > 0 else 0


# =============================================================================
# TAB 1: 종합 Overview
# =============================================================================
if selected_tab == "종합 Overview":
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        etc_label = f" · 기타 {etc_cnt}" if etc_cnt > 0 else ""
        c1_html = f"""
        <div class="saas-card">
            <div class="saas-card-title">
                <span>총 분석 대상 시설 (모델링 대상)</span>
                <span class="badge-mint">{total_target}개소</span>
            </div>
            <div class="saas-card-num">{total_target} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">개소</span></div>
            <div class="saas-card-sub">교사동 {sch_cnt} · 체육관 {gym_cnt}{etc_label}</div>
        </div>
        """
        render_html(c1_html)

    with k2:
        c2_html = f"""
        <div class="saas-card">
            <div class="saas-card-title">
                <span>Step 1 1차 3D 모델링</span>
                <span class="badge-violet">+{step1_cnt} 완료</span>
            </div>
            <div class="saas-card-num" style="color:#6366f1;">{step1_cnt} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">/ {total_target}</span></div>
            <div class="saas-card-sub">진척률 {s1_rate:.1f}% (잔여 {total_target - step1_cnt}개소)</div>
        </div>
        """
        render_html(c2_html)

    with k3:
        c3_html = f"""
        <div class="saas-card">
            <div class="saas-card-title">
                <span>Step 2 현장 계측 분석 완료</span>
                <span class="badge-mint">+{step2_cnt} 완료</span>
            </div>
            <div class="saas-card-num" style="color:#10b981;">{step2_cnt} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">/ {total_target}</span></div>
            <div class="saas-card-sub">진척률 {s2_rate:.1f}% (잔여 {total_target - step2_cnt}개소)</div>
        </div>
        """
        render_html(c3_html)

    with k4:
        c4_html = f"""
        <div class="saas-card">
            <div class="saas-card-title">
                <span>Step 3 모델 캘리브레이션</span>
                <span class="badge-violet">+{step3_cnt} 착수</span>
            </div>
            <div class="saas-card-num" style="color:#8b5cf6;">{step3_cnt} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">/ {total_target}</span></div>
            <div class="saas-card-sub">진척률 {s3_rate:.1f}% (계측 분석 연계 보정)</div>
        </div>
        """
        render_html(c4_html)

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.75, 1.25])

    # LEFT PANEL (Analytics, Cumulative Charts, Photo Gallery)
    with col_left:
        w_head = f"""
        <div class="saas-card">
            <div class="sec-header">
                <span>📊 주차별 배정 학교 작업 현황</span>
                <div style="font-size:0.75rem; color:#64748b;">주차별 모델링·계측 분석 실적</div>
            </div>
        """
        render_html(w_head)

        df_week = df_target[df_target['대상주차'] != '-'].copy()
        week_order = sorted(df_week['대상주차'].unique())
        week_stat = []
        for w in week_order:
            sub = df_week[df_week['대상주차'] == w]
            week_stat.append({
                "주차": w,
                "총시설": len(sub),
                "계측분석완료": sub['Step2_계측완료'].sum(),
                "모델링완료": sub['Step1_1차모델링'].sum()
            })
        df_wstat = pd.DataFrame(week_stat)

        fig_w = go.Figure()
        fig_w.add_trace(go.Bar(
            x=df_wstat['주차'], y=df_wstat['총시설'],
            name=f"배정 시설 ({total_target}개 대상)", marker_color="#e2e8f0"
        ))
        fig_w.add_trace(go.Bar(
            x=df_wstat['주차'], y=df_wstat['계측분석완료'],
            name="Step 2 현장 계측 분석 완료", marker_color="#34d399"
        ))
        fig_w.add_trace(go.Bar(
            x=df_wstat['주차'], y=df_wstat['모델링완료'],
            name="Step 1 1차 모델링 완료", marker_color="#6366f1"
        ))

        fig_w.update_layout(
            barmode="group",
            height=175,
            margin=dict(l=5, r=5, t=10, b=5),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#334155", size=9.5, family="Pretendard"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9.5, color="#1e293b")),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", linecolor="#cbd5e1", tickfont=dict(color="#475569")),
            xaxis=dict(showgrid=False, linecolor="#cbd5e1", tickfont=dict(size=9.5, color="#334155"))
        )
        st.plotly_chart(fig_w, use_container_width=True)
        render_html("</div>")

        # Cumulative Bar Charts for 교사동 & 체육관 (Dynamically aggregated from live data)
        c_b1, c_b2 = st.columns(2)
        
        with c_b1:
            cb1_head = f"""
            <div class="saas-card">
                <div class="sec-header">
                    <span>🏢 교사동 층수별 현황</span>
                    <span class="badge-violet">총 {sch_cnt}동</span>
                </div>
            """
            render_html(cb1_head)
            
            df_sch = df_target[df_target['시설구분'] == '교사동']
            sch_cats = ["2층 이하", "3층", "4층", "5층"]
            sch_m = []
            sch_f = []
            for cat in sch_cats:
                sub = df_sch[df_sch['층수'] == cat]
                tot = len(sub)
                m = int(sub['Step2_계측완료'].sum())
                sch_m.append(m)
                sch_f.append(tot - m)
            sch_tot = [m + f for m, f in zip(sch_m, sch_f)]
            sch_m_tot = sum(sch_m)
            sch_f_tot = sum(sch_f)

            fig_sb1 = go.Figure()
            fig_sb1.add_trace(go.Bar(x=sch_cats, y=sch_m, name=f"계측 분석 완료 ({sch_m_tot})", marker_color="#6366f1", text=sch_m, textposition="inside"))
            fig_sb1.add_trace(go.Bar(x=sch_cats, y=sch_f, name=f"향후계획 ({sch_f_tot})", marker_color="#c7d2fe", text=sch_f, textposition="inside"))
            for cat, tot in zip(sch_cats, sch_tot):
                fig_sb1.add_annotation(x=cat, y=tot, text=f"<b>{tot}</b>", showarrow=False, yshift=8, font=dict(color="#1e293b", size=10.5))

            fig_sb1.update_layout(
                barmode="stack",
                height=140,
                margin=dict(l=5, r=5, t=10, b=5),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(color="#334155", size=9, family="Pretendard"),
                showlegend=False,
                yaxis=dict(range=[0, max(sch_tot)*1.25 if max(sch_tot) > 0 else 10], showgrid=True, gridcolor="#f1f5f9", linecolor="#cbd5e1"),
                xaxis=dict(showgrid=False, linecolor="#cbd5e1", tickfont=dict(color="#1e293b", size=9.5))
            )
            st.plotly_chart(fig_sb1, use_container_width=True)
            render_html("</div>")

        with c_b2:
            cb2_head = f"""
            <div class="saas-card">
                <div class="sec-header">
                    <span>🏟️ 체육관 지붕구조별 현황</span>
                    <span class="badge-mint">총 {gym_cnt}동</span>
                </div>
            """
            render_html(cb2_head)

            df_gym = df_target[df_target['시설구분'] == '체육관']
            gym_cats = ["일반철골", "트러스", "스페이스프레임", "돔·아치"]
            gym_m = []
            gym_f = []
            for cat in gym_cats:
                sub = df_gym[df_gym['지붕구조'] == cat]
                tot = len(sub)
                m = int(sub['Step2_계측완료'].sum())
                gym_m.append(m)
                gym_f.append(tot - m)
            gym_tot = [m + f for m, f in zip(gym_m, gym_f)]
            gym_m_tot = sum(gym_m)
            gym_f_tot = sum(gym_f)

            fig_sb2 = go.Figure()
            fig_sb2.add_trace(go.Bar(x=gym_cats, y=gym_m, name=f"계측 분석 완료 ({gym_m_tot})", marker_color="#10b981", text=gym_m, textposition="inside"))
            fig_sb2.add_trace(go.Bar(x=gym_cats, y=gym_f, name=f"향후계획 ({gym_f_tot})", marker_color="#a7f3d0", text=gym_f, textposition="inside"))
            for cat, tot in zip(gym_cats, gym_tot):
                fig_sb2.add_annotation(x=cat, y=tot, text=f"<b>{tot}</b>", showarrow=False, yshift=8, font=dict(color="#1e293b", size=10.5))

            fig_sb2.update_layout(
                barmode="stack",
                height=140,
                margin=dict(l=5, r=5, t=10, b=5),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(color="#334155", size=9, family="Pretendard"),
                showlegend=False,
                yaxis=dict(range=[0, max(gym_tot)*1.25 if max(gym_tot) > 0 else 10], showgrid=True, gridcolor="#f1f5f9", linecolor="#cbd5e1"),
                xaxis=dict(showgrid=False, linecolor="#cbd5e1", tickfont=dict(color="#1e293b", size=9.5))
            )
            st.plotly_chart(fig_sb2, use_container_width=True)
            render_html("</div>")

        # Photo Cards with Click-to-Enlarge Modal (8 Representatives)
        photos_head = """
        <div class="saas-card">
            <div class="sec-header">
                <span>🖼️ 대표 학교 시설 전경 (교사동 4종 · 체육관 4종)</span>
                <div style="font-size:0.75rem; color:#6366f1; font-weight:600;">🔍 사진 클릭 시 원본 확대</div>
            </div>
        """
        render_html(photos_head)

        photos = [
            {"id": "p1", "type": "2층 이하", "name": "영동초 후관", "badge_bg": "#6366f1", "file": "2층_영동초등학교 후관교사.jpg", "fullname": "영동초등학교 후관교사 (2층 이하)"},
            {"id": "p2", "type": "3층 교사", "name": "서대전초 본관", "badge_bg": "#6366f1", "file": "3층_서대전초등학교 본관교사.jpg", "fullname": "서대전초등학교 본관교사 (3층)"},
            {"id": "p3", "type": "4층 교사", "name": "성남수정초 본관", "badge_bg": "#6366f1", "file": "4층_성남수정초등학교 본관교사.jpg", "fullname": "성남수정초등학교 본관교사 (4층)"},
            {"id": "p4", "type": "5층 교사", "name": "동두천중앙고", "badge_bg": "#6366f1", "file": "5층_동두천중앙고등학교 본관교사.jpg", "fullname": "동두천중앙고등학교 본관교사 (5층)"},
            {"id": "p5", "type": "일반철골", "name": "진천상업고", "badge_bg": "#10b981", "file": "일반철골_진천상업고등학교 체육관.jpg", "fullname": "진천상업고등학교 체육관 (일반철골)"},
            {"id": "p6", "type": "트러스", "name": "서대전초 체육", "badge_bg": "#10b981", "file": "트러스_서대전초등학교 체육관.jpg", "fullname": "서대전초등학교 체육관 (트러스)"},
            {"id": "p7", "type": "스페이스", "name": "안성고 체육관", "badge_bg": "#10b981", "file": "스페이스프레임_안성고등학교 체육관.jpg", "fullname": "안성고등학교 체육관 (스페이스프레임)"},
            {"id": "p8", "type": "돔·아치", "name": "의정부여중", "badge_bg": "#10b981", "file": "돔아치_의정부여자중학교 체육관.jpg", "fullname": "의정부여자중학교 체육관 (돔·아치)"}
        ]

        p_cols = st.columns(8)
        modal_htmls = []
        for col, item in zip(p_cols, photos):
            img_data = get_base64_image(item["file"])
            with col:
                p_html = f"""
                <a href="#{item['id']}" class="photo-saas-card" title="클릭하여 크게 보기">
                    <div style="position:relative;">
                        <img src="{img_data}" class="photo-saas-img">
                        <span style="position:absolute; top:3px; left:3px; background:{item['badge_bg']}; color:white; font-size:0.60rem; font-weight:bold; padding:1px 5px; border-radius:4px;">{item['type']}</span>
                    </div>
                    <div class="photo-saas-name">{item['name']}</div>
                </a>
                """
                render_html(p_html)

            # Lightbox Modal Markup
            modal_html = f"""
            <div id="{item['id']}" class="img-lightbox-modal">
                <a href="#close" class="img-lightbox-bg-close"></a>
                <div class="img-lightbox-box">
                    <a href="#close" class="img-lightbox-close" title="닫기">&times;</a>
                    <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:12px; display:flex; align-items:center; justify-content:center; gap:8px;">
                        <span style="background:{item['badge_bg']}; color:white; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:6px;">{item['type']}</span>
                        <span>{item['fullname']}</span>
                    </div>
                    <img src="{img_data}" alt="{item['fullname']}">
                    <div style="margin-top:10px; font-size:0.75rem; color:#64748b;">
                        현장 가속도 진동 계측 및 3D 모델링 표준 표본 시설
                    </div>
                </div>
            </div>
            """
            modal_htmls.append(modal_html)

        render_html("</div>" + "".join(modal_htmls))

    # RIGHT PANEL (계측 및 모델링 현황, 13 Regional Offices, AI Control Helper)
    with col_right:
        p1 = (step1_cnt / total_target * 100) if total_target > 0 else 0
        p2 = (step2_cnt / total_target * 100) if total_target > 0 else 0
        p3 = (step3_cnt / total_target * 100) if total_target > 0 else 0

        step_html = f"""
        <div class="saas-card" style="margin-bottom:10px;">
            <div class="sec-header">
                <div style="display:flex; align-items:center; gap:6px;">
                    <span style="color:#6366f1; font-size:1.0rem;">⚡</span>
                    <span style="font-size:0.88rem; font-weight:800; color:#0f172a;">계측 및 모델링 현황</span>
                </div>
                <span class="badge-violet">모델링 대상 {total_target}개소</span>
            </div>
            
            <div class="step-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span class="step-badge step-b1">Step 1</span>
                        <strong style="font-size:0.78rem; color:#1e293b;">1차 3D 구조 모델링</strong>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span style="font-size:0.75rem; font-weight:700; color:#6366f1;">{step1_cnt} <span style="font-size:0.68rem; color:#94a3b8; font-weight:500;">/ {total_target}</span></span>
                        <span class="badge-violet" style="font-size:0.65rem;">{p1:.1f}%</span>
                    </div>
                </div>
                <div style="font-size:0.68rem; color:#64748b; margin-bottom:4px;">구조 도면 기반 3D 프레임 및 해석 모델 구축</div>
                <div class="step-prog-track">
                    <div class="step-prog-bar" style="width:{p1:.1f}%; background:linear-gradient(90deg, #818cf8, #6366f1);"></div>
                </div>
            </div>

            <div class="step-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span class="step-badge step-b2">Step 2</span>
                        <strong style="font-size:0.78rem; color:#1e293b;">현장 계측 데이터 분석 완료</strong>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span style="font-size:0.75rem; font-weight:700; color:#10b981;">{step2_cnt} <span style="font-size:0.68rem; color:#94a3b8; font-weight:500;">/ {total_target}</span></span>
                        <span class="badge-mint" style="font-size:0.65rem;">{p2:.1f}%</span>
                    </div>
                </div>
                <div style="font-size:0.68rem; color:#64748b; margin-bottom:4px;">상시진동 가속도 계측 데이터 분석 및 고유진동수·모드형상 추출</div>
                <div class="step-prog-track">
                    <div class="step-prog-bar" style="width:{p2:.1f}%; background:linear-gradient(90deg, #34d399, #10b981);"></div>
                </div>
            </div>

            <div class="step-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span class="step-badge step-b3">Step 3</span>
                        <strong style="font-size:0.78rem; color:#1e293b;">구조 모델 캘리브레이션</strong>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span style="font-size:0.75rem; font-weight:700; color:#8b5cf6;">{step3_cnt} <span style="font-size:0.68rem; color:#94a3b8; font-weight:500;">/ {total_target}</span></span>
                        <span class="badge-violet" style="font-size:0.65rem;">{p3:.1f}%</span>
                    </div>
                </div>
                <div style="font-size:0.68rem; color:#64748b; margin-bottom:4px;">계측 분석 데이터 기반 모델 파라미터 보정 및 신뢰도 확보</div>
                <div class="step-prog-track">
                    <div class="step-prog-bar" style="width:{p3:.1f}%; background:linear-gradient(90deg, #a855f7, #8b5cf6);"></div>
                </div>
            </div>
        </div>
        """
        render_html(step_html)

        # 13 Regional Education Offices Progress Chart (Based on Target Facilities)
        reg_head = f"""
        <div class="saas-card">
            <div class="sec-header">
                <span>🏛️ 13개 시도 교육청별 배정 및 실적 (모델링 대상 {total_target}개소)</span>
                <div style="font-size:0.75rem; color:#64748b;">지역별 실시간 현황</div>
            </div>
        """
        render_html(reg_head)

        df_reg = df_target.groupby('교육청').agg(
            총시설=('시설물번호', 'count'),
            계측완료=('Step2_계측완료', 'sum'),
            모델링완료=('Step1_1차모델링', 'sum')
        ).reset_index().sort_values('총시설', ascending=True)

        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(y=df_reg['교육청'], x=df_reg['총시설'], orientation='h', name=f"총 배정 ({total_target})", marker_color="#e2e8f0"))
        fig_reg.add_trace(go.Bar(y=df_reg['교육청'], x=df_reg['계측완료'], orientation='h', name="계측 분석 완료", marker_color="#34d399"))
        fig_reg.add_trace(go.Bar(y=df_reg['교육청'], x=df_reg['모델링완료'], orientation='h', name="1차 모델링 완료", marker_color="#6366f1"))

        fig_reg.update_layout(
            barmode="group",
            height=210,
            margin=dict(l=5, r=5, t=10, b=5),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#334155", size=9.5, family="Pretendard"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9, color="#1e293b")),
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", linecolor="#cbd5e1", tickfont=dict(color="#475569")),
            yaxis=dict(showgrid=False, linecolor="#cbd5e1", tickfont=dict(size=8.5, color="#1e293b"))
        )
        st.plotly_chart(fig_reg, use_container_width=True)
        render_html("</div>")

        # Quick Action Helper Box
        quick_box = f"""
        <div class="saas-card" style="background:linear-gradient(135deg, #f8faff 0%, #eef2ff 100%); border:1px solid #e0e7ff;">
            <div style="font-size:0.82rem; font-weight:800; color:#312e81; margin-bottom:4px;">💡 실시간 분석 요약 (모델링 대상 {total_target}개 기준)</div>
            <div style="font-size:0.73rem; color:#4338ca; line-height:1.45;">
                • 분석 대상 <strong>총 {total_target}동</strong>: 교사동 <strong>{sch_cnt}동</strong>(2층 이하·3층·4층·5층 층수별 체계화), 체육관 <strong>{gym_cnt}동</strong>(일반철골·트러스·스페이스·돔아치 4대 구조형식)<br>
                • 현재 <strong>현장 계측 분석 완료({step2_cnt}개소, {s2_rate:.1f}%)</strong> 선행 완료, <strong>1차 3D 모델링({step1_cnt}개소)</strong> 및 <strong>모델 캘리브레이션({step3_cnt}개소)</strong> 순차 진행 중
            </div>
        </div>
        """
        render_html(quick_box)

    # Interactive Search and Filter Table
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    with st.expander("📋 실시간 시설 상세 검색 및 공정 필터링 테이블 (클릭하여 열기)", expanded=False):
        fc0, fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([1.2, 1.0, 0.9, 0.8, 0.8, 0.9, 1.1])
        with fc0:
            scope_opt = st.selectbox("분석 대상 범위", [f"모델링 대상 시설 ({total_target}개소)", f"전체 학교 시설 DB ({len(df_sheet)}개소)"])
        with fc1:
            search_kw = st.text_input("🔍 학교명 검색", placeholder="예: 가평, 영동, 대전...")
        with fc2:
            base_df = df_target if "대상" in scope_opt else df_sheet
            reg_opts = ["전체"] + sorted(list(base_df['교육청'].unique()))
            sel_reg = st.selectbox("시도 교육청", reg_opts)
        with fc3:
            type_opts = ["전체", "교사동", "체육관"] + [t for t in sorted(base_df['시설구분'].unique()) if t not in ["교사동", "체육관", "-"]]
            sel_type = st.selectbox("시설 구분", type_opts)
        with fc4:
            floor_opts = ["전체", "2층 이하", "3층", "4층", "5층"]
            sel_floor = st.selectbox("층수 (교사동)", floor_opts)
        with fc5:
            roof_opts = ["전체", "일반철골", "트러스", "스페이스프레임", "돔·아치"]
            sel_roof = st.selectbox("지붕구조 (체육관)", roof_opts)
        with fc6:
            step_filter = st.selectbox("공정 상태 필터", ["전체", "Step1 1차모델링 완료", "Step2 현장 계측 분석 완료", "Step3 캘리브레이션 완료"])

        df_filtered = df_target.copy() if "대상" in scope_opt else df_sheet.copy()
        if search_kw.strip():
            df_filtered = df_filtered[df_filtered['학교명'].str.contains(search_kw.strip(), na=False)]
        if sel_reg != "전체":
            df_filtered = df_filtered[df_filtered['교육청'] == sel_reg]
        if sel_type != "전체":
            df_filtered = df_filtered[df_filtered['시설구분'] == sel_type]
        if sel_floor != "전체":
            df_filtered = df_filtered[df_filtered['층수'] == sel_floor]
        if sel_roof != "전체":
            df_filtered = df_filtered[df_filtered['지붕구조'] == sel_roof]
        if step_filter == "Step1 1차모델링 완료":
            df_filtered = df_filtered[df_filtered['Step1_1차모델링']]
        elif step_filter == "Step2 현장 계측 분석 완료":
            df_filtered = df_filtered[df_filtered['Step2_계측완료']]
        elif step_filter == "Step3 캘리브레이션 완료":
            df_filtered = df_filtered[df_filtered['Step3_캘리브레이션']]

        df_display = df_filtered[['대상주차', '교육청', '지원청', '학교명', '시설상세명', '시설구분', '층수', '지붕구조', '내진상태', 'Step1_1차모델링', 'Step2_계측완료', 'Step3_캘리브레이션', '담당자']].copy()
        df_display = df_display.rename(columns={'Step2_계측완료': 'Step2_계측분석완료'})

        st.dataframe(
            df_display,
            use_container_width=True,
            height=260
        )


# =============================================================================
# TAB 2: 교사동·체육관 통계
# =============================================================================
elif selected_tab == "교사동·체육관 통계":
    df_sch = df_target[df_target['시설구분'] == '교사동']
    df_gym = df_target[df_target['시설구분'] == '체육관']

    sch_m = df_sch['Step2_계측완료'].sum()
    sch_mod = df_sch['Step1_1차모델링'].sum()
    sch_cal = df_sch['Step3_캘리브레이션'].sum()

    gym_m = df_gym['Step2_계측완료'].sum()
    gym_mod = df_gym['Step1_1차모델링'].sum()
    gym_cal = df_gym['Step3_캘리브레이션'].sum()

    tk1, tk2, tk3, tk4 = st.columns(4)
    with tk1:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>🏢 교사동 총 분석 대상</span><span class="badge-violet">{len(df_sch)}개소</span></div>
            <div class="saas-card-num" style="color:#6366f1;">{len(df_sch)} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">동</span></div>
            <div class="saas-card-sub">2층 이하 16 · 3층 33 · 4층 26 · 5층 9</div>
        </div>
        """)
    with tk2:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>🏢 교사동 공정 진척도</span><span class="badge-mint">분석 완료 {sch_m/len(df_sch)*100:.1f}%</span></div>
            <div class="saas-card-num">{sch_m} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">/ {len(df_sch)}동 분석</span></div>
            <div class="saas-card-sub">모델링 {sch_mod}동 ({sch_mod/len(df_sch)*100:.1f}%) · 캘리 {sch_cal}동</div>
        </div>
        """)
    with tk3:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>🏟️ 체육관 총 분석 대상</span><span class="badge-mint">{len(df_gym)}개소</span></div>
            <div class="saas-card-num" style="color:#10b981;">{len(df_gym)} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">동</span></div>
            <div class="saas-card-sub">일반철골 22 · 돔아치 16 · 트러스 12 · 스페이스 11</div>
        </div>
        """)
    with tk4:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>🏟️ 체육관 공정 진척도</span><span class="badge-violet">분석 완료 {gym_m/len(df_gym)*100:.1f}%</span></div>
            <div class="saas-card-num">{gym_m} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">/ {len(df_gym)}동 분석</span></div>
            <div class="saas-card-sub">모델링 {gym_mod}동 ({gym_mod/len(df_gym)*100:.1f}%) · 캘리 {gym_cal}동</div>
        </div>
        """)

    col_stat1, col_stat2 = st.columns(2)

    with col_stat1:
        render_html("""
        <div class="saas-card">
            <div class="sec-header">
                <span>🏢 교사동 층수별 상세 공정 비교 분석</span>
                <span class="badge-violet">총 85개소</span>
            </div>
        """)
        
        sch_summary = df_sch.groupby('층수').agg(
            총시설=('시설물번호', 'count'),
            모델링완료=('Step1_1차모델링', 'sum'),
            계측분석완료=('Step2_계측완료', 'sum'),
            캘리브레이션=('Step3_캘리브레이션', 'sum')
        ).reindex(['2층 이하', '3층', '4층', '5층']).fillna(0).reset_index()
        
        fig_cs1 = go.Figure()
        fig_cs1.add_trace(go.Bar(x=sch_summary['층수'], y=sch_summary['총시설'], name="총 대상동", marker_color="#e2e8f0"))
        fig_cs1.add_trace(go.Bar(x=sch_summary['층수'], y=sch_summary['계측분석완료'], name="Step 2 현장 계측 분석 완료", marker_color="#34d399"))
        fig_cs1.add_trace(go.Bar(x=sch_summary['층수'], y=sch_summary['모델링완료'], name="Step 1 1차 3D모델링", marker_color="#6366f1"))
        fig_cs1.add_trace(go.Bar(x=sch_summary['층수'], y=sch_summary['캘리브레이션'], name="Step 3 캘리브레이션", marker_color="#a855f7"))
        
        fig_cs1.update_layout(
            barmode="group",
            height=200,
            margin=dict(l=5, r=5, t=10, b=5),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#334155", size=9.5, family="Pretendard"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9, color="#1e293b")),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", linecolor="#cbd5e1"),
            xaxis=dict(showgrid=False, linecolor="#cbd5e1")
        )
        st.plotly_chart(fig_cs1, use_container_width=True)

        sch_summary['잔여대상'] = sch_summary['총시설'] - sch_summary['계측분석완료']
        sch_summary['분석완료율'] = (sch_summary['계측분석완료'] / sch_summary['총시설'] * 100).map(lambda x: f'{x:.1f}%')
        st.dataframe(sch_summary[['층수', '총시설', '계측분석완료', '모델링완료', '캘리브레이션', '잔여대상', '분석완료율']], use_container_width=True, hide_index=True)
        render_html("</div>")

    with col_stat2:
        render_html("""
        <div class="saas-card">
            <div class="sec-header">
                <span>🏟️ 체육관 지붕구조별 상세 공정 비교 분석</span>
                <span class="badge-mint">총 63개소</span>
            </div>
        """)
        
        gym_summary = df_gym.groupby('지붕구조').agg(
            총시설=('시설물번호', 'count'),
            모델링완료=('Step1_1차모델링', 'sum'),
            계측분석완료=('Step2_계측완료', 'sum'),
            캘리브레이션=('Step3_캘리브레이션', 'sum')
        ).reindex(['일반철골', '트러스', '스페이스프레임', '돔·아치']).fillna(0).reset_index()

        fig_cs2 = go.Figure()
        fig_cs2.add_trace(go.Bar(x=gym_summary['지붕구조'], y=gym_summary['총시설'], name="총 대상동", marker_color="#e2e8f0"))
        fig_cs2.add_trace(go.Bar(x=gym_summary['지붕구조'], y=gym_summary['계측분석완료'], name="Step 2 현장 계측 분석 완료", marker_color="#10b981"))
        fig_cs2.add_trace(go.Bar(x=gym_summary['지붕구조'], y=gym_summary['모델링완료'], name="Step 1 1차 3D모델링", marker_color="#6366f1"))
        fig_cs2.add_trace(go.Bar(x=gym_summary['지붕구조'], y=gym_summary['캘리브레이션'], name="Step 3 캘리브레이션", marker_color="#a855f7"))

        fig_cs2.update_layout(
            barmode="group",
            height=200,
            margin=dict(l=5, r=5, t=10, b=5),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#334155", size=9.5, family="Pretendard"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9, color="#1e293b")),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", linecolor="#cbd5e1"),
            xaxis=dict(showgrid=False, linecolor="#cbd5e1")
        )
        st.plotly_chart(fig_cs2, use_container_width=True)

        gym_summary['잔여대상'] = gym_summary['총시설'] - gym_summary['계측분석완료']
        gym_summary['분석완료율'] = (gym_summary['계측분석완료'] / gym_summary['총시설'] * 100).map(lambda x: f'{x:.1f}%')
        st.dataframe(gym_summary[['지붕구조', '총시설', '계측분석완료', '모델링완료', '캘리브레이션', '잔여대상', '분석완료율']], use_container_width=True, hide_index=True)
        render_html("</div>")

    # Photo Gallery & Drilldown with Lightbox Modal
    render_html("""
    <div class="saas-card">
        <div class="sec-header">
            <span>🖼️ 대표 학교 시설 전경 (교사동 4대 층수 · 체육관 4대 지붕구조)</span>
            <div style="font-size:0.75rem; color:#6366f1; font-weight:600;">🔍 사진 클릭 시 원본 확대</div>
        </div>
    """)
    photos_tab2 = [
        {"id": "t2_p1", "type": "2층 이하", "name": "영동초 후관", "badge_bg": "#6366f1", "file": "2층_영동초등학교 후관교사.jpg", "fullname": "영동초등학교 후관교사 (2층 이하)"},
        {"id": "t2_p2", "type": "3층 교사", "name": "서대전초 본관", "badge_bg": "#6366f1", "file": "3층_서대전초등학교 본관교사.jpg", "fullname": "서대전초등학교 본관교사 (3층)"},
        {"id": "t2_p3", "type": "4층 교사", "name": "성남수정초 본관", "badge_bg": "#6366f1", "file": "4층_성남수정초등학교 본관교사.jpg", "fullname": "성남수정초등학교 본관교사 (4층)"},
        {"id": "t2_p4", "type": "5층 교사", "name": "동두천중앙고", "badge_bg": "#6366f1", "file": "5층_동두천중앙고등학교 본관교사.jpg", "fullname": "동두천중앙고등학교 본관교사 (5층)"},
        {"id": "t2_p5", "type": "일반철골", "name": "진천상업고", "badge_bg": "#10b981", "file": "일반철골_진천상업고등학교 체육관.jpg", "fullname": "진천상업고등학교 체육관 (일반철골)"},
        {"id": "t2_p6", "type": "트러스", "name": "서대전초 체육", "badge_bg": "#10b981", "file": "트러스_서대전초등학교 체육관.jpg", "fullname": "서대전초등학교 체육관 (트러스)"},
        {"id": "t2_p7", "type": "스페이스", "name": "안성고 체육관", "badge_bg": "#10b981", "file": "스페이스프레임_안성고등학교 체육관.jpg", "fullname": "안성고등학교 체육관 (스페이스프레임)"},
        {"id": "t2_p8", "type": "돔·아치", "name": "의정부여중", "badge_bg": "#10b981", "file": "돔아치_의정부여자중학교 체육관.jpg", "fullname": "의정부여자중학교 체육관 (돔·아치)"}
    ]
    p_cols2 = st.columns(8)
    modal_htmls2 = []
    for col, item in zip(p_cols2, photos_tab2):
        img_data = get_base64_image(item["file"])
        with col:
            p_html = f"""
            <a href="#{item['id']}" class="photo-saas-card" title="클릭하여 크게 보기">
                <div style="position:relative;">
                    <img src="{img_data}" class="photo-saas-img">
                    <span style="position:absolute; top:3px; left:3px; background:{item['badge_bg']}; color:white; font-size:0.60rem; font-weight:bold; padding:1px 5px; border-radius:4px;">{item['type']}</span>
                </div>
                <div class="photo-saas-name">{item['name']}</div>
            </a>
            """
            render_html(p_html)

        modal_html = f"""
        <div id="{item['id']}" class="img-lightbox-modal">
            <a href="#close" class="img-lightbox-bg-close"></a>
            <div class="img-lightbox-box">
                <a href="#close" class="img-lightbox-close" title="닫기">&times;</a>
                <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:12px; display:flex; align-items:center; justify-content:center; gap:8px;">
                    <span style="background:{item['badge_bg']}; color:white; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:6px;">{item['type']}</span>
                    <span>{item['fullname']}</span>
                </div>
                <img src="{img_data}" alt="{item['fullname']}">
                <div style="margin-top:10px; font-size:0.75rem; color:#64748b;">
                    현장 진동 계측 데이터 분석 및 3D 모델링 대상 대표 표준 시설
                </div>
            </div>
        </div>
        """
        modal_htmls2.append(modal_html)

    render_html("</div>" + "".join(modal_htmls2))


# =============================================================================
# TAB 3: 주차별 로드맵
# =============================================================================
elif selected_tab == "주차별 로드맵":
    df_week = df_target[df_target['대상주차'] != '-'].copy()
    week_order = sorted(df_week['대상주차'].unique())
    
    wk1, wk2, wk3, wk4 = st.columns(4)
    with wk1:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>📅 추진 마일스톤 기간</span><span class="badge-mint">총 {len(week_order)}개 주차</span></div>
            <div class="saas-card-num">{len(week_order)} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">개 주차 운영</span></div>
            <div class="saas-card-sub">06월 2주차 ~ 10월 4주차 순차 배정</div>
        </div>
        """)
    with wk2:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>📅 최고 실적 주차</span><span class="badge-mint">06월 2주차</span></div>
            <div class="saas-card-num" style="color:#10b981;">47 <span style="font-size:0.85rem; font-weight:600; color:#64748b;">동 분석 완료</span></div>
            <div class="saas-card-sub">모델링 14동 완료 (초기 집중 수행)</div>
        </div>
        """)
    with wk3:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>📅 진행 중인 주차</span><span class="badge-violet">08~09월</span></div>
            <div class="saas-card-num" style="color:#6366f1;">78 <span style="font-size:0.85rem; font-weight:600; color:#64748b;">동 배정</span></div>
            <div class="saas-card-sub">계측 분석 10동 완료 · 잔여 일정 순차 투입</div>
        </div>
        """)
    with wk4:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>📅 후속 집중 주차</span><span class="badge-amber">10월 주차</span></div>
            <div class="saas-card-num" style="color:#f59e0b;">23 <span style="font-size:0.85rem; font-weight:600; color:#64748b;">동 배정</span></div>
            <div class="saas-card-sub">후속 마일스톤 계측 분석 및 최종 검증</div>
        </div>
        """)

    # Main Weekly Chart
    render_html("""
    <div class="saas-card">
        <div class="sec-header">
            <span>📊 주차별 배정 시설 및 공정 실적 타임라인</span>
            <div style="font-size:0.75rem; color:#64748b;">실시간 작업 진행 현황</div>
        </div>
    """)
    week_stat = []
    for w in week_order:
        sub = df_week[df_week['대상주차'] == w]
        week_stat.append({
            "주차": w,
            "총시설": len(sub),
            "계측분석완료": int(sub['Step2_계측완료'].sum()),
            "모델링완료": int(sub['Step1_1차모델링'].sum()),
            "캘리브레이션": int(sub['Step3_캘리브레이션'].sum())
        })
    df_wstat = pd.DataFrame(week_stat)

    fig_w_main = go.Figure()
    fig_w_main.add_trace(go.Bar(x=df_wstat['주차'], y=df_wstat['총시설'], name="총 배정 시설수", marker_color="#cbd5e1"))
    fig_w_main.add_trace(go.Bar(x=df_wstat['주차'], y=df_wstat['계측분석완료'], name="Step 2 현장 계측 분석 완료", marker_color="#10b981"))
    fig_w_main.add_trace(go.Bar(x=df_wstat['주차'], y=df_wstat['모델링완료'], name="Step 1 1차 모델링 완료", marker_color="#6366f1"))
    fig_w_main.add_trace(go.Bar(x=df_wstat['주차'], y=df_wstat['캘리브레이션'], name="Step 3 캘리브레이션", marker_color="#8b5cf6"))

    fig_w_main.update_layout(
        barmode="group",
        height=240,
        margin=dict(l=5, r=5, t=10, b=5),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#334155", size=9.5, family="Pretendard"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9.5, color="#1e293b")),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", linecolor="#cbd5e1"),
        xaxis=dict(showgrid=False, linecolor="#cbd5e1")
    )
    st.plotly_chart(fig_w_main, use_container_width=True)
    render_html("</div>")

    # Interactive Week Drilldown
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    col_sel_w, col_tbl_w = st.columns([1.0, 3.0])

    with col_sel_w:
        render_html("""
        <div class="saas-card">
            <div class="sec-header"><span>🔍 주차별 시설 상세 조회</span></div>
        """)
        sel_week_target = st.selectbox("조회할 주차를 선택하세요", week_order, index=0)
        df_selected_week = df_target[df_target['대상주차'] == sel_week_target]
        w_tot = len(df_selected_week)
        w_s2 = df_selected_week['Step2_계측완료'].sum()
        w_s1 = df_selected_week['Step1_1차모델링'].sum()
        render_html(f"""
            <div style="margin-top:10px; font-size:0.75rem; color:#475569; line-height:1.6;">
                • 선택 주차: <strong>{sel_week_target}</strong><br>
                • 총 배정 시설: <strong>{w_tot}개소</strong><br>
                • 현장 계측 분석 완료: <strong>{w_s2}개소 ({w_s2/w_tot*100 if w_tot>0 else 0:.1f}%)</strong><br>
                • 1차 모델링 완료: <strong>{w_s1}개소 ({w_s1/w_tot*100 if w_tot>0 else 0:.1f}%)</strong>
            </div>
        </div>
        """)

    with col_tbl_w:
        render_html(f"""
        <div class="saas-card">
            <div class="sec-header"><span>📋 {sel_week_target} 배정 학교 시설 목록 ({len(df_selected_week)}개소)</span></div>
        """)
        df_week_disp = df_selected_week[['학교명', '시설상세명', '시설구분', '층수', '지붕구조', '교육청', 'Step1_1차모델링', 'Step2_계측완료', 'Step3_캘리브레이션', '담당자']].copy()
        df_week_disp = df_week_disp.rename(columns={'Step2_계측완료': 'Step2_계측분석완료'})
        st.dataframe(
            df_week_disp,
            use_container_width=True,
            height=220,
            hide_index=True
        )
        render_html("</div>")


# =============================================================================
# TAB 4: 실시간 데이터 시트
# =============================================================================
elif selected_tab == "실시간 데이터 시트":
    sk1, sk2, sk3, sk4 = st.columns(4)
    with sk1:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>전체 학교 DB 시설</span><span class="badge-mint">222개소</span></div>
            <div class="saas-card-num">{len(df_sheet)} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">개소</span></div>
            <div class="saas-card-sub">구글 스프레드시트 실시간 동기화 완료</div>
        </div>
        """)
    with sk2:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>모델링 분석 대상 (S열)</span><span class="badge-violet">{total_target}개소</span></div>
            <div class="saas-card-num" style="color:#6366f1;">{total_target} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">개소</span></div>
            <div class="saas-card-sub">교사동 {sch_cnt}동 · 체육관 {gym_cnt}동</div>
        </div>
        """)
    with sk3:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>Step 2 현장 계측 분석 완료</span><span class="badge-mint">{step2_cnt}개소</span></div>
            <div class="saas-card-num" style="color:#10b981;">{step2_cnt} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">/ {total_target}</span></div>
            <div class="saas-card-sub">진척률 {s2_rate:.1f}%</div>
        </div>
        """)
    with sk4:
        render_html(f"""
        <div class="saas-card">
            <div class="saas-card-title"><span>Step 1 1차 모델링 완료</span><span class="badge-violet">{step1_cnt}개소</span></div>
            <div class="saas-card-num" style="color:#8b5cf6;">{step1_cnt} <span style="font-size:0.85rem; font-weight:600; color:#64748b;">/ {total_target}</span></div>
            <div class="saas-card-sub">진척률 {s1_rate:.1f}%</div>
        </div>
        """)

    render_html("""
    <div class="saas-card">
        <div class="sec-header">
            <span>📋 실시간 데이터베이스 다차원 필터링 및 검색</span>
        </div>
    """)
    fc0, fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([1.2, 1.0, 0.9, 0.8, 0.8, 0.9, 1.1])
    with fc0:
        scope_opt = st.selectbox("분석 대상 범위", [f"모델링 대상 시설 ({total_target}개소)", f"전체 학교 시설 DB ({len(df_sheet)}개소)"], key="sheet_scope")
    with fc1:
        search_kw = st.text_input("🔍 학교명 검색", placeholder="예: 가평, 영동, 대전...", key="sheet_kw")
    with fc2:
        base_df = df_target if "대상" in scope_opt else df_sheet
        reg_opts = ["전체"] + sorted(list(base_df['교육청'].unique()))
        sel_reg = st.selectbox("시도 교육청", reg_opts, key="sheet_reg")
    with fc3:
        type_opts = ["전체", "교사동", "체육관"] + [t for t in sorted(base_df['시설구분'].unique()) if t not in ["교사동", "체육관", "-"]]
        sel_type = st.selectbox("시설 구분", type_opts, key="sheet_type")
    with fc4:
        floor_opts = ["전체", "2층 이하", "3층", "4층", "5층"]
        sel_floor = st.selectbox("층수 (교사동)", floor_opts, key="sheet_floor")
    with fc5:
        roof_opts = ["전체", "일반철골", "트러스", "스페이스프레임", "돔·아치"]
        sel_roof = st.selectbox("지붕구조 (체육관)", roof_opts, key="sheet_roof")
    with fc6:
        step_filter = st.selectbox("공정 상태 필터", ["전체", "Step1 1차모델링 완료", "Step2 현장 계측 분석 완료", "Step3 캘리브레이션 완료"], key="sheet_step")

    df_filtered = df_target.copy() if "대상" in scope_opt else df_sheet.copy()
    if search_kw.strip():
        df_filtered = df_filtered[df_filtered['학교명'].str.contains(search_kw.strip(), na=False)]
    if sel_reg != "전체":
        df_filtered = df_filtered[df_filtered['교육청'] == sel_reg]
    if sel_type != "전체":
        df_filtered = df_filtered[df_filtered['시설구분'] == sel_type]
    if sel_floor != "전체":
        df_filtered = df_filtered[df_filtered['층수'] == sel_floor]
    if sel_roof != "전체":
        df_filtered = df_filtered[df_filtered['지붕구조'] == sel_roof]
    if step_filter == "Step1 1차모델링 완료":
        df_filtered = df_filtered[df_filtered['Step1_1차모델링']]
    elif step_filter == "Step2 현장 계측 분석 완료":
        df_filtered = df_filtered[df_filtered['Step2_계측완료']]
    elif step_filter == "Step3 캘리브레이션 완료":
        df_filtered = df_filtered[df_filtered['Step3_캘리브레이션']]

    st.write(f"조회 결과: 총 **{len(df_filtered)}건**의 시설 데이터")
    
    df_sheet_disp = df_filtered[['대상주차', '교육청', '지원청', '학교명', '시설상세명', '시설구분', '층수', '지붕구조', '내진상태', 'Step1_1차모델링', 'Step2_계측완료', 'Step3_캘리브레이션', '담당자']].copy()
    df_sheet_disp = df_sheet_disp.rename(columns={'Step2_계측완료': 'Step2_계측분석완료'})

    st.dataframe(
        df_sheet_disp,
        use_container_width=True,
        height=380
    )

    csv_data = df_filtered.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 필터링된 데이터 CSV 내보내기",
        data=csv_data,
        file_name=f"Seismic_School_Monitoring_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    render_html("</div>")


# -----------------------------------------------------------------------------
# 6. Global Bottom Copyright Footer
# -----------------------------------------------------------------------------
render_html("""
<footer style="margin-top:24px; padding:20px 0 12px 0; border-top:1px solid #e2e8f0; text-align:center;">
    <div style="font-size:0.80rem; font-weight:700; color:#64748b; letter-spacing:-0.2px;">
        © 2026 단국대학교 부설 리모델링연구소. All rights reserved.
    </div>
    <div style="font-size:0.70rem; color:#94a3b8; margin-top:4px;">
        학교시설 비구조요소 내진보강 기반 마련 연구(1차) 계측 및 3D 모델링 종합 관제 시스템
    </div>
</footer>
""")
