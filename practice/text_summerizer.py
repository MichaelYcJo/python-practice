from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import textwrap
import warnings

# 경고 제거
warnings.filterwarnings("ignore")

# 요약 파이프라인 초기화
def load_summarizer(model_name="t5-small"):
    print(f"📦 모델 로딩: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return pipeline("summarization", model=model, tokenizer=tokenizer)

# 텍스트 요약 함수
def summarize_text(text: str, model_name="t5-small", min_length=30, max_length=130):
    if not text or not isinstance(text, str):
        raise ValueError("요약할 텍스트를 문자열로 입력해주세요.")

    print("\n📝 요약 대상 텍스트 일부:")
    print(textwrap.shorten(text.strip(), width=300, placeholder="...") + "\n")

    summarizer = load_summarizer(model_name)
    print("🧠 요약 중...")
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]["summary_text"]

# 예시 실행
if __name__ == "__main__":
    sample_text = """
    인공지능(AI)은 컴퓨터 시스템이 인간과 유사한 방식으로 작업을 수행할 수 있도록 설계된 기술을 의미한다.
    AI 기술은 음성 인식, 자연어 처리, 이미지 분석, 의사 결정 등을 포함한다.
    특히 최근에는 생성형 AI 기술의 발전으로 텍스트 생성, 이미지 생성, 음악 작곡 등 창의적인 영역까지 활용 범위가 확장되고 있다.
    많은 기업들이 AI 기술을 활용해 비즈니스 효율을 높이고 있으며, 관련 시장도 빠르게 성장하고 있다.
    """

    summary = summarize_text(sample_text, model_name="t5-small")
    print("✅ 요약 결과:")
    print(summary)