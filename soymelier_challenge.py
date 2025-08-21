import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json
import os
import pytz

# 페이지 설정
st.set_page_config(
    page_title="두믈리에 챌린지",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 자연 힐링 CSS 스타일 적용
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
    
    /* 전체 앱 배경 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 50%, #e8f5e8 100%);
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    /* 메인 헤더 스타일 */
    .main-header {
        text-align: center;
        padding: 40px 0;
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(39, 174, 96, 0.05));
        border-radius: 25px;
        margin-bottom: 30px;
        border: 2px solid rgba(46, 204, 113, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #2ecc71, #27ae60, #16a085);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #2ecc71, #27ae60, #16a085);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #7f8c8d;
        font-weight: 300;
        margin-top: 15px;
    }
    
    .decorative-text {
        font-size: 2rem;
        margin: 20px 0;
        opacity: 0.7;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 10px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        /* 탭 리스트 가운데 정렬 */
        justify-content: center !important;
        display: flex !important;
        width: 100%;
        
        /* 개별 탭 설정 */
        flex: 0 0 auto;
        min-width: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 25px;
        background: transparent;
        border-radius: 15px;
        color: #34495e;
        font-weight: 500;
        font-size: 1.1rem;
        border: none;
        transition: all 0.3s ease;
        min-width: 250px;
        padding: 0 35px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(46, 204, 113, 0.1);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2ecc71, #27ae60) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
    }
    
    /* 단계 표시기 */
    .step-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 30px 0;
        gap: 20px;
    }
    
    .step-item {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .step-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1.2rem;
        transition: all 0.3s ease;
    }
    
    .step-completed {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
    }
    
    .step-current {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        animation: pulse 2s infinite;
    }
    
    .step-pending {
        background: #ecf0f1;
        color: #95a5a6;
    }
    
    .step-line {
        width: 60px;
        height: 3px;
        background: #ecf0f1;
        border-radius: 2px;
    }
    
    .step-line.completed {
        background: linear-gradient(90deg, #2ecc71, #27ae60);
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3); }
        50% { box-shadow: 0 4px 25px rgba(52, 152, 219, 0.5); }
        100% { box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3); }
    }
    
    /* 프로그레스 바 */
    .progress-container {
        margin: 20px 0;
        padding: 10px;
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #ecf0f1;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* 브랜드 카드 스타일 */
    .brand-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 25px;
        #margin: px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 2px solid rgba(46, 204, 113, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .brand-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #2ecc71, #27ae60);
    }
    
    .brand-name {
        font-size: 1.4rem;
        font-weight: 600;
        color: #27ae60;
        margin-bottom: 10px;
    }

    .brand-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        border-color: rgba(46, 204, 113, 0.3);
    }
    
    .brand-description {
        color: #7f8c8d;
        margin-bottom: 10px;
        line-height: 1.6;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 15px 30px;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
    }

        /* 브랜드 카드 하단 여백 완전 제거 */
    .stMarkdown {
        margin-bottom: 0.5rem !important;
    }
    
    /* 차트 컨테이너 여백 제거 */
    .js-plotly-plot {
        margin-bottom: 0px !important;
    }
    
    /* 컬럼 간격 조정 */
    .stColumns > div {
        padding-bottom: 0px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 204, 113, 0.4);
        background: linear-gradient(135deg, #27ae60, #2ecc71);
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border: 2px solid #e8f5e8;
        border-radius: 15px;
        padding: 15px 20px;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #2ecc71;
        box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.1);
        background: white;
    }
    
    /* 슬라이더 스타일 */
    # .stSlider > div > div > div > div {
    #     background: linear-gradient(90deg, #072ac8);
    # }

    # /* 슬라이더 진행 바 (빨간색→초록색으로 변경) */
    # .stSlider > div > div > div > div {
    #     background: linear-gradient(90deg, #2ecc71, #27ae60) !important;
    # }

    # /* 슬라이더 핸들 (초록 동그라미) */
    # .stSlider > div > div > div > div > div {
    #     background: #27ae60 !important;
    #     border: 2px solid white !important;
    # }
    
    /* 핸들 색상 */
    .stSlider [role="slider"] {
        background: #1e88e5 !important;
        border: 3px solid white !important;
        box-shadow: 0 2px 6px rgba(39, 174, 96, 0.3) !important;
    }
    
    /* 알림창 스타일 */
    .stAlert {
        border-radius: 15px;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
    }
    
    .stSuccess {
        background: rgba(46, 204, 113, 0.1);
        border-left-color: #2ecc71;
    }
    
    .stWarning {
        background: rgba(241, 196, 15, 0.1);
        border-left-color: #f1c40f;
    }
    
    .stError {
        background: rgba(231, 76, 60, 0.1);
        border-left-color: #e74c3c;
    }
    
    .stInfo {
        background: rgba(52, 152, 219, 0.1);
        border-left-color: #3498db;
    }
    
    # /* 데이터프레임 스타일 */
    # .stDataFrame {
    #     border-radius: 15px;
    #     overflow: hidden;
    #     box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    # }
    
    # /* 메트릭 스타일 */
    # .stMetric {
    #     background: rgba(255, 255, 255, 0.8);
    #     padding: 20px;
    #     border-radius: 15px;
    #     border: 2px solid rgba(46, 204, 113, 0.1);
    #     transition: all 0.3s ease;
    # }
    
    # .stMetric:hover {
    #     transform: translateY(-2px);
    #     box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    # }
    
    # /* 사이드바 숨기기 */
    # .css-1d391kg {
    #     display: none;
    # }
    
    # /* 여백 조정 */
    # .block-container {
    #     padding-top: 2rem;
    #     padding-bottom: 2rem;
    # }
    
    /* 섹션 헤더 스타일 */
    .section-header {
        color: #27ae60;
        font-size: 2rem;
        font-weight: 600;
        text-align: center;
        margin: 30px 0;
        padding: 20px;
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(39, 174, 96, 0.05));
        border-radius: 15px;
        border: 2px solid rgba(46, 204, 113, 0.2);
    }
    
    /* 샘플 카드 스타일 */
    .sample-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 2px solid rgba(46, 204, 113, 0.1);
        transition: all 0.3s ease;
    }
    
    .sample-title {
        font-size: 1.6rem;
        font-weight: 600;
        color: #27ae60;
        text-align: center;
        margin-bottom: 20px;
        padding: 15px;
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(39, 174, 96, 0.05));
        border-radius: 10px;
    }
    
    /* 결과 요약 스타일 */
    .results-summary {
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(39, 174, 96, 0.1));
        border-radius: 20px;
        padding: 30px;
        margin: 25px 0;
        border: 2px solid rgba(46, 204, 113, 0.2);
        position: relative;
    }
    
    .results-summary::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #2ecc71, #27ae60, #16a085);
        border-radius: 20px 20px 0 0;
    }
    
    /* 플롯 컨테이너 */
    .plot-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(46, 204, 113, 0.1);
    }
    
    /* 관리자 패널 */
    .admin-panel {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(41, 128, 185, 0.05));
        border-radius: 20px;
        padding: 30px;
        border: 2px solid rgba(52, 152, 219, 0.2);
        margin-top: 20px;
    }
    
    /* 애니메이션 효과 */
    .fade-in {
        animation: fadeIn 0.6s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 떠다니는 장식 요소 */
    .floating-decoration {
        position: fixed;
        pointer-events: none;
        opacity: 0.3;
        z-index: -1;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .content-container {
            padding: 25px;
            margin: 15px 0;
        }
        
        .step-container {
            flex-direction: column;
            gap: 15px;
        }
        
        .step-line {
            width: 3px;
            height: 30px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 네 가지 두유 브랜드 정보
BRANDS = {
    "밥스누 약콩두유": {
        "description": "100% 국산 약콩을 통째로, 콩 본연의 건강한 맛",
        "taste_profile": {"진함": 4, "단맛": 2}  # 1-5 스케일
    },
    "황성주 검은콩두유": {
        "description": "국내산 검은콩, 검은콩의 고소하고 진한 맛",
        "taste_profile": {"진함": 3, "단맛": 3}
    },
    "매일두유": {
        "description": "원액 두유 99.9%, 건강하고 고소한 맛",
        "taste_profile": {"진함": 2, "단맛": 1}
    },
    "베지밀 두유": {
        "description": "오랜 역사와 대중성, 균형 잡히고 친숙한 부드러운 맛",
        "taste_profile": {"진함": 3, "단맛": 4}
    }
}

# Google Sheets 연동 함수
def init_gsheet():
    """Google Sheets 초기화"""
    try:
        # 방법 1: JSON 파일 사용 (로컬 개발용)
        if os.path.exists('service-account-key.json'):
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            credentials = Credentials.from_service_account_file(
                'service-account-key.json', 
                scopes=scope
            )
            gc = gspread.authorize(credentials)
            return gc.open('두믈리에_챌린지_데이터').sheet1
        
        # 방법 2: Streamlit Secrets 사용 (배포용)
        elif "gcp_service_account" in st.secrets:
            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=['https://spreadsheets.google.com/feeds',
                       'https://www.googleapis.com/auth/drive']
            )
            gc = gspread.authorize(credentials)
            spreadsheet_name = st.secrets.get("spreadsheet_name", "두믈리에_챌린지_데이터")
            return gc.open(spreadsheet_name).sheet1
        
        else:
            st.warning("⚠️ Google Sheets 연동이 설정되지 않았습니다. 데모 모드로 실행됩니다.")
            return None
            
    except Exception as e:
        st.error(f"Google Sheets 연동 오류: {e}")
        st.info("📋 설정 가이드를 참조하여 Google Sheets를 연동해주세요.")
        return None

def save_to_gsheet(data):
    """데이터를 Google Sheets에 저장"""
    sheet = init_gsheet()
    if sheet:
        try:
            # 먼저 시트를 완전히 초기화 (기존 데이터가 있어도 헤더 재설정)
            try:
                all_values = sheet.get_all_values()
                if not all_values or len(all_values) == 0:
                    # 빈 시트인 경우 헤더 추가
                    headers = ['이름', '성별', '연령', '소속', '제출시간',
                              'A_진함', 'A_단맛', 'A_선택브랜드',
                              'B_진함', 'B_단맛', 'B_선택브랜드',
                              'C_진함', 'C_단맛', 'C_선택브랜드',
                              'D_진함', 'D_단맛', 'D_선택브랜드']
                    sheet.append_row(headers)
                    st.info(f"✅ 헤더 생성 완료 (총 {len(headers)}개 컬럼)")
                elif len(all_values[0]) < 16:
                    # 헤더가 부족한 경우 시트 초기화
                    sheet.clear()
                    headers = ['이름', '성별', '연령', '소속', '제출시간',
                              'A_진함', 'A_단맛', 'A_선택브랜드',
                              'B_진함', 'B_단맛', 'B_선택브랜드',
                              'C_진함', 'C_단맛', 'C_선택브랜드',
                              'D_진함', 'D_단맛', 'D_선택브랜드']
                    sheet.append_row(headers)
                    st.info("✅ 시트가 재초기화되었습니다.")
            except:
                # 안전한 초기화
                headers = ['이름', '성별', '연령', '소속', '제출시간',
                          'A_진함', 'A_단맛', 'A_선택브랜드',
                          'B_진함', 'B_단맛', 'B_선택브랜드',
                          'C_진함', 'C_단맛', 'C_선택브랜드',
                          'D_진함', 'D_단맛', 'D_선택브랜드']
                sheet.clear()
                sheet.append_row(headers)
            
            # 데이터 길이를 16개로 맞춤
            if len(data) > 16:
                data = data[:17]  # 16개로 자르기
            elif len(data) < 16:
                data.extend([''] * (16 - len(data)))  # 부족한 부분 빈 문자열로 채우기
            
            # 모든 데이터를 문자열로 변환
            data = [str(item) for item in data]
            
            # 데이터 추가
            sheet.append_row(data)
            return True
            
        except Exception as e:
            st.error(f"❌ 데이터 저장 오류: {e}")
            st.error(f"❌ 오류 상세: {type(e).__name__}")
            return False
    else:
        # Google Sheets 연동이 안된 경우 세션에 임시 저장 (데모용)
        if 'demo_data' not in st.session_state:
            st.session_state.demo_data = []
        st.session_state.demo_data.append(data)
        st.success("✅ 데이터가 저장되었습니다 (데모 모드)")
        st.info("🔗 실제 Google Sheets 연동을 위해 설정 가이드를 참조해주세요.")
        return True

def create_taste_profile_radar(taste_data, title):
    """Taste Profile 레이더 차트 생성 - 자연 테마"""
    categories = ['진함', '단맛']
    values = [taste_data.get('진함', 0), taste_data.get('단맛', 0)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=title,
        line=dict(color='#27ae60', width=3),
        fillcolor='rgba(46, 204, 113, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4],
                gridcolor='rgba(46, 204, 113, 0.2)',
                linecolor='rgba(46, 204, 113, 0.3)'
            ),
            angularaxis=dict(
                gridcolor='rgba(46, 204, 113, 0.2)',
                linecolor='rgba(46, 204, 113, 0.3)'
            ),
            bgcolor='rgba(255, 255, 255, 0.8)'
        ),
        showlegend=False,
        title={
            'text': title,
            'x': 0.5,  # 가운데 정렬
            'xanchor': 'center',  # 앵커를 중심으로
            'font': {'size': 16, 'color': '#27ae60', 'family': 'Noto Sans KR'}
        },
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def display_step_indicator(current_step):
    """단계 표시기 렌더링"""
    st.markdown(f"""
    <div class="step-container">
        <div class="step-item">
            <div class="step-circle {'step-completed' if current_step > 1 else 'step-current' if current_step == 1 else 'step-pending'}">1</div>
            <span>참여자 정보</span>
        </div>
        <div class="step-line {'completed' if current_step > 1 else ''}"></div>
        <div class="step-item">
            <div class="step-circle {'step-completed' if current_step > 2 else 'step-current' if current_step == 2 else 'step-pending'}">2</div>
            <span>브랜드 소개</span>
        </div>
        <div class="step-line {'completed' if current_step > 2 else ''}"></div>
        <div class="step-item">
            <div class="step-circle {'step-completed' if current_step > 3 else 'step-current' if current_step == 3 else 'step-pending'}">3</div>
            <span>시음 평가</span>
        </div>
        <div class="step-line {'completed' if current_step > 3 else ''}"></div>
        <div class="step-item">
            <div class="step-circle {'step-completed' if current_step == 4 else 'step-pending'}">4</div>
            <span>결과 확인</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_progress_bar(current_step):
    """프로그레스 바 렌더링"""
    progress = (current_step / 4) * 100
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # 메인 헤더
    st.markdown("""
    <div class="main-header fade-in">
        <div class="decorative-text">🌿 🥛 🌿</div>
        <h1 class="main-title">두믈리에 챌린지</h1>
        <p class="subtitle">자연의 맛을 찾아가는 특별한 여행</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 탭 구성
    tab1, tab2 = st.tabs(["🔔 챌린지 참여", "🖥️ 관리자 대시보드"])
    
    with tab1:
        challenge_page()
    
    with tab2:
        admin_dashboard()

def challenge_page():
    """챌린지 참여 페이지"""
    # 세션 상태 초기화
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'participant_info' not in st.session_state:
        st.session_state.participant_info = {}
    if 'taste_evaluations' not in st.session_state:
        st.session_state.taste_evaluations = {}
    
    # 컨테이너로 감싸기
    with st.container():
        st.markdown('<div class="content-container fade-in">', unsafe_allow_html=True)
        
        # 단계 표시기 및 프로그레스 바
        display_step_indicator(st.session_state.step)
        display_progress_bar(st.session_state.step)
        
        # 1단계: 참여자 정보 입력
        if st.session_state.step == 1:
            st.markdown('<div class="section-header">🌱 참여자 정보 입력</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("이름", key="name", placeholder="이름을 입력하세요")
                gender = st.selectbox("성별", ["선택하세요", "남성", "여성"], key="gender")
            
            with col2:
                age = st.number_input("연령", min_value=1, max_value=120, key="age", value=35)
                organization = st.text_input("소속", key="organization", placeholder="소속을 입력하세요")
            
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🌿 다음 단계로", key="step1_next", use_container_width=True):
                    if name and gender != "선택하세요" and age and organization:
                        st.session_state.participant_info = {
                            "name": name,
                            "gender": gender,
                            "age": age,
                            "organization": organization
                        }
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("모든 정보를 입력해주세요.")
        
        # 2단계: 브랜드 소개
        elif st.session_state.step == 2:
            st.markdown('<div class="section-header">🥛 네 가지 두유 브랜드 소개</div>', unsafe_allow_html=True)
            
            # 브랜드 카드들을 2x2 그리드로 배치
            col1, col2 = st.columns(2)
            brand_list = list(BRANDS.keys())
            
            for i, brand in enumerate(brand_list):
                with col1 if i % 2 == 0 else col2:
                    st.markdown(f"""
                    <div class="brand-card">
                        <h3 class="brand-name">{brand}</h3>
                        <p class="brand-description">{BRANDS[brand]["description"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # # Taste Profile 차트를 컨테이너로 감싸기
                    # with st.container():
                    #     st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                    #     fig = create_taste_profile_radar(BRANDS[brand]["taste_profile"], f"{brand} 맛 프로필")
                    #     st.plotly_chart(fig, use_container_width=True)
                    #     st.markdown('</div>', unsafe_allow_html=True)

                    # 수정 후 (간단하게)
                    fig = create_taste_profile_radar(BRANDS[brand]["taste_profile"], f"{brand} 맛 프로필")
                    st.plotly_chart(fig, use_container_width=True)

                    # 맛 프로필 바 차트
                    cleanness = BRANDS[brand]["taste_profile"]["진함"]
                    sweetness = BRANDS[brand]["taste_profile"]["단맛"]
                    
                    st.markdown("**맛 특성:**")
                    st.markdown(f"진함: {'🟢' * cleanness}{'⚪' * (4-cleanness)} ({cleanness}/4)")
                    st.markdown(f"단맛: {'🟢' * sweetness}{'⚪' * (4-sweetness)} ({sweetness}/4)")
                    if i < len(brand_list) - 1:
                        st.markdown("---")
            
            st.info("📝 각 브랜드의 맛 특성을 확인하신 후, 다음 단계에서 실제 시음을 진행해주세요!")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🌱 시음 평가하기", key="step2_next", use_container_width=True):
                    st.session_state.step = 3
                    st.rerun()
        
        # 3단계: 시음 평가
        elif st.session_state.step == 3:
            st.markdown('<div class="section-header">🌿 시음 평가</div>', unsafe_allow_html=True)
            st.info("A, B, C, D 두유를 시음하고 각각의 맛을 평가해주세요.")
            
            samples = ['A', 'B', 'C', 'D']
            
            # 이미 선택된 브랜드들을 추적
            def get_selected_brands():
                selected = []
                for sample in samples:
                    brand = st.session_state.get(f"{sample}_brand", "선택하세요")
                    if brand != "선택하세요":
                        selected.append(brand)
                return selected
            
            # 각 샘플에 대해 사용 가능한 브랜드 옵션 생성
            def get_available_brands(current_sample):
                selected_brands = get_selected_brands()
                current_selection = st.session_state.get(f"{current_sample}_brand", "선택하세요")
                
                available_brands = ["선택하세요"]
                for brand in BRANDS.keys():
                    if brand not in selected_brands or brand == current_selection:
                        available_brands.append(brand)
                
                return available_brands
            
            # 2x2 그리드로 샘플 배치
            for row in range(2):
                col1, col2 = st.columns(2)
                for col_idx, col in enumerate([col1, col2]):
                    sample_idx = row * 2 + col_idx
                    if sample_idx < len(samples):
                        sample = samples[sample_idx]
                        
                        with col:
                            st.markdown(f"""
                            <div class="sample-card">
                                <div class="sample-title">🥛 {sample} 두유</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 깔끔함 슬라이더
                            cleanness = st.slider(
                                f"**맛의 진함**",
                                min_value=1, max_value=4, value=2,
                                help="1: 매우 깔끔함, 4: 매우 진함",
                                key=f"{sample}_cleanness"
                            )
                            st.markdown(f"현재 값: {cleanness}/4 {'🔵' * cleanness}{'⚪' * (4-cleanness)}")
                            
                            # 단맛 슬라이더
                            sweetness = st.slider(
                                f"**단맛 정도**",
                                min_value=1, max_value=5, value=3,
                                help="1: 달지 않음, 4: 달큰함",
                                key=f"{sample}_sweetness"
                            )
                            st.markdown(f"현재 값: {sweetness}/4 {'🔵' * sweetness}{'⚪' * (4-sweetness)}")
                            
                            # 브랜드 선택
                            available_brands = get_available_brands(sample)
                            current_selection = st.session_state.get(f"{sample}_brand", "선택하세요")
                            
                            if current_selection not in available_brands:
                                current_selection = "선택하세요"
                            
                            selected_brand = st.selectbox(
                                f"어떤 브랜드일까요?",
                                available_brands,
                                index=available_brands.index(current_selection) if current_selection in available_brands else 0,
                                key=f"{sample}_brand"
                            )
                            
                            # 중복 선택 경고
                            if selected_brand != "선택하세요":
                                selected_brands = get_selected_brands()
                                duplicate_samples = []
                                for other_sample in samples:
                                    if other_sample != sample and st.session_state.get(f"{other_sample}_brand") == selected_brand:
                                        duplicate_samples.append(other_sample)
                                
                                if duplicate_samples:
                                    st.warning(f"⚠️ {selected_brand}는 {', '.join(duplicate_samples)} 샘플에서도 선택되었습니다!")
                                    st.info("💡 각 브랜드는 한 번만 선택할 수 있습니다.")
                            
                            # 실시간 레이더 차트
                            if cleanness and sweetness:
                                #with st.container():
                                    #st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                                    taste_data = {"진함": cleanness, "단맛": sweetness}
                                    fig = create_taste_profile_radar(taste_data, f"{sample} 두유 평가")
                                    st.plotly_chart(fig, use_container_width=True)
                                    #st.markdown('</div>', unsafe_allow_html=True)
            
            # 선택 현황 표시
            st.markdown('<div class="section-header">📋 현재 선택 현황</div>', unsafe_allow_html=True)
            
            selection_status = []
            for sample in samples:
                brand = st.session_state.get(f"{sample}_brand", "선택하세요")
                status = "✅ 완료" if brand != "선택하세요" else "❌ 미완료"
                selection_status.append({
                    "샘플": f"{sample} 두유",
                    "선택한 브랜드": brand,
                    "상태": status
                })
            
            status_df = pd.DataFrame(selection_status)
            st.dataframe(status_df, use_container_width=True)
            
            # 완료 확인
            all_completed = all([
                st.session_state.get(f"{sample}_brand", "선택하세요") != "선택하세요"
                for sample in samples
            ])
            
            selected_brands = get_selected_brands()
            has_duplicates = len(selected_brands) != len(set(selected_brands))
            
            if all_completed and not has_duplicates:
                st.success("🎉 모든 두유 평가가 완료되었습니다!")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🌱 평가 완료하기", key="step3_complete", use_container_width=True):
                        for sample in samples:
                            st.session_state.taste_evaluations[sample] = {
                                "진함": st.session_state[f"{sample}_cleanness"],
                                "단맛": st.session_state[f"{sample}_sweetness"],
                                "선택브랜드": st.session_state[f"{sample}_brand"]
                            }
                        st.session_state.step = 4
                        st.rerun()
            elif not all_completed:
                st.warning("⚠️ 모든 두유의 브랜드를 선택해주세요.")
            elif has_duplicates:
                st.error("❌ 중복된 브랜드가 선택되었습니다. 각 브랜드는 한 번만 선택할 수 있습니다.")
        
        # 4단계: 결과 제출
        elif st.session_state.step == 4:
            st.markdown('<div class="section-header">🎉 평가 완료!</div>', unsafe_allow_html=True)
            
            # 결과 요약
            participant = st.session_state.participant_info
            
            st.markdown(f"""
            <div class="results-summary">
                <h3 style="color: #27ae60; margin-bottom: 20px;">📋 평가 결과 요약</h3>
                <p><strong>참여자:</strong> {participant['name']} ({participant['gender']}, {participant['age']}세)</p>
                <p><strong>소속:</strong> {participant['organization']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 평가 결과 테이블
            results_data = []
            for sample in ['A', 'B', 'C', 'D']:
                eval_data = st.session_state.taste_evaluations[sample]
                results_data.append({
                    '샘플': f'{sample} 두유',
                    '진함 (1-5)': f"{eval_data['진함']}/5 {'🟢' * eval_data['진함']}{'⚪' * (5-eval_data['진함'])}",
                    '단맛 (1-5)': f"{eval_data['단맛']}/5 {'🟢' * eval_data['단맛']}{'⚪' * (5-eval_data['단맛'])}",
                    '예상 브랜드': eval_data['선택브랜드']
                })
            
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True)
            
            # 제출 버튼
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🌿 최종 제출하기", key="step4_submit", use_container_width=True):
                    # 저장할 데이터 준비
                    kst = pytz.timezone('Asia/Seoul')
                    submit_data = [
                        participant['name'],
                        participant['gender'],
                        participant['age'],
                        participant['organization'],
                        datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")  # 한국시간 적용
                    ]
                    
                    # A, B, C, D 평가 데이터 추가
                    for sample in ['A', 'B', 'C', 'D']:
                        eval_data = st.session_state.taste_evaluations[sample]
                        submit_data.extend([
                            eval_data['진함'],
                            eval_data['단맛'],
                            eval_data['선택브랜드']
                        ])
                    
                    # 저장
                    if save_to_gsheet(submit_data):
                        st.success("🎉 제출이 완료되었습니다! 참여해주셔서 감사합니다.")
                        #st.balloons()
                        
                        # 새 참여자를 위한 리셋 버튼
                        if st.button("🌱 새로운 참여자 시작", key="step4_reset", use_container_width=True):
                            for key in list(st.session_state.keys()):
                                del st.session_state[key]
                            st.rerun()
                    else:
                        st.error("제출 중 오류가 발생했습니다. 다시 시도해주세요.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def admin_dashboard():
    """관리자 대시보드"""
    st.markdown('<div class="content-container fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">👑 관리자 대시보드</div>', unsafe_allow_html=True)
    
    # 관리자 인증
    admin_password = st.text_input("관리자 비밀번호", type="password", key="admin_password")
    
    if admin_password != "admin123":
        st.warning("⚠️ 관리자 비밀번호를 입력해주세요.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    st.markdown("""
    <div class="admin-panel">
        <h3 style="color: #3498db; margin-bottom: 20px;">✅ 관리자 인증 완료</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 관리 기능들
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔗 Google Sheets 연결 테스트", key="admin_connect_test", use_container_width=True):
            sheet = init_gsheet()
            if sheet:
                try:
                    all_records = sheet.get_all_records()
                    st.success(f"📊 총 {len(all_records)}개의 데이터가 있습니다.")
                except Exception as e:
                    st.error(f"데이터 읽기 오류: {e}")
            else:
                st.error("Google Sheets 연결에 실패했습니다.")
    
    with col2:
        if st.button("📊 전체 데이터 보기", key="admin_show_all", use_container_width=True):
            show_all_data()
    
    # 소속별 분석
    st.markdown('<div class="section-header">🏢 소속별 결과 분석</div>', unsafe_allow_html=True)
    organization_filter = st.text_input("분석할 소속명을 입력하세요", key="admin_org_filter")
    
    if organization_filter:
        if st.button("📈 분석하기", use_container_width=True):
            show_organization_analysis(organization_filter)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_all_data():
    """전체 데이터 표시"""
    sheet = init_gsheet()
    if sheet:
        try:
            all_records = sheet.get_all_records()
            if all_records:
                df = pd.DataFrame(all_records)
                st.dataframe(df, use_container_width=True)
                
                # 기본 통계
                st.markdown('<div class="section-header">📈 기본 통계</div>', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("총 참여자", len(df))
                with col2:
                    if '소속' in df.columns:
                        st.metric("참여 소속 수", df['소속'].nunique())
                with col3:
                    if '성별' in df.columns:
                        male_count = (df['성별'] == '남성').sum()
                        st.metric("남성 참여자", male_count)
                with col4:
                    if '성별' in df.columns:
                        female_count = (df['성별'] == '여성').sum()
                        st.metric("여성 참여자", female_count)
            else:
                st.info("아직 데이터가 없습니다.")
        except Exception as e:
            st.error(f"데이터 로드 오류: {e}")
    else:
        # 데모 데이터 표시
        if 'demo_data' in st.session_state and st.session_state.demo_data:
            st.info("📋 Google Sheets 연동 후 실제 데이터를 표시합니다 (현재 데모 모드)")
            demo_df = pd.DataFrame(st.session_state.demo_data, 
                                 columns=['이름', '성별', '연령', '소속', '제출시간',
                                         'A_진함', 'A_단맛', 'A_선택브랜드',
                                         'B_진함', 'B_단맛', 'B_선택브랜드',
                                         'C_진함', 'C_단맛', 'C_선택브랜드',
                                         'D_진함', 'D_단맛', 'D_선택브랜드'])
            st.dataframe(demo_df, use_container_width=True)
        else:
            st.info("아직 데이터가 없습니다.")

def show_organization_analysis(organization_filter):
    """소속별 분석 표시"""
    samples = ['A', 'B', 'C', 'D']
    
    sheet = init_gsheet()
    if sheet:
        try:
            all_records = sheet.get_all_records()
            df = pd.DataFrame(all_records)
            
            if not df.empty and '소속' in df.columns:
                # 해당 소속 데이터 필터링
                filtered_df = df[df['소속'].str.contains(organization_filter, na=False)]
                
                if not filtered_df.empty:
                    st.write(f"📈 **{organization_filter}** 소속 참여자: {len(filtered_df)}명")
                    
                    # 정답 설정 (실제 챌린지에 맞게 수정하세요)
                    correct_answers = {
                        'A': '밥스누 약콩두유',
                        'B': '황성주 검은콩두유', 
                        'C': '매일두유',
                        'D': '베지밀 두유'
                    }
                    
                    # 완벽한 정답자 찾기
                    all_correct_participants = []
                    for _, row in filtered_df.iterrows():
                        correct_count = 0
                        for sample in samples:
                            if row.get(f'{sample}_선택브랜드') == correct_answers[sample]:
                                correct_count += 1
                        
                        if correct_count == 4:
                            all_correct_participants.append(row['이름'])
                    
                    # 완벽한 정답자 표시
                    if all_correct_participants:
                        st.success(f"🏆 **완벽한 두믈리에 ({len(all_correct_participants)}명):** {', '.join(all_correct_participants)}")
                    else:
                        st.info("🎯 아직 네 개 브랜드를 모두 맞춘 참여자가 없습니다.")
                    
                    # 상세 결과 테이블
                    detailed_results = []
                    for _, row in filtered_df.iterrows():
                        result = {
                            '이름': row['이름'],
                            '성별': row.get('성별', ''),
                            '연령': row.get('연령', ''),
                        }
                        
                        correct_count = 0
                        for sample in samples:
                            selected_brand = row.get(f'{sample}_선택브랜드', '')
                            is_correct = selected_brand == correct_answers[sample]
                            if is_correct:
                                correct_count += 1
                            result[f'{sample}_선택'] = selected_brand
                            result[f'{sample}_정답'] = '✅' if is_correct else '❌'
                            result[f'{sample}_진함'] = row.get(f'{sample}_진함', '')
                            result[f'{sample}_단맛'] = row.get(f'{sample}_단맛', '')
                        
                        result['총_정답수'] = f"{correct_count}/4"
                        detailed_results.append(result)
                    
                    # 결과 표시
                    results_df = pd.DataFrame(detailed_results)
                    st.markdown('<div class="section-header">📋 상세 결과</div>', unsafe_allow_html=True)
                    
                    # 정답 수에 따라 정렬
                    results_df['정답순서'] = results_df['총_정답수'].apply(lambda x: int(x.split('/')[0]))
                    results_df = results_df.sort_values('정답순서', ascending=False)
                    results_df = results_df.drop('정답순서', axis=1)
                    
                    st.dataframe(results_df, use_container_width=True)
                    
                    # 시각화
                    st.markdown('<div class="section-header">📊 정답률 분석</div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # 브랜드별 정답률 차트
                        accuracy_data = []
                        for sample in samples:
                            correct_count = sum(1 for _, row in filtered_df.iterrows() 
                                              if row.get(f'{sample}_선택브랜드') == correct_answers[sample])
                            accuracy_rate = (correct_count / len(filtered_df)) * 100
                            accuracy_data.append({
                                '샘플': f'{sample}\n({correct_answers[sample]})',
                                '정답률': accuracy_rate,
                                '정답자수': correct_count,
                                '전체': len(filtered_df)
                            })
                        
                        accuracy_df = pd.DataFrame(accuracy_data)
                        
                        # 막대 차트
                        fig_bar = go.Figure(data=[
                            go.Bar(
                                x=accuracy_df['샘플'],
                                y=accuracy_df['정답률'],
                                text=[f"{rate:.1f}%<br>({correct}/{total})" 
                                      for rate, correct, total in zip(accuracy_df['정답률'], 
                                                                     accuracy_df['정답자수'], 
                                                                     accuracy_df['전체'])],
                                textposition='auto',
                                marker_color=['#2ecc71', '#27ae60', '#16a085', '#1abc9c']
                            )
                        ])
                        
                        fig_bar.update_layout(
                            title=f"{organization_filter} 브랜드별 정답률",
                            xaxis_title="두유 샘플",
                            yaxis_title="정답률 (%)",
                            yaxis=dict(range=[0, 100]),
                            height=400,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(family='Noto Sans KR', color='#2c3e50')
                        )
                        
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        # 정답률 메트릭
                        total_correct = sum(accuracy_df['정답자수'])
                        total_attempts = len(filtered_df) * 4
                        overall_accuracy = (total_correct / total_attempts) * 100
                        
                        st.metric(
                            label="전체 정답률",
                            value=f"{overall_accuracy:.1f}%",
                            delta=f"{total_correct}/{total_attempts}"
                        )
                        
                        st.metric(
                            label="완벽한 정답자",
                            value=f"{len(all_correct_participants)}명",
                            delta=f"{len(all_correct_participants)}/{len(filtered_df)}"
                        )
                        
                        # 개별 정답률
                        st.markdown("**브랜드별 상세 정답률:**")
                        for _, row in accuracy_df.iterrows():
                            st.metric(
                                label=row['샘플'].replace('\n', ' '),
                                value=f"{row['정답률']:.1f}%",
                                delta=f"{row['정답자수']}/{row['전체']}"
                            )
                
                else:
                    st.info(f"'{organization_filter}' 소속의 데이터가 없습니다.")
            else:
                st.warning("데이터가 없거나 형식이 올바르지 않습니다.")
        except Exception as e:
            st.error(f"데이터 분석 오류: {e}")
    else:
        st.info("Google Sheets 연동이 필요합니다.")

if __name__ == "__main__":
    main()
