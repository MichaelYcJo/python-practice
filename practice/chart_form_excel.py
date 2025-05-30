import pandas as pd
import matplotlib.pyplot as plt


def main():
    # 📂 엑셀 파일 로드
    file_path = input("📄 엑셀 파일 경로를 입력하세요 (예: data.xlsx): ").strip()
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ 엑셀 파일을 불러오는 데 실패했습니다: {e}")
        return

    print(f"✅ 컬럼 목록: {list(df.columns)}")

    # 📊 X축, Y축 컬럼 선택
    x_col = input("👉 X축으로 사용할 컬럼명을 입력하세요: ").strip()
    y_col = input("👉 Y축으로 사용할 컬럼명을 입력하세요: ").strip()

    if x_col not in df.columns or y_col not in df.columns:
        print("⚠️ 입력한 컬럼명이 엑셀에 없습니다.")
        return

    # 🖼️ 차트 그리기
    plt.figure(figsize=(10, 6))
    plt.bar(df[x_col], df[y_col])
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"{y_col} by {x_col}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 💾 저장 여부 선택
    save_choice = (
        input("💾 차트를 이미지 파일로 저장하시겠습니까? (y/n): ").strip().lower()
    )
    if save_choice == "y":
        save_path = input("저장할 파일명을 입력하세요 (예: chart.png): ").strip()
        try:
            plt.savefig(save_path)
            print(f"✅ 차트가 {save_path}로 저장되었습니다.")
        except Exception as e:
            print(f"❌ 저장 중 오류 발생: {e}")
    else:
        print("🖼️ 차트를 화면에 표시합니다.")
        plt.show()


if __name__ == "__main__":
    main()
