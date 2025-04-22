def calculate_bmi(height_cm, weight_kg):
    height_m = height_cm / 100  # cm -> m
    bmi = weight_kg / (height_m**2)
    return bmi


def classify_bmi(bmi):
    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상 체중"
    elif bmi < 25:
        return "과체중"
    elif bmi < 30:
        return "비만"
    else:
        return "고도 비만"


def main():
    print("=== 🧮 BMI 계산기 ===")

    try:
        height = float(input("당신의 키(cm)를 입력하세요: ").strip())
        weight = float(input("당신의 몸무게(kg)를 입력하세요: ").strip())

        # 입력값 유효성 체크
        if height <= 0 or weight <= 0:
            print("❗ 키와 몸무게는 0보다 큰 값을 입력해야 합니다.")
            return

        bmi = calculate_bmi(height, weight)
        status = classify_bmi(bmi)

        print(f"\n👉 당신의 BMI는 {bmi:.2f}입니다.")
        print(f"🏷️ 건강 상태: {status}")

    except ValueError:
        print("❗ 숫자를 정확히 입력해주세요.")


if __name__ == "__main__":
    main()
