import textwrap
import warnings
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

warnings.filterwarnings("ignore")

#────────────────────────
# 1. 요약 파이프라인 로딩 (강력한 모델 기본)
#────────────────────────
def load_summarizer(model_name="facebook/bart-large-cnn"):
    print(f"📦 모델 로딩: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model     = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return pipeline("summarization", model=model, tokenizer=tokenizer)

#────────────────────────
# 2. 텍스트를 문단 단위로 나눠서 요약
#────────────────────────
def chunk_and_summarize(text: str,
                        summarizer,
                        max_chunk_chars: int = 1000,
                        **summ_kwargs) -> str:
    # 단순히 '\n\n'로 문단 분리
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for p in paragraphs:
        # 문단을 합쳐도 max_chunk_chars 이내면 계속 붙이고,
        # 넘치면 지금까지 묶은 current를 하나의 청크로 보관
        if len(current) + len(p) < max_chunk_chars:
            current += p + "\n\n"
        else:
            chunks.append(current)
            current = p + "\n\n"
    if current:
        chunks.append(current)

    summaries = []
    for i, chunk in enumerate(chunks, 1):
        print(f"  ▶️ 청크 {i}/{len(chunks)} 요약 중...")
        out = summarizer(chunk, **summ_kwargs)[0]["summary_text"]
        summaries.append(out)

    # 청크별 요약을 다시 한 번 합쳐 요약
    combined = " ".join(summaries)
    print("  ▶️ 최종 합본 요약 중...")
    final = summarizer(combined, **summ_kwargs)[0]["summary_text"]
    return final

#────────────────────────
# 3. 메인 요약 함수
#────────────────────────
def summarize_text(text: str,
                   model_name: str = "facebook/bart-large-cnn",
                   min_length: int = 50,
                   max_length: int = 200) -> str:
    if not text or not isinstance(text, str):
        raise ValueError("요약할 텍스트를 문자열로 입력해주세요.")

    print("\n📝 요약 대상 텍스트 일부:")
    print(textwrap.shorten(text.strip(), width=300, placeholder="…") + "\n")

    summarizer = load_summarizer(model_name)
    summary = chunk_and_summarize(
        text,
        summarizer,
        max_chunk_chars=800,    # 한 번에 넘치지 않게
        max_length=max_length,
        min_length=min_length,
        do_sample=False
    )

    return summary

#────────────────────────
# 4. 예시 실행
#────────────────────────
if __name__ == "__main__":
    sample_text = """
    인공지능(AI)은 컴퓨터 시스템이 인간과 유사한 방식으로 작업을 수행할 수 있도록 설계된 기술을 의미한다.
    AI 기술은 음성 인식, 자연어 처리, 이미지 분석, 의사 결정 등을 포함한다.
    특히 최근에는 생성형 AI 기술의 발전으로 텍스트 생성, 이미지 생성, 음악 작곡 등 창의적인 영역까지 활용 범위가 확장되고 있다.
    많은 기업들이 AI 기술을 활용해 비즈니스 효율을 높이고 있으며, 관련 시장도 빠르게 성장하고 있다.

    (여기에 훨씬 더 긴 본문이 들어간다고 가정하세요)
    """

    result = summarize_text(sample_text)
    print("\n✅ 최종 요약 결과:")
    print(textwrap.fill(result, width=80))