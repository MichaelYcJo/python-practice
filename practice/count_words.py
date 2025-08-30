import argparse
import csv
import json
import logging
import re
import statistics
import sys
import time
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union
import warnings

# 선택적 의존성들
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ─────────────────────────────────────────
# 로깅 설정
# ─────────────────────────────────────────
def setup_logging(verbose: bool = False) -> None:
    """로깅 설정"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


# ─────────────────────────────────────────
# 설정 파일 지원
# ─────────────────────────────────────────
def load_config(config_file: Optional[Path] = None) -> Dict:
    """설정 파일 로드 (JSON/YAML 지원)"""
    if not config_file or not config_file.exists():
        return {}
    
    try:
        content = config_file.read_text(encoding='utf-8')
        if config_file.suffix.lower() in ['.yml', '.yaml'] and HAS_YAML:
            return yaml.safe_load(content) or {}
        else:
            return json.loads(content) or {}
    except (json.JSONDecodeError, yaml.YAMLError if HAS_YAML else Exception) as e:
        logging.warning("설정 파일 파싱 실패: %s", str(e))
        return {}


# ─────────────────────────────────────────
# 통계 정보 계산
# ─────────────────────────────────────────
def calculate_stats(counter: Counter) -> Dict[str, Union[int, float]]:
    """단어 빈도 통계 계산"""
    if not counter:
        return {}
    
    counts = list(counter.values())
    total_words = sum(counts)
    unique_words = len(counts)
    
    stats = {
        'total_words': total_words,
        'unique_words': unique_words,
        'max_frequency': max(counts),
        'min_frequency': min(counts),
        'mean_frequency': statistics.mean(counts),
        'median_frequency': statistics.median(counts),
        'vocabulary_richness': unique_words / total_words if total_words > 0 else 0
    }
    
    return stats


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
# ─────────────────────────────────────────
# 텍스트 정규화 & 토큰화 (개선됨)
# ─────────────────────────────────────────
def advanced_normalize_text(text: str, lower: bool = True, 
                           remove_punctuation: bool = True,
                           remove_extra_spaces: bool = True) -> str:
    """고급 텍스트 정규화"""
    # 유니코드 정규화 (NFKC): 전각/호환 문자 등 정리
    text = unicodedata.normalize("NFKC", text)
    
    if remove_punctuation:
        # 구두점 제거하되 단어 경계 유지
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
    
    if remove_extra_spaces:
        # 연속된 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
    
    if lower:
        text = text.lower()
    
    return text.strip()


def process_text_chunks(text: str, chunk_size: int = 10000) -> List[str]:
    """대용량 텍스트를 청크로 나누어 처리"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        # 청크 경계에서 단어가 잘리지 않도록 조정
        if i + chunk_size < len(text):
            last_space = chunk.rfind(' ')
            if last_space > chunk_size // 2:  # 청크가 너무 작아지지 않게
                chunk = chunk[:last_space]
        chunks.append(chunk)
    
    return chunks


def parallel_tokenize(text: str, keep_numbers: bool = True, 
                     chunk_size: int = 10000) -> List[str]:
    """병렬 처리로 토큰화 (대용량 텍스트용)"""
    chunks = process_text_chunks(text, chunk_size)
    
    if len(chunks) == 1:
        return tokenize(chunks[0], keep_numbers)
    
    all_tokens = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(tokenize, chunk, keep_numbers) for chunk in chunks]
        for future in as_completed(futures):
            all_tokens.extend(future.result())
    
    return all_tokens


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
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            # 파일 읽기 문제 시 조용히 기본셋만 사용
            logging.warning("불용어 파일 읽기 실패: %s", str(e))
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
# 시각화 (선택적)
# ─────────────────────────────────────────
def create_frequency_plot(rows: List[Tuple[str, int]], 
                         top_n: int = 20, 
                         save_path: Optional[Path] = None,
                         show: bool = False) -> None:
    """단어 빈도 막대 그래프 생성"""
    if not HAS_MATPLOTLIB:
        warnings.warn("matplotlib이 없어 시각화를 건너뜁니다.")
        return
    
    # 상위 N개만
    plot_data = rows[:top_n] if len(rows) > top_n else rows
    words, freqs = zip(*plot_data) if plot_data else ([], [])
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(range(len(words)), freqs)
    plt.xlabel('단어')
    plt.ylabel('빈도')
    plt.title(f'상위 {len(words)}개 단어 빈도')
    plt.xticks(range(len(words)), words, rotation=45, ha='right')
    
    # 막대 위에 숫자 표시
    for bar, freq in zip(bars, freqs):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(freqs)*0.01,
                str(freq), ha='center', va='bottom')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logging.info("그래프 저장됨: %s", str(save_path))
    
    if show:
        plt.show()
    else:
        plt.close()


