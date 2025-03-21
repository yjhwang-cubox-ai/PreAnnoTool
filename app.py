import streamlit as st
import os
import json
import tempfile
from PIL import Image, ImageDraw
import numpy as np
from datetime import datetime
from ocr_model import perform_ocr

# 페이지 설정
st.set_page_config(
    page_title="OCR Pre-annotation Tool",
    page_icon="📝",
    layout="wide"
)

# 저장 디렉토리 설정
ANNOTATION_DIR = "annotations"
os.makedirs(ANNOTATION_DIR, exist_ok=True)

# 세션 상태 초기화
if 'ocr_results' not in st.session_state:
    st.session_state.ocr_results = None
if 'temp_image_path' not in st.session_state:
    st.session_state.temp_image_path = None
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'edited_values' not in st.session_state:
    st.session_state.edited_values = {}

# 제목
st.title("OCR Pre-annotation Tool")
st.markdown("사업자등록증 이미지를 업로드하고 OCR 결과를 확인 및 수정할 수 있습니다.")

# 사이드바
with st.sidebar:
    st.header("설정")
    st.markdown("---")
    
    # 이미지 업로드
    uploaded_file = st.file_uploader("사업자등록증 이미지 업로드", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # 이미지 임시 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.write(uploaded_file.getvalue())
        st.session_state.temp_image_path = temp_file.name
        temp_file.close()
        
        # 이미지 표시
        st.session_state.original_image = Image.open(st.session_state.temp_image_path)
        
        # OCR 처리 버튼
        if st.button("OCR 처리 시작"):
            with st.spinner("OCR 처리 중..."):
                # OCR 모델 호출
                try:
                    results = perform_ocr(st.session_state.temp_image_path)
                    st.session_state.ocr_results = results
                    st.session_state.edited_values = {result['id']: result['text'] for result in results}
                    st.success("OCR 처리가 완료되었습니다.")
                except Exception as e:
                    st.error(f"OCR 처리 중 오류가 발생했습니다: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 정보")
    st.info("이 툴은 OCR 결과를 확인하고 수정할 수 있는 기능을 제공합니다.")

# 메인 화면
col1, col2 = st.columns(2)

# 왼쪽 컬럼 - 이미지 표시
with col1:
    st.header("원본 이미지")
    if st.session_state.original_image is not None:
        # 이미지 표시
        st.image(st.session_state.original_image, use_column_width=True)
        
        # 바운딩 박스가 있는 이미지 표시 옵션
        if st.session_state.ocr_results is not None:
            if st.checkbox("바운딩 박스 표시", value=True):
                # 바운딩 박스 그리기
                img_with_boxes = st.session_state.original_image.copy()
                draw = ImageDraw.Draw(img_with_boxes)
                
                for result in st.session_state.ocr_results:
                    bbox = result['bbox']
                    # 박스 그리기
                    draw.rectangle(
                        [(bbox[0], bbox[1]), (bbox[2], bbox[3])],
                        outline="red",
                        width=2
                    )
                    # ID 텍스트 추가
                    draw.text((bbox[0], bbox[1] - 15), f"ID: {result['id']}", fill="red")
                
                st.image(img_with_boxes, use_column_width=True, caption="바운딩 박스가 표시된 이미지")

# 오른쪽 컬럼 - OCR 결과 및 수정
with col2:
    st.header("OCR 결과")
    
    if st.session_state.ocr_results is not None:
        # 각 결과에 대한 편집 가능한 텍스트 필드 표시
        for i, result in enumerate(st.session_state.ocr_results):
            result_id = result['id']
            confidence = result['confidence']
            
            # 컨테이너로 각 결과 묶기
            with st.container():
                st.markdown(f"**항목 {i+1}** (ID: {result_id}, 신뢰도: {confidence}%)")
                
                # 텍스트 수정 입력창
                edited_text = st.text_input(
                    f"인식된 텍스트 {i+1}",
                    value=st.session_state.edited_values.get(result_id, result['text']),
                    key=f"text_{result_id}"
                )
                
                # 세션 상태에 수정된 값 저장
                st.session_state.edited_values[result_id] = edited_text
                
                st.markdown("---")
        
        # 저장 버튼
        if st.button("어노테이션 저장", type="primary"):
            try:
                annotations = []
                
                for result in st.session_state.ocr_results:
                    result_id = result['id']
                    original_text = result['text']
                    modified_text = st.session_state.edited_values.get(result_id, original_text)
                    
                    annotations.append({
                        'id': result_id,
                        'original_text': original_text,
                        'modified_text': modified_text,
                        'confidence': result['confidence'],
                        'bbox': result['bbox'],
                        'modified': (original_text != modified_text)
                    })
                
                # 이미지 파일명 가져오기
                original_filename = os.path.basename(uploaded_file.name)
                base_filename = os.path.splitext(original_filename)[0]
                
                # 타임스탬프 추가
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{base_filename}_annotation_{timestamp}.json"
                output_path = os.path.join(ANNOTATION_DIR, output_filename)
                
                # JSON 파일로 저장
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'image_filename': original_filename,
                        'annotations': annotations,
                        'timestamp': timestamp
                    }, f, ensure_ascii=False, indent=2)
                
                st.success(f"어노테이션이 저장되었습니다. 파일 위치: {output_path}")
                
                # 다운로드 버튼 추가
                with open(output_path, 'r', encoding='utf-8') as f:
                    json_data = f.read()
                    
                st.download_button(
                    label="JSON 파일 다운로드",
                    data=json_data,
                    file_name=output_filename,
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"저장 중 오류가 발생했습니다: {str(e)}")
    else:
        if uploaded_file is not None:
            st.info("OCR 처리를 시작하려면 왼쪽 사이드바의 'OCR 처리 시작' 버튼을 클릭하세요.")
        else:
            st.info("이미지를 업로드하고 OCR 처리를 시작해주세요.")