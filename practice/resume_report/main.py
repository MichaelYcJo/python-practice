import re
import json
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ResumeInfo:
    """이력서 정보를 저장하는 데이터 클래스"""
    name: Optional[str] = None
    emails: List[str] = None
    phones: List[str] = None
    skills: List[str] = None
    experience_years: Optional[int] = None
    education: List[str] = None
    projects: List[str] = None
    
    def __post_init__(self):
        if self.emails is None:
            self.emails = []
        if self.phones is None:
            self.phones = []
        if self.skills is None:
            self.skills = []
        if self.education is None:
            self.education = []
        if self.projects is None:
            self.projects = []

class ResumeAnalyzer:
    """이력서 분석기 클래스"""
    
    def __init__(self, skills_file: Optional[str] = None):
        self.skills_file = skills_file or "skills.json"
        self.skills_set = self._load_skills()
        
    def _load_skills(self) -> Set[str]:
        """스킬 리스트를 파일에서 로드"""
        default_skills = {
            "Python", "JavaScript", "React", "Node.js", "SQL", "Java", "C++", 
            "Docker", "Kubernetes", "AWS", "GCP", "Linux", "Django", "Flask", 
            "TypeScript", "Vue.js", "Angular", "MongoDB", "PostgreSQL", "Redis",
            "Git", "Jenkins", "Ansible", "Terraform", "Spring", "Express.js",
            "FastAPI", "GraphQL", "REST API", "Microservices", "CI/CD"
        }
        
        try:
            if Path(self.skills_file).exists():
                with open(self.skills_file, 'r', encoding='utf-8') as f:
                    skills_data = json.load(f)
                    return set(skills_data.get('skills', default_skills))
            else:
                # 기본 스킬 파일 생성
                with open(self.skills_file, 'w', encoding='utf-8') as f:
                    json.dump({'skills': list(default_skills)}, f, indent=2, ensure_ascii=False)
                return default_skills
        except Exception as e:
            logger.warning(f"스킬 파일 로드 실패: {e}, 기본 스킬 사용")
            return default_skills
    
    def extract_emails(self, text: str) -> List[str]:
        """이메일 주소 추출 (개선된 정규식)"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))  # 중복 제거
    
    def extract_phones(self, text: str) -> List[str]:
        """전화번호 추출 (다양한 형식 지원)"""
        phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',  # 미국 형식
            r'\+82[-.\s]?([0-9]{1,2})[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{4})',    # 한국 형식
            r'\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}'  # 일반 형식
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    phone = ''.join(match)
                else:
                    phone = match
                if len(phone) >= 10:  # 최소 10자리
                    phones.append(phone)
        
        return list(set(phones))
    
    def extract_name(self, text: str) -> Optional[str]:
        """이름 추출 (개선된 패턴 매칭)"""
        name_patterns = [
            r"(?:my name is|I'm|I am|name:)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",
            r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\s+(?:resume|CV|portfolio)",
            r"(?:contact|email|phone).*?([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",
            r"^([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",  # 첫 줄에 이름이 있는 경우
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # 이름 유효성 검사 (최소 2글자, 최대 50글자)
                if 2 <= len(name) <= 50 and not any(char.isdigit() for char in name):
                    return name
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """기술 스킬 추출 (개선된 매칭)"""
        found_skills = set()
        
        # 1. 직접 언급된 스킬 찾기
        for skill in self.skills_set:
            # 대소문자 구분 없이 매칭, 단어 경계 고려
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found_skills.add(skill)
        
        # 2. "Skills:" 섹션에서 추출
        skills_section = re.search(r'skills?[:\s]+([^.\n]+)', text, re.IGNORECASE)
        if skills_section:
            skills_text = skills_section.group(1)
            for skill in self.skills_set:
                if re.search(r'\b' + re.escape(skill) + r'\b', skills_text, re.IGNORECASE):
                    found_skills.add(skill)
        
        return sorted(list(found_skills))
    
    def extract_experience_years(self, text: str) -> Optional[int]:
        """경력 연차 추출"""
        experience_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*in\s+(?:development|programming|software)',
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                if 0 <= years <= 50:  # 합리적인 범위
                    return years
        return None
    
    def extract_education(self, text: str) -> List[str]:
        """학력 정보 추출"""
        education_patterns = [
            r'(?:Bachelor|Master|PhD|B\.S\.|M\.S\.|Ph\.D\.)[^.\n]*',
            r'(?:University|College|School)[^.\n]*',
            r'(?:Computer Science|Engineering|Information Technology)[^.\n]*',
        ]
        
        education = []
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.extend(matches)
        
        return list(set(education))
    
    def extract_projects(self, text: str) -> List[str]:
        """프로젝트 정보 추출"""
        project_patterns = [
            r'(?:project|developed|built|created)[^.\n]*',
            r'(?:GitHub|github\.com)[^.\n]*',
            r'(?:portfolio|showcase)[^.\n]*',
        ]
        
        projects = []
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            projects.extend(matches)
        
        return list(set(projects))
    
    def analyze_resume(self, text: str) -> ResumeInfo:
        """이력서 전체 분석"""
        if not text or not text.strip():
            raise ValueError("이력서 텍스트가 비어있습니다.")
        
        try:
            result = ResumeInfo(
                name=self.extract_name(text),
                emails=self.extract_emails(text),
                phones=self.extract_phones(text),
                skills=self.extract_skills(text),
                experience_years=self.extract_experience_years(text),
                education=self.extract_education(text),
                projects=self.extract_projects(text)
            )
            
            logger.info(f"이력서 분석 완료: {result.name or 'Unknown'}")
            return result
            
        except Exception as e:
            logger.error(f"이력서 분석 중 오류 발생: {e}")
            raise

def main():
    """메인 함수"""
    analyzer = ResumeAnalyzer()
    
    # 예제 이력서 텍스트
    resume_text = """
    Hello, I'm Jane Elizabeth Doe.
    You can reach me at jane.doe@example.com or jane@doe.dev.
    Contact: +1 (234) 567-8901 or +82-10-1234-5678.
    
    Skills: Python, JavaScript, React, SQL, Docker, Kubernetes, AWS.
    Experience: 5 years of software development experience.
    
    Education: Bachelor of Science in Computer Science from MIT.
    Projects: Built a microservices architecture using Docker and Kubernetes.
    
    Formerly at ACME Corp as a Senior Backend Developer.
    """
    
    try:
        result = analyzer.analyze_resume(resume_text)
        
        print("📋 이력서 분석 결과:\n")
        print(f"👤 이름: {result.name or '추출 실패'}")
        print(f"📧 이메일: {', '.join(result.emails) if result.emails else '없음'}")
        print(f"📞 전화번호: {', '.join(result.phones) if result.phones else '없음'}")
        print(f"💻 기술 스킬: {', '.join(result.skills) if result.skills else '없음'}")
        print(f"⏰ 경력: {result.experience_years}년" if result.experience_years else "경력: 정보 없음")
        print(f"🎓 학력: {', '.join(result.education) if result.education else '없음'}")
        print(f"🚀 프로젝트: {', '.join(result.projects) if result.projects else '없음'}")
        
        print("\n📄 JSON 형식:")
        print(json.dumps(result.__dict__, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()