# ─────────────────────────────────────────
# 입출력 (개선됨)
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


def print_enhanced_table(rows: List[Tuple[str, int]], 
                        stats: Optional[Dict] = None,
                        show_percentage: bool = False) -> None:
    """향상된 테이블 출력"""
    if not rows:
        print("📄 결과가 없습니다.")
        return
    
    total = sum(count for _, count in rows)
    
    # 헤더 출력
    if stats:
        print("� 통계 요약")
        print(f"   총 단어 수: {stats.get('total_words', 0):,}")
        print(f"   고유 단어 수: {stats.get('unique_words', 0):,}")
        print(f"   어휘 풍부도: {stats.get('vocabulary_richness', 0):.3f}")
        print(f"   평균 빈도: {stats.get('mean_frequency', 0):.1f}")
        print(f"   중앙값 빈도: {stats.get('median_frequency', 0):.1f}")
        print()
    
    print("📄 단어 빈도 순위")
    print("=" * 50)
    
    # 컬럼 폭 계산
    word_width = max((len(word) for word, _ in rows), default=10)
    word_width = max(word_width, 10)  # 최소 10자
    
    # 헤더
    header = f"{'순위':<4} {'단어':<{word_width}} {'빈도':<8}"
    if show_percentage:
        header += " {'비율':<8}"
    print(header)
    print("-" * len(header))
    
    # 데이터 행
    for i, (word, count) in enumerate(rows, 1):
        line = f"{i:<4} {word:<{word_width}} {count:<8}"
        if show_percentage:
            percentage = (count / total * 100) if total > 0 else 0
            line += f" {percentage:<7.2f}%"
        print(line)
    
    print("=" * 50)


