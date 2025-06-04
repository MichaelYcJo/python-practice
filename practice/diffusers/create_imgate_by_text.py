# pip install diffusers transformers accelerate safetensors
# 모델 다운로드 경로 ~/.cache/huggingface/hub

import torch
from diffusers import StableDiffusionPipeline
import gc
import warnings
from datetime import datetime
import os
import logging
from typing import Optional, Tuple

warnings.filterwarnings("ignore", message="resource_tracker: There appear to be .*")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SAVE_DIR = "generated_images"
os.makedirs(SAVE_DIR, exist_ok=True)

class ImageGenerationError(Exception):
    """이미지 생성 중 발생하는 에러를 처리하기 위한 커스텀 예외"""
    pass

def load_pipeline() -> StableDiffusionPipeline:
    """Stable Diffusion 파이프라인을 로드하고 캐시합니다."""
    if not hasattr(load_pipeline, "pipe"):
        try:
            logger.info("⏳ 모델 로딩 중...")
            load_pipeline.pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16,
                safety_checker=None,  # 안전성 검사 비활성화로 성능 향상
            ).to("mps")
            logger.info("✅ 모델 로딩 완료")
        except Exception as e:
            logger.error(f"모델 로딩 실패: {str(e)}")
            raise ImageGenerationError(f"모델 로딩 실패: {str(e)}")
    return load_pipeline.pipe

def generate_image(
    prompt: str,
    save_path: str,
    height: int = 512,
    width: int = 512,
    num_inference_steps: int = 50,
    guidance_scale: float = 7.5
) -> None:
    """이미지를 생성하고 저장합니다."""
    try:
        pipe = load_pipeline()
        logger.info(f"🎨 '{prompt}' 에 대한 이미지 생성 중...")

        image = pipe(
            prompt,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        ).images[0]
        
        image.save(save_path)
        logger.info(f"✅ 이미지 저장 완료: {save_path}")
        
    except Exception as e:
        logger.error(f"이미지 생성 실패: {str(e)}")
        raise ImageGenerationError(f"이미지 생성 실패: {str(e)}")

def cleanup_resources() -> None:
    """메모리 리소스를 정리합니다."""
    try:
        if hasattr(load_pipeline, "pipe"):
            del load_pipeline.pipe
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        gc.collect()
        logger.info("🧹 리소스 정리 완료")
    except Exception as e:
        logger.error(f"리소스 정리 중 오류 발생: {str(e)}")

def main():
    try:
        prompt = input("📝 이미지 설명을 입력하세요: ").strip()
        if not prompt:
            raise ValueError("프롬프트가 비어있습니다.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        save_path = os.path.join(SAVE_DIR, filename)

        generate_image(prompt, save_path)
        
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {str(e)}")
    finally:
        cleanup_resources()

if __name__ == "__main__":
    main()
