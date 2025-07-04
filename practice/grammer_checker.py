from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained("prithivida/grammar_error_correcter_v1")
model = AutoModelForSeq2SeqLM.from_pretrained("prithivida/grammar_error_correcter_v1")

def correct_sentence(text: str) -> str:
    """단일 문장 문법 교정"""
    inputs = tokenizer.encode(text, return_tensors="pt", max_length=128, truncation=True)
    outputs = model.generate(inputs, max_length=128, num_beams=5)
    corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return corrected

def correct_multiple_sentences(sentences: list[str]):
    """여러 문장을 순차적으로 교정"""
    print("📝 문장 교정 결과:")
    print("=" * 40)
    for i, sentence in enumerate(sentences, 1):
        corrected = correct_sentence(sentence)
        print(f"{i}. ✏️ 원문    : {sentence}")
        print(f"   ✅ 교정본 : {corrected}")
        print("-" * 40)

# 예시 입력
if __name__ == "__main__":
    test_sentences = [
        "He go to school everyday.",
        "They is playing in the park.",
        "What time she wake up?",
        "The informations are incorrect.",
        "I has a apple."
    ]
    correct_multiple_sentences(test_sentences)