import os
from googletrans import Translator, LANGUAGES

"""
자동 언어 감지 + 예외 처리 + 파일 크기 제한 + 최적화 추가
"""


def translate_text_file(input_file, target_language="en"):
    """텍스트 파일을 번역하여 저장하는 함수"""
    translator = Translator()

    # 파일 존재 여부 확인
    if not os.path.exists(input_file):
        print("❌ 오류: 해당 파일이 존재하지 않습니다.")
        return

    # 파일 크기 제한 (1MB 이상이면 경고)
    file_size = os.path.getsize(input_file)
    if file_size > 1 * 1024 * 1024:  # 1MB 이상이면 경고
        print("⚠️ 경고: 파일 크기가 너무 큽니다. 번역 성능이 저하될 수 있습니다.")

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # 자동 언어 감지
        detected_lang = translator.detect(lines[0]).lang
        print(f"🌍 감지된 원본 언어: {LANGUAGES.get(detected_lang, '알 수 없음')}")

        translated_lines = [
            translator.translate(line, src=detected_lang, dest=target_language).text
            for line in lines
        ]

        # 자동 출력 파일명 설정
        output_file = (
            f"{os.path.splitext(input_file)[0]}_translated_{target_language}.txt"
        )
        with open(output_file, "w", encoding="utf-8") as file:
            file.writelines("\n".join(translated_lines))

        print(f"✅ 번역 완료! 번역된 파일: {output_file}")

    except Exception as e:
        print(f"⚠️ 번역 중 오류 발생: {e}")


# 사용 예시
input_file = input("📄 번역할 텍스트 파일명을 입력하세요: ")
target_language = input(
    "🌍 번역할 언어 코드(예: en, ko, ja, fr)를 입력하세요: "
).strip()

translate_text_file(input_file, target_language)
