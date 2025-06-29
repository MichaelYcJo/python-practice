import re
import json

def extract_emails(text):
    return re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)

def extract_phones(text):
    return re.findall(r'\+?\d[\d\- ()]{7,}\d', text)

def extract_name(text):
    patterns = [
        r"(?:my name is|I'm|I am)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)",  # 이름은 일반적으로 대문자 시작
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_skills(text, predefined_skills):
    # 콤마로 구분된 기술 리스트 추출
    possible_skills = re.findall(r'([A-Za-z+#]+)', text)
    found = set()
    for skill in predefined_skills:
        if skill.lower() in [s.lower() for s in possible_skills]:
            found.add(skill)
    return list(found)

def analyze_resume(text):
    skill_set = [
        "Python", "JavaScript", "React", "Node.js", "SQL", "Java", "C++", "Docker",
        "Kubernetes", "AWS", "GCP", "Linux", "Django", "Flask", "TypeScript"
    ]

    result = {
        "name": extract_name(text),
        "emails": extract_emails(text),
        "phones": extract_phones(text),
        "skills": extract_skills(text, skill_set),
    }

    return result

def main():
    # 예제 이력서 텍스트
    resume_text = """
    Hello, I'm Jane Elizabeth Doe.
    You can reach me at jane.doe@example.com or jane@doe.dev.
    Contact: +1 (234) 567-8901 or +82-10-1234-5678.
    Skills: Python, JavaScript, React, SQL, Docker, Kubernetes.
    Formerly at ACME Corp.
    """

    result = analyze_resume(resume_text)
    print("📋 분석 결과 (JSON):\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()