import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def read_excel(file_path):
    df = pd.read_excel(file_path)
    print("✅ 데이터 미리보기:")
    print(df.head())
    return df


def plot_chart(df, x_col, y_col, chart_type="bar"):
    plt.figure(figsize=(10, 6))

    if chart_type == "bar":
        plt.bar(df[x_col], df[y_col])
    elif chart_type == "line":
        plt.plot(df[x_col], df[y_col], marker="o")
    else:
        raise ValueError("지원하지 않는 차트 형식입니다. ('bar' 또는 'line')")

    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"{x_col} vs {y_col}")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    file_path = input("📄 Excel 파일 경로를 입력하세요: ").strip()
    if not Path(file_path).exists():
        print("❌ 파일이 존재하지 않습니다.")
        return

    df = read_excel(file_path)

    print("\n🧩 사용 가능한 컬럼 목록:")
    print(df.columns.tolist())

    x_col = input("👉 X축으로 사용할 컬럼명을 입력하세요: ").strip()
    y_col = input("👉 Y축으로 사용할 컬럼명을 입력하세요: ").strip()
    chart_type = input("📊 차트 유형 (bar 또는 line): ").strip()

    if x_col in df.columns and y_col in df.columns:
        plot_chart(df, x_col, y_col, chart_type)
    else:
        print("❗ 지정한 컬럼명이 올바르지 않습니다.")


if __name__ == "__main__":
    main()
