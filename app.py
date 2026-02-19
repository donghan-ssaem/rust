import streamlit as st
import cv2
import numpy as np
from PIL import Image

# 페이지 설정
st.set_page_config(page_title="녹 분석기", layout="wide")

st.title("🧪 부식 면적 실시간 분석기")
st.info("왼쪽 사이드바의 슬라이더를 조절하여 녹슨 부위를 정확하게 찾아보세요!")

# 1. 사이드바에 상세 설명과 슬라이더 배치
with st.sidebar:
    st.header("🎨 필터 설정 및 도움말")
    
    st.subheader("1. 색상(Hue)")
    st.caption("어떤 '색깔'을 찾을지 결정합니다. 녹은 보통 0~20 사이의 붉은색/갈색 영역에 있습니다.")
    h_min = st.slider("색상 최소값", 0, 179, 0)
    h_max = st.slider("색상 최대값", 0, 179, 20)
    
    st.divider()
    
    st.subheader("2. 채도(Saturation)")
    st.caption("색이 얼마나 '진한가'를 결정합니다. 값이 높을수록 회색빛 철판을 제외하고 진한 녹색만 골라냅니다.")
    s_min = st.slider("채도 최소값", 0, 255, 50)
    
    st.divider()
    
    st.subheader("3. 밝기(Value)")
    st.caption("색이 얼마나 '밝은가'를 결정합니다. 그림자진 어두운 녹까지 포함하려면 값을 낮추세요.")
    v_min = st.slider("밝기 최소값", 0, 255, 50)

# 2. 이미지 업로드부
uploaded_file = st.file_uploader("철판 사진을 업로드하세요", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 이미지 처리
    img = Image.open(uploaded_file)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

    # 슬라이더 값 적용
    lower_rust = np.array([h_min, s_min, v_min])
    upper_rust = np.array([h_max, 255, 255])
    mask = cv2.inRange(hsv, lower_rust, upper_rust)

    # 결과 계산
    rust_pixels = np.sum(mask == 255)
    total_pixels = img_cv.shape[0] * img_cv.shape[1]
    ratio = (rust_pixels / total_pixels) * 100

    # 결과 이미지 시각화
    result_img = img_cv.copy()
    result_img[mask == 255] = [0, 0, 255] # 녹슨 곳을 빨간색으로 표시
    result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

    # 화면 레이아웃 구성
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("원본 사진")
        st.image(img, use_container_width=True)
    with col2:
        st.subheader("분석 결과")
        st.image(result_img, caption="빨간색 영역이 감지된 녹입니다.", use_container_width=True)

    # 최종 결과 출력
    st.markdown(f"""
    <div style="background-color:#f0f2f6;padding:20px;border-radius:10px">
        <h2 style="margin:0;text-align:center;">전체 면적 대비 녹 발생 비율: <span style="color:#ff4b4b;">{ratio:.2f}%</span></h2>
    </div>
    """, unsafe_allow_config=True)

else:
    st.write("위의 버튼을 눌러 분석할 철판 사진을 선택해주세요.")
