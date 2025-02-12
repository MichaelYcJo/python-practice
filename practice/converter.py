def meter_to_kilometer(value):
    return value / 1000

def kilometer_to_meter(value):
    return value * 1000

def gram_to_kilogram(value):
    return value / 1000

def kilogram_to_gram(value):
    return value * 1000

def celsius_to_fahrenheit(value):
    return (value * 9/5) + 32

def fahrenheit_to_celsius(value):
    return (value - 32) * 5/9

def unit_converter():
    """단위 변환기 실행"""
    conversions = {
        "1": ("미터 ➡️ 킬로미터", meter_to_kilometer),
        "2": ("킬로미터 ➡️ 미터", kilometer_to_meter),
        "3": ("그램 ➡️ 킬로그램", gram_to_kilogram),
        "4": ("킬로그램 ➡️ 그램", kilogram_to_gram),
        "5": ("섭씨 ➡️ 화씨", celsius_to_fahrenheit),
        "6": ("화씨 ➡️ 섭씨", fahrenheit_to_celsius),
        "7": ("종료", None)
    }

    while True:
        print("\n🔄 단위 변환기")
        for key, (desc, _) in conversions.items():
            print(f"{key}. {desc}")
        
        choice = input("👉 변환할 항목을 선택하세요: ")
        
        if choice == "7":
            print("👋 프로그램을 종료합니다!")
            break
        elif choice in conversions:
            value = float(input("💡 변환할 값을 입력하세요: "))
            result = conversions[choice][1](value)
            print(f"✅ 변환 결과: {result:.2f}\n")
        else:
            print("⚠️ 올바른 선택지를 입력하세요.\n")

# 실행
unit_converter()