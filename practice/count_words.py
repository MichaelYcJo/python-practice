import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Tuple, Set


# ─────────────────────────────────────────
# 기본 불용어 (가볍게 시작, 필요시 확장)
# ─────────────────────────────────────────
DEFAULT_STOPWORDS_EN: Set[str] = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "if",
    "on",
    "in",
    "at",
    "of",
    "for",
    "to",
    "from",
    "by",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "with",
    "that",
    "this",
    "it",
    "its",
    "into",
    "about",
    "than",
    "then",
    "so",
    "such",
    "there",
    "their",
    "they",
    "them",
    "these",
    "those",
    "i",
    "you",
    "he",
    "she",
    "we",
    "us",
    "our",
    "your",
    "his",
    "her",
    "my",
    "me",
}
DEFAULT_STOPWORDS_KO: Set[str] = {
    "그리고",
    "그러나",
    "하지만",
    "또한",
    "및",
    "등",
    "이",
    "가",
    "은",
    "는",
    "을",
    "를",
    "의",
    "에",
    "에서",
    "으로",
    "와",
    "과",
    "하다",
    "했다",
    "합니다",
    "한다",
    "것",
    "수",
    "있다",
    "없다",
    "같다",
    "위해",
    "대한",
    "에서의",
    "하여",
    "이는",
}


# ─────────────────────────────────────────
# 텍스트 정규화 & 토큰화
# ─────────────────────────────────────────
def normalize_text(text: str, lower: bool = True) -> str:
    # 유니코드 정규화 (NFKC): 전각/호환 문자 등 정리
    text = unicodedata.normalize("NFKC", text)
    if lower:
        text = text.lower()
    return text


def tokenize(text: str, keep_numbers: bool = True) -> List[str]:
    """
    간단 멀티랭 토큰화:
    - 영문/숫자/한글 음절을 '단어'로 간주
    - 필요시 숫자 제거
    """
    # 영문/숫자/한글(가-힣)만 남기는 토큰화
    tokens = re.findall(r"[A-Za-z0-9가-힣]+", text)
    if not keep_numbers:
        tokens = [t for t in tokens if not t.isdigit()]
    return tokens


