# pip install diffusers transformers accelerate safetensors
# 모델 다운로드 경로 ~/.cache/huggingface/hub


import torch
from diffusers import StableDiffusionPipeline
import gc
import warnings
from datetime import datetime
import os

warnings.filterwarnings("ignore", message="resource_tracker: There appear to be .*")

SAVE_DIR = "generated_images"
os.makedirs(SAVE_DIR, exist_ok=True)


def load_pipeline():
    if not hasattr(load_pipeline, "pipe"):
        print("⏳ 모델 로딩 중...")
        load_pipeline.pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            # safety_checker=None,
        ).to(
            "mps"
        )  # M1 Mac에서 GPU 사용을 위해 "mps" 설정
    return load_pipeline.pipe


def generate_image(prompt: str, save_path: str):
    pipe = load_pipeline()
    print(f"🎨 '{prompt}' 에 대한 이미지 생성 중...")

    image = pipe(prompt, height=512, width=512).images[0]
    image.save(save_path)
    print(f"✅ 이미지 저장 완료: {save_path}")


def main():
    prompt = input("📝 이미지 설명을 입력하세요: ").strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.png"
    save_path = os.path.join(SAVE_DIR, filename)

    generate_image(prompt, save_path)

    gc.collect()  # M1의 경우 자주 리소스를 비워주는 것이 좋음
    print("🧹 리소스 정리 완료")


if __name__ == "__main__":
    main()
