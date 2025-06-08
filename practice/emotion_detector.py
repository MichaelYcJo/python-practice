from transformers import pipeline

def analyze_sentiment(text: str):
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    result = classifier(text)[0]
    label = result['label']
    score = result['score']
    print(f"🧠 감정 분석 결과: {label} ({score:.2f})")

if __name__ == "__main__":
    input_text = "I love using AI to build cool things!"
    analyze_sentiment(input_text)
    