import re
import json
from transformers import DonutProcessor, VisionEncoderDecoderModel, AutoTokenizer, GenerationConfig
from datasets import load_dataset
import torch
from PIL import Image

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
    model_name = 'models/epoch-015_step-01008_ED-0.2259'

    processor = DonutProcessor.from_pretrained(model_name)
    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    gen_config = GenerationConfig.from_pretrained(model_name)

    image = Image.open(image_path).convert("RGB")
    pixel_values = processor(image, return_tensors="pt").pixel_values

    task_prompt = "<s_ko>"
    decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt")["input_ids"]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    outputs = model.generate(
        pixel_values.to(device),
        decoder_input_ids=decoder_input_ids.to(device),
        max_length=model.decoder.config.max_position_embeddings,
        early_stopping=False,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.convert_tokens_to_ids("</s>"),
        # processor.tokenizer.eos_token_id,
        use_cache=True,
        num_beams=1,
        bad_words_ids=[[processor.tokenizer.unk_token_id]],
        return_dict_in_generate=True,
        output_scores=True,)

    sequence = processor.batch_decode(outputs.sequences)[0]
    sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
    sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # remove first task start token
    
    return sequence