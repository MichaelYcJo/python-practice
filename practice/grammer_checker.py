from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# 모델 로드
tokenizer = AutoTokenizer.from_pretrained("prithivida/grammar_error_correcter_v1")
model = AutoModelForSeq2SeqLM.from_pretrained("prithivida/grammar_error_correcter_v1")

def correct_grammar(text: str) -> str:
    input_text = "gec: " + text
    inputs = tokenizer.encode(input_text, return_tensors="pt", truncation=True)
    outputs = model.generate(inputs, max_length=128, num_beams=5, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# 테스트
input_text = "She no went to the market yesterday."
corrected = correct_grammar(input_text)
print(f"✅ 원문: {input_text}")
print(f"🔧 교정: {corrected}")