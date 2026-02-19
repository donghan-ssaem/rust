import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# 1. 앱 페이지 설정
st.set_page_config(page_title="녹슨 면적 측정기", layout="centered")

st.title("錆(녹) 면적 측정 앱 🧪")
st.markdown("""
학생 실험을 위한 철판의 **녹슨 면적 비율**을 측정해 보세요!
사진을 업로드하면 녹슨 부분을 분석하여 면적 비율을 알려줍니다.
""")

st.warning("측정 정확도는 사진의 조명, 각도, 녹의 색상에 따라 달라질 수 있습니다.")

# 2. 이미지 업로드 위젯
uploaded_file = st.file_uploader("철판 사진을 업로드해주세요 (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 3. 이미지 읽기 및 전처리
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 원본 사진", use_column_width=True)

    # PIL 이미지를 OpenCV 형식으로 변환 (RGB -> BGR)
    img_array = np.array(image)
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # 4. 이미지 처리 시작
    st.subheader("📊 녹슨 면적 분석 결과")

    # 이미지를 HSV 색공간으로 변환 (색상 기반 분리에 유리)
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

    # ✅ 중요: 녹색상 범위 정의 (이 값은 실제 녹 색상에 맞춰 조정해야 합니다!)
    # 일반적으로 녹은 주황-갈색-붉은색 계열에 해당합니다.
    # [H_min, S_min, V_min], [H_max, S_max, V_max]
    # 예시: 붉은색 계열의 녹
    # lower_rust = np.array([0, 100, 100])
    # upper_rust = np.array([20, 255, 255])
    # 갈색 계열의 녹 (더 일반적)
    lower_rust1 = np.array([0, 50, 50]) # 붉은 갈색 시작
    upper_rust1 = np.array([20, 255, 255]) # 붉은 갈색 끝
    lower_rust2 = np.array([170, 50, 50]) # 다시 붉은색 계열
    upper_rust2 = np.array([180, 255, 255]) # 붉은색 끝

    # 두 범위의 마스크를 생성하고 합침
    mask1 = cv2.inRange(hsv, lower_rust1, upper_rust1)
    mask2 = cv2.inRange(hsv, lower_rust2, upper_rust2)
    rust_mask = cv2.bitwise_or(mask1, mask2)
    
    # 노이즈 제거 (작은 점들을 없애고, 구멍을 채움)
    kernel = np.ones((5,5), np.uint8)
    rust_mask = cv2.morphologyEx(rust_mask, cv2.MORPH_OPEN, kernel) # 열림 연산
    rust_mask = cv2.morphologyEx(rust_mask, cv2.MORPH_CLOSE, kernel) # 닫힘 연산

    # 녹슨 픽셀 수 계산
    rust_pixels = np.sum(rust_mask == 255)
    total_pixels = img_cv.shape[0] * img_cv.shape[1] # 전체 픽셀 수

    # 녹슨 면적 비율 계산
    rust_ratio = (rust_pixels / total_pixels) * 100

    # 5. 결과 이미지 시각화
    # 녹슨 부분만 빨간색으로 강조
    # 원본 이미지 복사 후 마스크 적용하여 시각화
    result_img = img_cv.copy()
    result_img[rust_mask == 255] = [0, 0, 255] # BGR 순서로 파란색이 아닌 빨간색으로 (255가 BGR에서 RED)
    
    # 텍스트 추가 (결과 이미지 위에)
    text = f"Rust Area: {rust_ratio:.2f}%"
    cv2.putText(result_img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA) # 흰색 텍스트

    st.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB), caption="분석된 녹슨 부분 (빨간색 강조)", use_column_width=True)

    st.success(f"**총 녹슨 면적 비율: {rust_ratio:.2f}%**")

    st.markdown("""
    ---
    ### ⚙️ 분석 팁:
    만약 녹슨 부분이 제대로 감지되지 않는다면, 사이드바를 통해 녹색상 범위를 조절해 보세요.
    이는 사진의 조명과 실제 녹의 색상에 따라 달라질 수 있습니다.
    """)
    
    # 6. (선택) 녹색상 범위 조절 슬라이더 (정확도 향상)
    with st.sidebar:
        st.header("녹 색상 범위 조정 (고급)")
        st.markdown("정확한 분석을 위해 녹색상(HSV) 범위를 조정할 수 있습니다.")

        st.subheader("첫 번째 녹 색상 범위 (붉은 갈색)")
        h_min1 = st.slider("Hue Min 1", 0, 179, 0)
        s_min1 = st.slider("Saturation Min 1", 0, 255, 50)
        v_min1 = st.slider("Value Min 1", 0, 255, 50)
        h_max1 = st.slider("Hue Max 1", 0, 179, 20)
        s_max1 = st.slider("Saturation Max 1", 0, 255, 255)
        v_max1 = st.slider("Value Max 1", 0, 255, 255)

        lower_rust_custom1 = np.array([h_min1, s_min1, v_min1])
        upper_rust_custom1 = np.array([h_max1, s_max1, v_max1])

        st.subheader("두 번째 녹 색상 범위 (진한 붉은색, 필요시)")
        h_min2 = st.slider("Hue Min 2", 0, 179, 170)
        s_min2 = st.slider("Saturation Min 2", 0, 255, 50)
        v_min2 = st.slider("Value Min 2", 0, 255, 50)
        h_max2 = st.slider("Hue Max 2", 0, 179, 179)
        s_max2 = st.slider("Saturation Max 2", 0, 255, 255)
        v_max2 = st.slider("Value Max 2", 0, 255, 255)

        lower_rust_custom2 = np.array([h_min2, s_min2, v_min2])
        upper_rust_custom2 = np.array([h_max2, s_max2, v_max2])
        
        # 실제 앱에서는 이 사용자 정의 값을 위 분석 로직에 반영해야 합니다.
        # (현재는 기본값으로 작동하며, 추후 연결)
        st.info("이 슬라이더로 조정한 값들은 현재 코드에 직접 반영되진 않습니다. \n"
                "코드 내 `lower_rust1` 등 변수에 직접 입력하여 테스트해 보세요.")
else:
    st.info("사진을 업로드하면 녹슨 면적 분석을 시작합니다.")
