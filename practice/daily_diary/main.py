#!/usr/bin/env python3
"""
개인 일기/메모 관리 시스템
매일 새로운 기능을 추가할 수 있는 프로젝트

기능:
- 일기 작성, 읽기, 수정, 삭제
- 날짜별 검색
- 키워드 검색
- 통계 기능
- 데이터 내보내기/가져오기
"""

import json
import os
import sys
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Any
import argparse
import logging
import traceback
from contextlib import contextmanager


class DailyDiary:
    """개인 일기 관리 클래스"""
    
    def __init__(self, data_dir: str = "diary_data"):
        self.data_dir = Path(data_dir)
        self.diary_file = self.data_dir / "diaries.json"
        self.backup_dir = self.data_dir / "backups"
        self._setup_logging()
        self._ensure_directories()
        self.load_diaries()
    
    def _setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.data_dir / 'diary.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _ensure_directories(self):
        """필요한 디렉토리 생성"""
        try:
            self.data_dir.mkdir(exist_ok=True)
            self.backup_dir.mkdir(exist_ok=True)
        except PermissionError:
            self.logger.error(f"디렉토리 생성 권한이 없습니다: {self.data_dir}")
            raise
        except Exception as e:
            self.logger.error(f"디렉토리 생성 중 오류 발생: {e}")
            raise
    
    def load_diaries(self) -> None:
        """저장된 일기 데이터 로드"""
        try:
            if self.diary_file.exists():
                with open(self.diary_file, 'r', encoding='utf-8') as f:
                    self.diaries = json.load(f)
                self.logger.info(f"일기 데이터 로드 완료: {len(self.diaries)}개 날짜")
            else:
                self.diaries = {}
                self.logger.info("새로운 일기 데이터베이스 생성")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 파일 손상: {e}")
            self._create_backup()
            self.diaries = {}
            print("⚠️  일기 데이터 파일이 손상되었습니다. 백업을 생성하고 새로 시작합니다.")
        except PermissionError:
            self.logger.error("파일 읽기 권한이 없습니다.")
            raise
        except Exception as e:
            self.logger.error(f"데이터 로드 중 오류 발생: {e}")
            raise
    
    def save_diaries(self) -> None:
        """일기 데이터 저장"""
        try:
            # 백업 생성
            self._create_backup()
            
            # 임시 파일에 먼저 저장
            temp_file = self.diary_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.diaries, f, ensure_ascii=False, indent=2)
            
            # 원자적 이동 (파일 손상 방지)
            temp_file.replace(self.diary_file)
            self.logger.info("일기 데이터 저장 완료")
            
        except PermissionError:
            self.logger.error("파일 쓰기 권한이 없습니다.")
            raise
        except Exception as e:
            self.logger.error(f"데이터 저장 중 오류 발생: {e}")
            raise
    
    def _create_backup(self) -> None:
        """데이터 백업 생성"""
        if self.diary_file.exists():
            backup_file = self.backup_dir / f"diaries_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                import shutil
                shutil.copy2(self.diary_file, backup_file)
                self.logger.info(f"백업 생성 완료: {backup_file}")
            except Exception as e:
                self.logger.warning(f"백업 생성 실패: {e}")
    
    def write_diary(self, content: str, mood: str = "보통", tags: List[str] = None) -> str:
        """새 일기 작성"""
        today = date.today().isoformat()
        diary_id = f"{today}_{datetime.now().strftime('%H%M%S')}"
        
        diary_entry = {
            "id": diary_id,
            "date": today,
            "content": content,
            "mood": mood,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "word_count": len(content.split())
        }
        
        if today not in self.diaries:
            self.diaries[today] = []
        
        self.diaries[today].append(diary_entry)
        self.save_diaries()
        
        return diary_id
    
    def read_diary(self, target_date: str = None) -> List[Dict]:
        """특정 날짜의 일기 읽기"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        return self.diaries.get(target_date, [])
    
    def search_diaries(self, keyword: str = None, mood: str = None, tags: List[str] = None, 
                      start_date: str = None, end_date: str = None, case_sensitive: bool = False) -> List[Dict]:
        """고급 일기 검색"""
        results = []
        
        for date_str, diaries in self.diaries.items():
            # 날짜 범위 필터링
            if start_date and date_str < start_date:
                continue
            if end_date and date_str > end_date:
                continue
            
            for diary in diaries:
                match = True
                
                # 키워드 검색
                if keyword:
                    content = diary["content"]
                    if not case_sensitive:
                        content = content.lower()
                        keyword = keyword.lower()
                    if keyword not in content:
                        match = False
                
                # 기분 검색
                if mood and diary["mood"] != mood:
                    match = False
                
                # 태그 검색
                if tags:
                    diary_tags = set(diary.get("tags", []))
                    if not any(tag in diary_tags for tag in tags):
                        match = False
                
                if match:
                    results.append(diary)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """일기 통계 정보"""
        total_diaries = sum(len(diaries) for diaries in self.diaries.values())
        total_words = sum(
            diary.get("word_count", 0) 
            for diaries in self.diaries.values() 
            for diary in diaries
        )
        
        # 가장 많이 사용된 태그
        all_tags = []
        for diaries in self.diaries.values():
            for diary in diaries:
                all_tags.extend(diary.get("tags", []))
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        most_used_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 기분 통계
        mood_counts = {}
        for diaries in self.diaries.values():
            for diary in diaries:
                mood = diary.get("mood", "보통")
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # 월별 통계
        monthly_stats = self._get_monthly_statistics()
        
        return {
            "total_diaries": total_diaries,
            "total_words": total_words,
            "total_days": len(self.diaries),
            "most_used_tags": most_used_tags,
            "mood_distribution": mood_counts,
            "monthly_stats": monthly_stats,
            "average_words_per_diary": total_words / total_diaries if total_diaries > 0 else 0
        }
    
    def _get_monthly_statistics(self) -> Dict[str, Dict[str, Any]]:
        """월별 통계 계산"""
        monthly_data = {}
        
        for date_str, diaries in self.diaries.items():
            year_month = date_str[:7]  # YYYY-MM
            
            if year_month not in monthly_data:
                monthly_data[year_month] = {
                    "diary_count": 0,
                    "word_count": 0,
                    "moods": {},
                    "tags": []
                }
            
            monthly_data[year_month]["diary_count"] += len(diaries)
            
            for diary in diaries:
                monthly_data[year_month]["word_count"] += diary.get("word_count", 0)
                
                # 기분 통계
                mood = diary.get("mood", "보통")
                monthly_data[year_month]["moods"][mood] = monthly_data[year_month]["moods"].get(mood, 0) + 1
                
                # 태그 수집
                monthly_data[year_month]["tags"].extend(diary.get("tags", []))
        
        # 태그 빈도 계산
        for month_data in monthly_data.values():
            tag_counts = {}
            for tag in month_data["tags"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            month_data["top_tags"] = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            del month_data["tags"]  # 원본 태그 리스트는 삭제
        
        return monthly_data
    
    def list_dates(self) -> List[str]:
        """일기가 있는 날짜 목록"""
        return sorted(self.diaries.keys(), reverse=True)
    
    def edit_diary(self, diary_id: str, new_content: str = None, new_mood: str = None, new_tags: List[str] = None) -> bool:
        """일기 수정"""
        try:
            for date_str, diaries in self.diaries.items():
                for i, diary in enumerate(diaries):
                    if diary["id"] == diary_id:
                        if new_content is not None:
                            diary["content"] = new_content
                            diary["word_count"] = len(new_content.split())
                        if new_mood is not None:
                            diary["mood"] = new_mood
                        if new_tags is not None:
                            diary["tags"] = new_tags
                        diary["updated_at"] = datetime.now().isoformat()
                        
                        self.save_diaries()
                        self.logger.info(f"일기 수정 완료: {diary_id}")
                        return True
            return False
        except Exception as e:
            self.logger.error(f"일기 수정 중 오류 발생: {e}")
            return False
    
    def delete_diary(self, diary_id: str) -> bool:
        """일기 삭제"""
        try:
            for date_str, diaries in self.diaries.items():
                for i, diary in enumerate(diaries):
                    if diary["id"] == diary_id:
                        del diaries[i]
                        if not diaries:  # 해당 날짜에 일기가 없으면 날짜도 삭제
                            del self.diaries[date_str]
                        self.save_diaries()
                        self.logger.info(f"일기 삭제 완료: {diary_id}")
                        return True
            return False
        except Exception as e:
            self.logger.error(f"일기 삭제 중 오류 발생: {e}")
            return False
    
    def get_diary_by_id(self, diary_id: str) -> Optional[Dict]:
        """ID로 일기 조회"""
        for diaries in self.diaries.values():
            for diary in diaries:
                if diary["id"] == diary_id:
                    return diary
        return None
    
    def validate_date(self, date_str: str) -> bool:
        """날짜 형식 검증"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def validate_mood(self, mood: str) -> bool:
        """기분 값 검증"""
        valid_moods = ["매우 좋음", "좋음", "보통", "나쁨", "매우 나쁨"]
        return mood in valid_moods
    
    def export_diary(self, diary_id: str, format: str = "txt") -> str:
        """일기 내보내기"""
        diary_entry = self.get_diary_by_id(diary_id)
        if not diary_entry:
            return None
        
        export_dir = self.data_dir / "exports"
        export_dir.mkdir(exist_ok=True)
        
        if format == "txt":
            filename = f"diary_{diary_id}.txt"
            filepath = export_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"일기 ID: {diary_entry['id']}\n")
                f.write(f"날짜: {diary_entry['date']}\n")
                f.write(f"기분: {diary_entry['mood']}\n")
                f.write(f"태그: {', '.join(diary_entry['tags'])}\n")
                f.write(f"단어 수: {diary_entry['word_count']}\n")
                f.write(f"작성 시간: {diary_entry['created_at']}\n")
                if 'updated_at' in diary_entry:
                    f.write(f"수정 시간: {diary_entry['updated_at']}\n")
                f.write("\n" + "="*50 + "\n")
                f.write(diary_entry['content'])
            
            return str(filepath)
        
        elif format == "json":
            filename = f"diary_{diary_id}.json"
            filepath = export_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(diary_entry, f, ensure_ascii=False, indent=2)
            
            return str(filepath)
        
        return None
    
    def export_all_diaries(self, format: str = "txt") -> str:
        """모든 일기 내보내기"""
        export_dir = self.data_dir / "exports"
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == "txt":
            filename = f"all_diaries_{timestamp}.txt"
            filepath = export_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=== 모든 일기 모음 ===\n\n")
                
                for date_str in sorted(self.diaries.keys()):
                    f.write(f"📅 {date_str}\n")
                    f.write("="*50 + "\n")
                    
                    for diary in self.diaries[date_str]:
                        f.write(f"\n[ID: {diary['id']}]\n")
                        f.write(f"기분: {diary['mood']}\n")
                        f.write(f"태그: {', '.join(diary['tags'])}\n")
                        f.write(f"단어 수: {diary['word_count']}\n")
                        f.write(f"작성 시간: {diary['created_at']}\n")
                        if 'updated_at' in diary:
                            f.write(f"수정 시간: {diary['updated_at']}\n")
                        f.write(f"\n내용:\n{diary['content']}\n")
                        f.write("\n" + "-"*30 + "\n")
                    
                    f.write("\n\n")
            
            return str(filepath)
        
        elif format == "json":
            filename = f"all_diaries_{timestamp}.json"
            filepath = export_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.diaries, f, ensure_ascii=False, indent=2)
            
            return str(filepath)
        
        return None


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="개인 일기 관리 시스템")
    parser.add_argument("command", choices=["write", "read", "search", "stats", "list", "edit", "delete", "show", "export", "export-all"], 
                       help="실행할 명령어")
    parser.add_argument("--date", help="날짜 (YYYY-MM-DD 형식)")
    parser.add_argument("--keyword", help="검색할 키워드")
    parser.add_argument("--mood", default="보통", help="기분 (기본값: 보통)")
    parser.add_argument("--tags", nargs="*", help="태그들")
    parser.add_argument("--id", help="일기 ID")
    parser.add_argument("--content", help="새로운 내용")
    parser.add_argument("--new-mood", help="새로운 기분")
    parser.add_argument("--new-tags", nargs="*", help="새로운 태그들")
    parser.add_argument("--start-date", help="검색 시작 날짜 (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="검색 종료 날짜 (YYYY-MM-DD)")
    parser.add_argument("--case-sensitive", action="store_true", help="대소문자 구분 검색")
    parser.add_argument("--format", choices=["txt", "json"], default="txt", help="내보내기 형식")
    parser.add_argument("--month", help="월별 통계 (YYYY-MM 형식)")
    
    args = parser.parse_args()
    
    diary = DailyDiary()
    
    if args.command == "write":
        # 기분 검증
        if not diary.validate_mood(args.mood):
            print(f"❌ 잘못된 기분입니다. 사용 가능한 기분: 매우 좋음, 좋음, 보통, 나쁨, 매우 나쁨")
            return
        
        print("일기를 작성하세요 (종료하려면 'quit' 입력):")
        content_lines = []
        while True:
            line = input()
            if line.strip() == "quit":
                break
            content_lines.append(line)
        
        content = "\n".join(content_lines).strip()
        if content:
            # 태그 중복 제거 및 정리
            clean_tags = list(set([tag.strip() for tag in (args.tags or []) if tag.strip()]))
            
            diary_id = diary.write_diary(content, args.mood, clean_tags)
            print(f"✅ 일기가 저장되었습니다! ID: {diary_id}")
        else:
            print("❌ 내용이 없어서 저장하지 않았습니다.")
    
    elif args.command == "read":
        # 날짜 검증
        if args.date and not diary.validate_date(args.date):
            print(f"❌ 잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력하세요.")
            return
        
        diaries = diary.read_diary(args.date)
        if diaries:
            print(f"\n=== {args.date or date.today().isoformat()} 일기 ===")
            for diary_entry in diaries:
                print(f"\n[ID: {diary_entry['id']}]")
                print(f"기분: {diary_entry['mood']}")
                print(f"태그: {', '.join(diary_entry['tags'])}")
                print(f"단어 수: {diary_entry['word_count']}")
                print(f"작성 시간: {diary_entry['created_at']}")
                print(f"내용:\n{diary_entry['content']}")
                print("-" * 50)
        else:
            print("해당 날짜에 일기가 없습니다.")
    
    elif args.command == "search":
        # 날짜 범위 검증
        if args.start_date and not diary.validate_date(args.start_date):
            print(f"❌ 잘못된 시작 날짜 형식입니다. YYYY-MM-DD 형식으로 입력하세요.")
            return
        if args.end_date and not diary.validate_date(args.end_date):
            print(f"❌ 잘못된 종료 날짜 형식입니다. YYYY-MM-DD 형식으로 입력하세요.")
            return
        
        # 기분 검증
        if args.mood and not diary.validate_mood(args.mood):
            print(f"❌ 잘못된 기분입니다. 사용 가능한 기분: 매우 좋음, 좋음, 보통, 나쁨, 매우 나쁨")
            return
        
        results = diary.search_diaries(
            keyword=args.keyword,
            mood=args.mood if args.mood != "보통" else None,
            tags=args.tags,
            start_date=args.start_date,
            end_date=args.end_date,
            case_sensitive=args.case_sensitive
        )
        
        if results:
            print(f"\n=== 검색 결과 ({len(results)}개) ===")
            if args.keyword:
                print(f"키워드: '{args.keyword}'")
            if args.mood and args.mood != "보통":
                print(f"기분: {args.mood}")
            if args.tags:
                print(f"태그: {', '.join(args.tags)}")
            if args.start_date or args.end_date:
                print(f"날짜 범위: {args.start_date or '시작'} ~ {args.end_date or '종료'}")
            if args.case_sensitive:
                print("대소문자 구분: 예")
            
            print("\n" + "="*60)
            for diary_entry in results:
                print(f"\n📅 [날짜: {diary_entry['date']}] [ID: {diary_entry['id']}]")
                print(f"😊 기분: {diary_entry['mood']}")
                if diary_entry['tags']:
                    print(f"🏷️  태그: {', '.join(diary_entry['tags'])}")
                print(f"📝 내용: {diary_entry['content'][:100]}...")
                print("-" * 60)
        else:
            print("❌ 검색 결과가 없습니다.")
    
    elif args.command == "stats":
        stats = diary.get_statistics()
        
        if args.month:
            # 특정 월 통계
            if args.month in stats['monthly_stats']:
                month_data = stats['monthly_stats'][args.month]
                print(f"\n=== {args.month} 월별 통계 ===")
                print(f"일기 수: {month_data['diary_count']}개")
                print(f"총 단어 수: {month_data['word_count']}개")
                print(f"평균 단어 수: {month_data['word_count'] / month_data['diary_count']:.1f}개")
                
                print("\n기분 분포:")
                for mood, count in month_data['moods'].items():
                    print(f"  {mood}: {count}회")
                
                if month_data['top_tags']:
                    print("\n인기 태그:")
                    for tag, count in month_data['top_tags']:
                        print(f"  {tag}: {count}회")
            else:
                print(f"❌ {args.month} 월의 데이터가 없습니다.")
        else:
            # 전체 통계
            print("\n=== 전체 일기 통계 ===")
            print(f"📊 총 일기 수: {stats['total_diaries']}개")
            print(f"📝 총 단어 수: {stats['total_words']}개")
            print(f"📅 일기를 쓴 날: {stats['total_days']}일")
            print(f"📈 일기당 평균 단어 수: {stats['average_words_per_diary']:.1f}개")
            
            if stats['mood_distribution']:
                print("\n😊 기분 분포:")
                for mood, count in stats['mood_distribution'].items():
                    percentage = (count / stats['total_diaries']) * 100
                    print(f"  {mood}: {count}회 ({percentage:.1f}%)")
            
            if stats['most_used_tags']:
                print("\n🏷️  인기 태그:")
                for tag, count in stats['most_used_tags']:
                    print(f"  {tag}: {count}회")
            
            if stats['monthly_stats']:
                print("\n📅 월별 요약:")
                for month, data in sorted(stats['monthly_stats'].items()):
                    print(f"  {month}: {data['diary_count']}개 일기, {data['word_count']}단어")
    
    elif args.command == "list":
        dates = diary.list_dates()
        if dates:
            print("\n=== 일기가 있는 날짜 목록 ===")
            for date_str in dates:
                diary_count = len(diary.diaries[date_str])
                print(f"{date_str} ({diary_count}개 일기)")
        else:
            print("아직 작성된 일기가 없습니다.")
    
    elif args.command == "edit":
        if not args.id:
            print("수정할 일기 ID를 입력하세요: --id 일기ID")
            return
        
        diary_entry = diary.get_diary_by_id(args.id)
        if not diary_entry:
            print(f"일기를 찾을 수 없습니다: {args.id}")
            return
        
        print(f"\n=== 일기 수정 (ID: {args.id}) ===")
        print(f"현재 내용: {diary_entry['content'][:100]}...")
        print(f"현재 기분: {diary_entry['mood']}")
        print(f"현재 태그: {', '.join(diary_entry['tags'])}")
        
        # 내용 수정
        if args.content:
            new_content = args.content
        else:
            print("\n새로운 내용을 입력하세요 (변경하지 않으려면 Enter):")
            new_content = input().strip()
            if not new_content:
                new_content = None
        
        # 기분 수정
        if args.new_mood:
            new_mood = args.new_mood
        else:
            print(f"\n새로운 기분을 입력하세요 (현재: {diary_entry['mood']}, 변경하지 않으려면 Enter):")
            new_mood = input().strip()
            if not new_mood:
                new_mood = None
        
        # 태그 수정
        if args.new_tags:
            new_tags = args.new_tags
        else:
            print(f"\n새로운 태그를 입력하세요 (현재: {', '.join(diary_entry['tags'])}, 변경하지 않으려면 Enter):")
            new_tags_input = input().strip()
            if new_tags_input:
                new_tags = [tag.strip() for tag in new_tags_input.split(',')]
            else:
                new_tags = None
        
        success = diary.edit_diary(args.id, new_content, new_mood, new_tags)
        if success:
            print("✅ 일기가 성공적으로 수정되었습니다!")
        else:
            print("❌ 일기 수정에 실패했습니다.")
    
    elif args.command == "delete":
        if not args.id:
            print("삭제할 일기 ID를 입력하세요: --id 일기ID")
            return
        
        diary_entry = diary.get_diary_by_id(args.id)
        if not diary_entry:
            print(f"일기를 찾을 수 없습니다: {args.id}")
            return
        
        print(f"\n=== 일기 삭제 확인 ===")
        print(f"날짜: {diary_entry['date']}")
        print(f"내용: {diary_entry['content'][:100]}...")
        print(f"기분: {diary_entry['mood']}")
        
        confirm = input("\n정말로 이 일기를 삭제하시겠습니까? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            success = diary.delete_diary(args.id)
            if success:
                print("✅ 일기가 성공적으로 삭제되었습니다!")
            else:
                print("❌ 일기 삭제에 실패했습니다.")
        else:
            print("삭제가 취소되었습니다.")
    
    elif args.command == "show":
        if not args.id:
            print("조회할 일기 ID를 입력하세요: --id 일기ID")
            return
        
        diary_entry = diary.get_diary_by_id(args.id)
        if diary_entry:
            print(f"\n=== 일기 상세 보기 ===")
            print(f"ID: {diary_entry['id']}")
            print(f"날짜: {diary_entry['date']}")
            print(f"기분: {diary_entry['mood']}")
            print(f"태그: {', '.join(diary_entry['tags'])}")
            print(f"단어 수: {diary_entry['word_count']}")
            print(f"작성 시간: {diary_entry['created_at']}")
            if 'updated_at' in diary_entry:
                print(f"수정 시간: {diary_entry['updated_at']}")
            print(f"\n내용:\n{diary_entry['content']}")
        else:
            print(f"일기를 찾을 수 없습니다: {args.id}")
    
    elif args.command == "export":
        if not args.id:
            print("내보낼 일기 ID를 입력하세요: --id 일기ID")
            return
        
        filepath = diary.export_diary(args.id, args.format)
        if filepath:
            print(f"✅ 일기가 내보내기되었습니다: {filepath}")
        else:
            print(f"❌ 일기를 찾을 수 없습니다: {args.id}")
    
    elif args.command == "export-all":
        filepath = diary.export_all_diaries(args.format)
        if filepath:
            print(f"✅ 모든 일기가 내보내기되었습니다: {filepath}")
        else:
            print("❌ 내보내기에 실패했습니다.")


if __name__ == "__main__":
    main()
