import textwrap
import warnings
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

warnings.filterwarnings("ignore")

# ───────────────────────
# 1) 추출적 요약 (LexRank)
# ───────────────────────
def extractive_summary(text: str, num_sentences: int = 2) -> str:
    parser     = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sents = summarizer(parser.document, num_sentences)
    return " ".join(str(sent) for sent in summary_sents)

# ───────────────────────
# 2) 생성적 요약 모델 로딩
# ───────────────────────
def load_summarizer(model_name="facebook/bart-large-cnn"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model     = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return pipeline("summarization", model=model, tokenizer=tokenizer)

# ───────────────────────
# 3) 생성적 요약
# ───────────────────────
def abstractive_summary(text: str,
                        summarizer,
                        min_length: int = 30,
                        max_length: int = 130) -> str:
    out = summarizer(
        text,
        max_length=max_length,
        min_length=min_length,
        do_sample=False
    )
    return out[0]["summary_text"]

# ───────────────────────
# 4) 하이브리드 요약 함수
# ───────────────────────
def summarize_text(text: str,
                   model_name: str = "facebook/bart-large-cnn") -> str:
    if not text or not isinstance(text, str):
        raise ValueError("요약할 텍스트를 문자열로 입력해주세요.")

    # 토큰(단어) 수 기준
    word_count = len(text.split())
    print(f"📝 입력 길이: {word_count} words")

    # 50 단어 이하: 원문 반환
    if word_count <= 50:
        print("ℹ️ 짧은 텍스트이므로 원문을 반환합니다.")
        return text.strip()

    # 200 단어 이하: 추출적 요약
    if word_count <= 200:
        print("🧩  추출적 요약(LexRank)을 수행합니다.")
        return extractive_summary(text, num_sentences=2)

    # 그 이상: 생성적 요약
    print("🤖  생성적 요약(BART)을 수행합니다.")
    summarizer = load_summarizer(model_name)
    # 먼저 추출적 요약으로 2~3문장 뽑아서 압축
    interim = extractive_summary(text, num_sentences=3)
    return abstractive_summary(interim, summarizer)

# ───────────────────────
# 5) 예시 실행
# ───────────────────────
if __name__ == "__main__":
    sample = (
        "autoimmune disease (AI) is a type of autoimmune disease that affects the immune "
        "system. The disease is caused by a lack of immune system function. It affects "
        "the body's ability to fight infections, such as infections of the skin, skin "
        "cells, and skin cells."
    )

    print("\n📝 원본 텍스트:")
    print(textwrap.fill(sample, width=80))

    result = summarize_text(sample)
    print("\n✅ 요약 결과:")
    print(textwrap.fill(result, width=80))