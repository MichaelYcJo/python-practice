from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

# uvicorn main:app --reload

# FastAPI 애플리케이션
app = FastAPI()

# Logger 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 스케줄러 인스턴스 생성
scheduler = BackgroundScheduler()


# 매일 00시에 실행될 작업
def daily_task():
    logger.info(f"Daily Task executed at {datetime.now()}")


# FastAPI 애플리케이션 시작 시 스케줄러 시작
@app.on_event("startup")
async def start_scheduler():
    # 스케줄러에 작업 추가
    scheduler.add_job(
        daily_task,  # 실행할 함수
        trigger=CronTrigger(hour=23, minute=10),  # 매일 00:00에 실행
        id="daily_task",  # 작업 ID
        replace_existing=True,  # 동일 ID의 작업이 있으면 대체
    )
    scheduler.start()
    logger.info("Scheduler started.")


# FastAPI 애플리케이션 종료 시 스케줄러 정지
@app.on_event("shutdown")
async def stop_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler stopped.")


# 간단한 라우트 예제
@app.get("/")
async def root():
    return {"message": "Hello, APScheduler with CronTrigger!"}