def build_stopwords(
    extra: Iterable[str] = None, stopwords_file: Path = None
) -> Set[str]:
    sw: Set[str] = set(DEFAULT_STOPWORDS_EN) | set(DEFAULT_STOPWORDS_KO)
    if stopwords_file and stopwords_file.exists():
        try:
            items = [
                line.strip()
                for line in stopwords_file.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            sw |= set(items)
        except Exception:
            # 파일 읽기 문제 시 조용히 기본셋만 사용
            pass
    if extra:
        sw |= {s.strip() for s in extra if s.strip()}
    return sw


def apply_stopwords(tokens: List[str], stopwords: Set[str], min_len: int) -> List[str]:
    # 길이 제한 & 불용어 제거
    return [t for t in tokens if len(t) >= min_len and t not in stopwords]


def make_ngrams(tokens: List[str], n: int) -> List[str]:
    if n <= 1:
        return tokens
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


# ─────────────────────────────────────────
# 카운팅 & 정렬
# ─────────────────────────────────────────
def count_terms(terms: List[str]) -> Counter:
    return Counter(terms)


def sort_counts(
    counter: Counter, by: str = "freq", desc: bool = True
) -> List[Tuple[str, int]]:
    items = list(counter.items())
    if by == "alpha":
        items.sort(key=lambda x: x[0], reverse=desc)
    else:  # freq
        items.sort(key=lambda x: x[1], reverse=desc)
    return items


# ─────────────────────────────────────────
# 입출력
# ─────────────────────────────────────────
def read_input_text(
    file: Path = None, encoding: str = "utf-8", text_arg: str = None
) -> str:
    if text_arg:
        return text_arg
    if file:
        return file.read_text(encoding=encoding, errors="ignore")
    # stdin 지원
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise ValueError("No input provided. Use --text or --file or pipe from stdin.")


def print_table(rows: List[Tuple[str, int]], total: int = None):
    # 콘솔 예쁘게
    if total is not None:
        print(f"📄 Total unique: {len(rows)}  |  Total tokens counted: {total}")
    width = max((len(k) for k, _ in rows), default=0)
    for k, v in rows:
        print(f"{k.ljust(width)}  {v}")


def save_output(rows: List[Tuple[str, int]], fmt: str, outpath: Path):
    outpath.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        data = [{"term": k, "count": v} for k, v in rows]
        outpath.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    elif fmt == "csv":
        with outpath.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["term", "count"])
            for k, v in rows:
                w.writerow([k, v])
    elif fmt == "txt":
        with outpath.open("w", encoding="utf-8") as f:
            for k, v in rows:
                f.write(f"{k}\t{v}\n")
    else:
        raise ValueError(f"Unsupported output format: {fmt}")


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description="Word Frequency Counter (multi-lang, n-gram, stopwords, JSON/CSV)"
    )
    src = ap.add_mutually_exclusive_group(required=False)
    src.add_argument("--text", type=str, help="직접 입력 텍스트")
    src.add_argument("--file", type=Path, help="텍스트 파일 경로")
    ap.add_argument("--encoding", default="utf-8", help="입력 파일 인코딩 (기본 utf-8)")
    ap.add_argument(
        "--lower", action="store_true", help="소문자화 (기본: 켜짐)", default=True
    )
    ap.add_argument(
        "--no-lower", dest="lower", action="store_false", help="소문자화 끄기"
    )
    ap.add_argument(
        "--keep-numbers",
        action="store_true",
        help="숫자 토큰 유지 (기본: 제거 안 함)",
        default=True,
    )
    ap.add_argument(
        "--drop-numbers",
        dest="keep_numbers",
        action="store_false",
        help="숫자 토큰 제거",
    )
    ap.add_argument("--min-len", type=int, default=2, help="최소 토큰 길이 (기본 2)")
    ap.add_argument(
        "--ngram", type=int, default=1, choices=[1, 2, 3], help="n-그램 크기 (1~3)"
    )
    ap.add_argument("--top", type=int, default=0, help="상위 N개만 출력 (0=전체)")
    ap.add_argument(
        "--sort-by", choices=["freq", "alpha"], default="freq", help="정렬 기준"
    )
    ap.add_argument("--asc", action="store_true", help="오름차순 정렬 (기본: 내림차순)")
    ap.add_argument("--stopwords-file", type=Path, help="불용어 파일(.txt, 줄단위)")
    ap.add_argument(
        "--extra-stopwords", type=str, nargs="*", help="추가 불용어 (공백 구분)"
    )
    ap.add_argument("--output", choices=["json", "csv", "txt"], help="파일로 저장 포맷")
    ap.add_argument("--outpath", type=Path, help="저장 경로 (미지정 시 자동 생성)")

    args = ap.parse_args()

    try:
        text = read_input_text(
            file=args.file, encoding=args.encoding, text_arg=args.text
        )
    except Exception as e:
        print(f"❌ 입력 오류: {e}")
        sys.exit(1)

    # 정규화 & 토큰화
    text = normalize_text(text, lower=args.lower)
    tokens = tokenize(text, keep_numbers=args.keep_numbers)

    # 불용어 적용
    stopwords = build_stopwords(
        extra=args.extra_stopwords, stopwords_file=args.stopwords_file
    )
    tokens = apply_stopwords(tokens, stopwords, min_len=args.min_len)

    # n-그램
    terms = make_ngrams(tokens, n=args.ngram)

    # 카운트 & 정렬
    counter = count_terms(terms)
    rows = sort_counts(counter, by=args.sort_by, desc=not args.asc)

    # 상위 N
    if args.top and args.top > 0:
        rows = rows[: args.top]

    # 콘솔 출력
    print_table(rows, total=sum(counter.values()))

    # 저장
    if args.output:
        outpath = args.outpath
        if not outpath:
            # 자동 파일명
            base = "word_freq"
            suffix = f"_{args.ngram}gram" if args.ngram > 1 else ""
            outpath = Path(f"{base}{suffix}.{args.output}")
        try:
            save_output(rows, fmt=args.output, outpath=outpath)
            print(f"\n💾 저장 완료: {outpath}")
        except Exception as e:
            print(f"\n❌ 저장 실패: {e}")


if __name__ == "__main__":
    main()
