## AI
from transformers import AutoModel, AutoProcessor
from PIL import Image
import torch
import requests

model = AutoModel.from_pretrained("Bingsu/clip-vit-large-patch14-ko")
processor = AutoProcessor.from_pretrained("Bingsu/clip-vit-large-patch14-ko")


def ai_classification_food(url, text_query):
    """
    이미지를 AI로 분석한 뒤 이미지 분석 데이터 반환
    """
    if url != None:
        image = Image.open(requests.get(url, stream=True).raw)
        
        # 입력 데이터 준비
        inputs = processor(text=text_query, images=image, return_tensors="pt", padding=True)

        with torch.inference_mode():
            outputs = model(**inputs)

        # 이미지와 텍스트 간의 유사도 계산
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)

        # 확률값에서 가장 큰 값을 찾음
        max_prob, pred_idx = torch.max(probs[0], dim=0)
        pred_text = text_query[pred_idx]

        # 조건에 따라 결과 반환
        if max_prob < 0.89:
            print(f"이미지 분석 취소: 신뢰도 높은 결과 없음 , max_prob: {max_prob}")
            return False
        else:
            print(f"이미지 분석 성공: {pred_text} (확률: {max_prob.item():.4f})")
            return {"pred_text": pred_text, "probability": max_prob.item()}
    else:
        raise ValueError("이미지 url 확인에 실패했습니다.")

def review_analyser():
    """
    리뷰 데이터를 AI로 분석한 뒤 긍정 및 부정 평가
    """
    pass