# 개인 일기/메모 관리 시스템 📝

매일 새로운 기능을 추가할 수 있는 1일 1커밋 프로젝트입니다.

## 현재 기능

### 기본 기능
- ✅ 일기 작성, 읽기, 수정, 삭제
- ✅ 날짜별 일기 조회
- ✅ 고급 검색 (키워드, 기분, 태그, 날짜 범위)
- ✅ 기분 태그 시스템 (매우 좋음, 좋음, 보통, 나쁨, 매우 나쁨)
- ✅ 태그 시스템
- ✅ 단어 수 자동 계산
- ✅ 고급 통계 기능 (월별, 기분 분포)
- ✅ 에러 처리 및 로깅
- ✅ 자동 백업 시스템
- ✅ 입력 데이터 검증
- ✅ 일기 내보내기 (TXT, JSON)

## 사용법

### 1. 일기 작성
```bash
python main.py write --mood "좋음" --tags "운동" "건강"
```

### 2. 일기 읽기
```bash
# 오늘 일기 읽기
python main.py read

# 특정 날짜 일기 읽기
python main.py read --date 2024-01-15
```

### 3. 일기 검색
```bash
# 기본 키워드 검색
python main.py search --keyword "운동"

# 고급 검색 (기분, 태그, 날짜 범위)
python main.py search --keyword "운동" --mood "좋음" --tags "건강" "운동"
python main.py search --start-date "2024-01-01" --end-date "2024-01-31"
python main.py search --keyword "Python" --case-sensitive
```

### 4. 통계 보기
```bash
# 전체 통계
python main.py stats

# 특정 월 통계
python main.py stats --month 2024-01
```

### 5. 날짜 목록 보기
```bash
python main.py list
```

### 6. 일기 수정
```bash
# 대화형 수정
python main.py edit --id 2024-01-15_143022

# 명령줄로 직접 수정
python main.py edit --id 2024-01-15_143022 --content "새로운 내용" --new-mood "좋음" --new-tags "운동" "건강"
```

### 7. 일기 삭제
```bash
python main.py delete --id 2024-01-15_143022
```

### 8. 일기 상세 보기
```bash
python main.py show --id 2024-01-15_143022
```

### 9. 일기 내보내기
```bash
# 특정 일기 내보내기
python main.py export --id 2024-01-15_143022 --format txt
python main.py export --id 2024-01-15_143022 --format json

# 모든 일기 내보내기
python main.py export-all --format txt
python main.py export-all --format json
```

## 향후 추가 예정 기능 (1일 1커밋)

### Week 1: 기본 기능 완성 ✅
- [x] 일기 수정/삭제 기능
- [x] 일기 백업/복원 기능
- [x] 에러 처리 및 로깅
- [ ] 일기 내보내기 (PDF, TXT)

### Week 2: 검색 및 필터링 ✅
- [x] 고급 검색 (날짜 범위, 태그, 기분)
- [x] 대소문자 구분 검색
- [ ] 일기 정렬 기능
- [ ] 즐겨찾기 일기

### Week 3: 통계 및 분석 ✅
- [x] 월별/연도별 통계
- [x] 기분 분포 분석
- [x] 태그 빈도 분석
- [ ] 기분 변화 그래프
- [ ] 단어 빈도 분석
- [ ] 일기 작성 패턴 분석

### Week 4: UI 개선
- [ ] 웹 인터페이스 추가
- [ ] CLI 테마 시스템
- [ ] 일기 미리보기 기능

### Week 5: 고급 기능
- [ ] 일기 템플릿 시스템
- [ ] 자동 태그 제안
- [ ] 일기 연관성 분석
- [ ] 감정 분석 기능
- [x] 일기 내보내기 (TXT, JSON)

### Week 6: 데이터 관리
- [ ] 데이터베이스 연동
- [ ] 클라우드 동기화
- [ ] 다중 사용자 지원
- [ ] 데이터 암호화

## 프로젝트 구조

```
daily_diary/
├── main.py              # 메인 스크립트
├── README.md            # 프로젝트 문서
├── diary_data/          # 일기 데이터 저장소
│   └── diaries.json     # 일기 데이터 파일
└── requirements.txt     # 의존성 파일
```

## 설치 및 실행

1. 프로젝트 디렉토리로 이동
```bash
cd daily_diary
```

2. 스크립트 실행 권한 부여
```bash
chmod +x main.py
```

3. 일기 작성 시작
```bash
python main.py write
```

## 데이터 형식

일기 데이터는 JSON 형식으로 저장됩니다:

```json
{
  "2024-01-15": [
    {
      "id": "2024-01-15_143022",
      "date": "2024-01-15",
      "content": "오늘은 좋은 하루였다...",
      "mood": "좋음",
      "tags": ["운동", "건강"],
      "created_at": "2024-01-15T14:30:22.123456",
      "word_count": 25
    }
  ]
}
```

## 기여하기

이 프로젝트는 1일 1커밋을 목표로 하므로, 매일 새로운 기능이나 개선사항을 추가해보세요!

### 커밋 아이디어
- 새로운 기능 추가
- 기존 기능 개선
- 버그 수정
- 코드 리팩토링
- 문서 업데이트
- 테스트 추가
- 성능 최적화
