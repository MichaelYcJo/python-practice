from googletrans import Translator


def translate_text_file(input_file, output_file, target_language="en"):
    """텍스트 파일을 번역하여 저장하는 함수"""
    translator = Translator()

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            text = file.read()

        translated_text = translator.translate(text, dest=target_language).text

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(translated_text)

        print(f"✅ 번역 완료! 번역된 파일: {output_file}")

    except Exception as e:
        print(f"⚠️ 번역 중 오류 발생: {e}")


# 사용 예시
input_file = input("📄 번역할 텍스트 파일명을 입력하세요: ")
output_file = input("💾 번역된 내용을 저장할 파일명을 입력하세요: ")
target_language = input(
    "🌍 번역할 언어 코드(예: en, ko, ja, fr)를 입력하세요: "
).strip()

translate_text_file(input_file, output_file, target_language)