def save_enhanced_output(rows: List[Tuple[str, int]], 
                        fmt: str, 
                        outpath: Path,
                        stats: Optional[Dict] = None,
                        metadata: Optional[Dict] = None) -> None:
    """향상된 파일 저장"""
    outpath.parent.mkdir(parents=True, exist_ok=True)
    
    if fmt == "json":
        data = {
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_entries": len(rows),
                **(metadata or {})
            },
            "statistics": stats or {},
            "results": [{"rank": i+1, "term": word, "count": count} 
                       for i, (word, count) in enumerate(rows)]
        }
        outpath.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    elif fmt == "csv":
        with outpath.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            # 헤더에 메타데이터 포함
            if metadata:
                w.writerow([f"# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}"])
                for key, value in metadata.items():
                    w.writerow([f"# {key}: {value}"])
                w.writerow([])
            
            w.writerow(["rank", "term", "count"])
            for i, (word, count) in enumerate(rows, 1):
                w.writerow([i, word, count])
    elif fmt == "txt":
        with outpath.open("w", encoding="utf-8") as f:
            if metadata:
                f.write(f"# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                for key, value in metadata.items():
                    f.write(f"# {key}: {value}\n")
                f.write("\n")
            
            if stats:
                f.write("# Statistics\n")
                for key, value in stats.items():
                    f.write(f"# {key}: {value}\n")
                f.write("\n")
            
            f.write("rank\tterm\tcount\n")
            for i, (word, count) in enumerate(rows, 1):
                f.write(f"{i}\t{word}\t{count}\n")
    else:
        raise ValueError(f"Unsupported output format: {fmt}")


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description="Enhanced Word Frequency Counter (multi-lang, n-gram, stopwords, visualization)"
    )
    src = ap.add_mutually_exclusive_group(required=False)
    src.add_argument("--text", type=str, help="직접 입력 텍스트")
    src.add_argument("--file", type=Path, help="텍스트 파일 경로")
    ap.add_argument("--encoding", default="utf-8", help="입력 파일 인코딩 (기본 utf-8)")
    ap.add_argument("--config", type=Path, help="설정 파일 경로 (JSON/YAML)")
    
    # 텍스트 전처리
    ap.add_argument(
        "--lower", action="store_true", help="소문자화 (기본: 켜짐)", default=True
    )
    ap.add_argument(
        "--no-lower", dest="lower", action="store_false", help="소문자화 끄기"
    )
    ap.add_argument(
        "--advanced-normalize", action="store_true", 
        help="고급 텍스트 정규화 사용", default=False
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
    
    # 출력 옵션
    ap.add_argument("--top", type=int, default=0, help="상위 N개만 출력 (0=전체)")
    ap.add_argument(
        "--sort-by", choices=["freq", "alpha"], default="freq", help="정렬 기준"
    )
    ap.add_argument("--asc", action="store_true", help="오름차순 정렬 (기본: 내림차순)")
    ap.add_argument("--show-stats", action="store_true", help="통계 정보 표시")
    ap.add_argument("--show-percentage", action="store_true", help="비율 표시")
    
    # 불용어
    ap.add_argument("--stopwords-file", type=Path, help="불용어 파일(.txt, 줄단위)")
    ap.add_argument(
        "--extra-stopwords", type=str, nargs="*", help="추가 불용어 (공백 구분)"
    )
    
    # 저장 옵션
    ap.add_argument("--output", choices=["json", "csv", "txt"], help="파일로 저장 포맷")
    ap.add_argument("--outpath", type=Path, help="저장 경로 (미지정 시 자동 생성)")
    
    # 시각화
    if HAS_MATPLOTLIB:
        ap.add_argument("--plot", action="store_true", help="막대 그래프 생성")
        ap.add_argument("--plot-path", type=Path, help="그래프 저장 경로")
        ap.add_argument("--show-plot", action="store_true", help="그래프 화면에 표시")
    
    # 기타
    ap.add_argument("--verbose", "-v", action="store_true", help="상세 로그 출력")
    ap.add_argument("--parallel", action="store_true", help="병렬 처리 사용 (대용량 파일)")

    args = ap.parse_args()
    
    # 로깅 설정
    setup_logging(args.verbose)
    
    # 설정 파일 로드
    config = load_config(args.config)
    logging.info("설정 로드 완료")

    try:
        start_time = time.time()
        text = read_input_text(
            file=args.file, encoding=args.encoding, text_arg=args.text
        )
        logging.info("텍스트 로드 완료: %d 문자", len(text))
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, IOError) as e:
        print(f"❌ 입력 오류: {e}")
        sys.exit(1)

    # 텍스트 정규화
    if args.advanced_normalize:
        text = advanced_normalize_text(text, lower=args.lower)
        logging.info("고급 텍스트 정규화 완료")
    else:
        # 기본 정규화
        text = unicodedata.normalize("NFKC", text)
        if args.lower:
            text = text.lower()
        logging.info("기본 텍스트 정규화 완료")
    
    # 토큰화 (병렬 처리 옵션)
    if args.parallel and len(text) > 50000:
        tokens = parallel_tokenize(text, keep_numbers=args.keep_numbers)
        logging.info("병렬 토큰화 완료: %d 토큰", len(tokens))
    else:
        tokens = tokenize(text, keep_numbers=args.keep_numbers)
        logging.info("토큰화 완료: %d 토큰", len(tokens))

    # 불용어 적용
    stopwords = build_stopwords(
        extra=args.extra_stopwords, stopwords_file=args.stopwords_file
    )
    tokens = apply_stopwords(tokens, stopwords, min_len=args.min_len)
    logging.info("불용어 필터링 완료: %d 토큰", len(tokens))

    # n-그램
    terms = make_ngrams(tokens, n=args.ngram)
    logging.info("n-그램 생성 완료: %d terms", len(terms))

    # 카운트 & 정렬
    counter = count_terms(terms)
    rows = sort_counts(counter, by=args.sort_by, desc=not args.asc)
    
    # 통계 계산
    stats = calculate_stats(counter) if args.show_stats else None
    
    processing_time = time.time() - start_time
    logging.info("처리 완료: %.2f초", processing_time)

    # 상위 N
    if args.top and args.top > 0:
        rows = rows[: args.top]

    # 출력
    print_enhanced_table(rows, stats, args.show_percentage)

    # 시각화
    if HAS_MATPLOTLIB and args.plot:
        create_frequency_plot(
            rows, 
            top_n=min(20, len(rows)),
            save_path=args.plot_path,
            show=args.show_plot
        )

    # 저장
    if args.output:
        outpath = args.outpath
        if not outpath:
            # 자동 파일명
            base = "word_freq"
            suffix = f"_{args.ngram}gram" if args.ngram > 1 else ""
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            outpath = Path(f"{base}{suffix}_{timestamp}.{args.output}")
        
        try:
            metadata = {
                "processing_time": f"{processing_time:.2f}s",
                "input_length": len(text),
                "ngram_size": args.ngram,
                "min_length": args.min_len,
                "total_terms": len(terms)
            }
            save_enhanced_output(rows, fmt=args.output, outpath=outpath, 
                               stats=stats, metadata=metadata)
            print(f"\n💾 저장 완료: {outpath}")
        except (IOError, OSError, PermissionError) as e:
            print(f"\n❌ 저장 실패: {e}")
            logging.error("저장 실패: %s", str(e), exc_info=True)


if __name__ == "__main__":
    main()
