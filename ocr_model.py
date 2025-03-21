# OCR 모델 인터페이스
# 실제 모델 연동 부분은 구현해야 합니다

def perform_ocr(image_path):
    """
    이미지 경로를 받아 OCR을 수행하고 결과를 반환합니다.
    
    Args:
        image_path (str): 이미지 파일 경로
        
    Returns:
        list: OCR 결과 리스트. 각 항목은 다음 형식의 딕셔너리입니다:
            {
                'id': 'unique_id',
                'text': '인식된 텍스트',
                'confidence': 신뢰도 (0-100),
                'bbox': [x1, y1, x2, y2] (텍스트 영역의 좌표)
            }
    """
    # 여기에 실제 OCR 모델 연동 코드를 구현하세요
    # 아래는 테스트용 샘플 데이터입니다
    
    # 예시 데이터
    sample_results = [
        {
            'id': '1',
            'text': '사업자등록증',
            'confidence': 95,
            'bbox': [100, 50, 300, 80]
        },
        {
            'id': '2',
            'text': '등록번호: 123-45-67890',
            'confidence': 92,
            'bbox': [100, 100, 400, 130]
        },
        {
            'id': '3',
            'text': '상호: 예시회사',
            'confidence': 88,
            'bbox': [100, 150, 350, 180]
        },
        {
            'id': '4',
            'text': '대표자: 홍길동',
            'confidence': 90,
            'bbox': [100, 200, 350, 230]
        },
        {
            'id': '5',
            'text': '주소: 서울시 강남구 테헤란로 123',
            'confidence': 85,
            'bbox': [100, 250, 500, 280]
        }
    ]
    
    return sample_results 