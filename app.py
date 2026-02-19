import streamlit as st
import cv2
import numpy as np
from PIL import Image

# 페이지 설정
st.set_page_config(page_title="녹 분석기", layout="wide")

st.title("🧪 부식 면적 실시간 분석기")

# 1. 사이드바에 상세한 원리 설명과 슬라이더 배치
with st.sidebar:
    st.header("🔍 분석 필터 설정법")
    st.write("컴퓨터에게 '어떤 색이 녹인지' 알려주는 과정입니다.")
    
    st.divider()

    # 1. 색상(Hue) 설명 및 슬라이더
    st.subheader("1. 색상(Hue) 범위")
    st.info("**원리:** 찾고자 하는 '색깔의 종류'를 정합니다.\n\n**팁:** 최소값과 최대값 사이의 울타리를 만들어 녹색(보통 0~20)만 골라냅니다.")
    h_min = st.slider("색상 최소값 (시작)", 0, 179, 0)
    h_max = st.slider("색상 최대값 (끝)", 0, 179, 20)
    
    st.divider()
    
    # 2. 채도(Saturation) 설명 및 슬라이더
    st.subheader("2. 채도(Saturation) 최소값")
    st.info("**원리:** 색이 얼마나 '진한가'를 봅니다.\n\n**팁:** 은색 철판은 색이 연해서 채도가 낮습니다. 최소값을 높여서 진한 녹색만 남기세요.")
    s_min = st.slider("채도 최소값", 0, 255, 50)
    
    st.divider()
    
    # 3. 밝기(Value) 설명 및 슬라이더
    st.subheader("3. 밝기(Value) 최소값")
    st.info("**원리:** 얼마나 '밝은가'를 봅니다.\n\n**팁:** 너무 어두운 그림자나 구석을 녹으로 착각하지 않게 하려면 최소값을 적당히 높여주세요.")
    v_min = st.slider("밝기 최소값", 0, 255, 50)

# 2. 이미지 업로드부
uploaded_file = st.file_uploader("분석할 철판 사진을 업로드하세요", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 이미지 처리
    img = Image.open(uploaded_file)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

    # 슬라이더 값 적용
    lower_rust = np.array([h_min, s_min, v_min])
    upper_rust = np.array([h_max, 255, 255]) # 최대치는 넉넉하게 255로 고정
    mask = cv2.inRange(hsv, lower_rust, upper_rust)

    # 결과 계산
    rust_pixels = np.sum(mask == 255)
    total_pixels = img_cv.shape[0] * img_cv.shape[1]
    ratio = (rust_pixels / total_pixels) * 100

    # 결과 이미지 시각화
    result_img = img_cv.copy()
    result_img[mask == 255] = [0, 0, 255] # 녹슨 곳을 빨간색(BGR에서 Red)으로 표시
    result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

    # 화면 레이아웃 구성
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 원본 사진")
        st.image(img, use_container_width=True)
    with col2:
        st.subheader("🔬 분석 결과")
        st.image(result_img, caption="빨간색으로 칠해진 부분이 감지된 녹입니다.", use_container_width=True)

    # 최종 결과 출력
    st.markdown(f"""
    <div style="background-color:#f0f2f6;padding:25px;border-radius:15px;border:2px solid #ff4b4b;">
        <h2 style="margin:0;text-align:center;">전체 면적 대비 녹 발생 비율: <span style="color:#ff4b4b;">{ratio:.2f}%</span></h2>
    </div>
    """, unsafe_allow_html=True)

else:
    st.write("위의 버튼을 눌러 실험 사진을 업로드하면 분석이 시작됩니다.")
