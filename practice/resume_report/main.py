import re

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'\+?\d[\d\- ]{7,}\d', text)
    return match.group(0) if match else None

def extract_name(text):
    lines = text.strip().splitlines()
    for line in lines:
        if "name is" in line.lower():
            return line.split("is")[-1].strip().replace(".", "")
    return None

def extract_skills(text, skill_set):
    found_skills = []
    for skill in skill_set:
        if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
            found_skills.append(skill)
    return found_skills

def analyze_resume(text):
    skills = ["Python", "JavaScript", "React", "Node.js", "SQL", "Java", "Docker"]
    
    print("🔍 분석 결과:")
    print(f"👤 이름: {extract_name(text)}")
    print(f"📧 이메일: {extract_email(text)}")
    print(f"📱 전화번호: {extract_phone(text)}")
    print(f"💻 기술 스택: {', '.join(extract_skills(text, skills))}")

if __name__ == "__main__":
    # 샘플 이력서 텍스트 입력
    resume_text = """
    Hi, my name is Jane Doe.
    You can reach me at jane.doe@example.com or +1-234-567-8901.
    I'm experienced in Python, JavaScript, React, and SQL.
    Previously worked at XYZ Corp as a backend developer.
    """

    analyze_resume(resume_text)