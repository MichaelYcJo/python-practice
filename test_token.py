import requests   # pip install requests

# TOKEN = ''
JWT_TOKEN = (
    # 한문자를 나눠쓰기 
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFt"
    "ZSI6InVzZXIxIiwiZXhwIjoxNTk3Mjk0NDA0LCJlbWFpbCI6IiIsIm9yaWdfaWF"
    "0IjoxNTk3Mjk0MTA0fQ.7Mi5kf3HHQT8tHNUCnPTsJHT3OYTGFbuG-fxop6vQkc"

)

headers = {
    # 'Authorization': f'Token {TOKEN}',  # Token 인증
    'Authorization': f'JWT {JWT_TOKEN}',  # JWT 인증
}

res = requests.get("http://localhost:8000/post/1/", headers=headers)
print(res.json())

# http POST http://localhost:8000/accounts/api-jwt-auth/ username=user1 password=user1   // httpie를 통한 토큰 발급 cli명령어 
# 콘솔에서 python test_token.py 으로 결과 확인 