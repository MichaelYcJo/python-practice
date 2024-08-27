import os
from dotenv import load_dotenv
from pathlib import Path

# .env 파일 로드
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
