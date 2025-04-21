def calculate_bmi(height_cm, weight_kg):
    height_m = height_cm / 100  # cm를 m로 변환
    bmi = weight_kg / (height_m**2)
    return bmi


def main():
    print("=== 🧮 BMI 계산기 ===")

    try:
        height = float(input("당신의 키(cm)를 입력하세요: ").strip())
        weight = float(input("당신의 몸무게(kg)를 입력하세요: ").strip())

        bmi = calculate_bmi(height, weight)
        print(f"👉 당신의 BMI는 {bmi:.2f}입니다.")

    except ValueError:
        print("❗ 숫자를 정확히 입력해주세요.")


if __name__ == "__main__":
    main()
