import streamlit as st
import cv2
import numpy as np
from PIL import Image

# 페이지 설정
st.set_page_config(page_title="녹 분석기", layout="wide")

st.title("🧪 부식 면적 실시간 분석기")

# 1. 사이드바에 상세한 원리 설명과 슬라이더 배치
with st.sidebar:
    st.header("🔍 분석 필터 설정 가이드")
    
    # --- 색상(Hue) 설명 ---
    st.subheader("1. 색상(Hue) 범위 설정")
    st.markdown("""
    **범위 원리:** 최소값 이상 ~ 최대값 이하의 '색상 울타리'를 만듭니다.
    * **0 ~ 20:** 붉은색, 주황색, 갈색 (**녹색의 주요 구간**)
    * **20 ~ 40:** 노란색 (갓 생긴 연한 녹)
    * **40 ~ 90:** 초록색, 민트색
    * **90 ~ 130:** 파란색, 보라색
    * **130 ~ 179:** 다시 붉은색 계열
    
    ✅ **추천 범위:** **최소 0 ~ 최대 25** (일반적인 철 부식 분석 시)
    """)
    h_min = st.slider("색상 최소값 (범위 시작)", 0, 179, 0)
    h_max = st.slider("색상 최대값 (범위 끝)", 0, 179, 25)
    
    st.divider()
    
    # --- 채도(Saturation) 설명 ---
    st.subheader("2. 채도(Saturation) 최소값")
    st.info("""
    **버리는 범위:** **0 ~ 설정값 미만** (이 구간은 분석에서 제외됩니다.)
    
    **💡 팁:** 은색 철판은 색이 연해서 채도가 매우 낮습니다. 
    은색 철판의 채도보다 최소값을 더 높게 설정하세요. 그러면 철판은 버리고 '진한 녹색'만 빨갛게 남길 수 있습니다.
    """)
    s_min = st.slider("채도 최소값 (설정값 미만은 버림)", 0, 255, 50)
    
    st.divider()
    
    # --- 밝기(Value) 설명 ---
    st.subheader("3. 밝기(Value) 최소값")
    st.info("""
    **버리는 범위:** **0 ~ 설정값 미만** (너무 어두운 곳은 버립니다.)
    
    **💡 팁:** 그림자나 어두운 구석은 검은색에 가까워 분석을 방해합니다. 
    최소값을 적당히 높여서 어두운 영역을 분석 대상에서 제외하세요.
    """)
    v_min = st.slider("밝기 최소값 (설정값 미만은 버림)", 0, 255, 50)

# 2. 이미지 업로드 및 분석 로직
uploaded_file = st.file_uploader("철판 사진을 업로드하세요", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

    # 슬라이더 값 적용 (채도와 밝기는 최대치를 255로 고정하여 최소값 이상의 모든 영역 포함)
    lower_rust = np.array([h_min, s_min, v_min])
    upper_rust = np.array([h_max, 255, 255]) 
    mask = cv2.inRange(hsv, lower_rust, upper_rust)

    # 결과 계산
    rust_pixels = np.sum(mask == 255)
    total_pixels = img_cv.shape[0] * img_cv.shape[1]
    ratio = (rust_pixels / total_pixels) * 100

    # 시각화
    result_img = img_cv.copy()
    result_img[mask == 255] = [0, 0, 255] 
    result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 원본 사진")
        st.image(img, use_container_width=True)
    with col2:
        st.subheader("🔬 분석 결과")
        st.image(result_img, caption="빨간색 영역이 감지된 녹입니다.", use_container_width=True)

    st.markdown(f"""
    <div style="background-color:#f0f2f6;padding:25px;border-radius:15px;border:2px solid #ff4b4b;text-align:center;">
        <h2 style="margin:0;">전체 면적 대비 녹 발생 비율: <span style="color:#ff4b4b;">{ratio:.2f}%</span></h2>
    </div>
    """, unsafe_allow_html=True)
