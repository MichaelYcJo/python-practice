# pip install diffusers transformers accelerate safetensors
# 모델 다운로드 경로 ~/.cache/huggingface/hub


import torch
from diffusers import StableDiffusionPipeline
import gc
import warnings
from datetime import datetime
import os

# 경고 무시 설정 (선택)
warnings.filterwarnings("ignore", message="resource_tracker: There appear to be .*")

# 이미지 저장 경로
SAVE_DIR = "generated_images"
os.makedirs(SAVE_DIR, exist_ok=True)


def generate_image(prompt: str, save_path: str):
    print("⏳ 모델 로딩 중...")

    # 모델 로딩 (Hugging Face에서 캐시됨: ~/.cache/huggingface/hub)
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float32,
        safety_checker=None,
    )

    # pipe.to("cpu")  # GPU가 있다면 pipe.to("cuda")도 가능
    pipe.to("cuda")

    print(f"🎨 '{prompt}' 에 대한 이미지 생성 중...")

    image = pipe(prompt).images[0]
    image.save(save_path)
    print(f"✅ 이미지 저장 완료: {save_path}")

    # 리소스 해제
    del pipe
    del image
    gc.collect()  # 세마포어 누수 방지
    print("🧹 리소스 정리 완료")


def main():
    prompt = input("📝 이미지 설명을 입력하세요: ").strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.png"
    save_path = os.path.join(SAVE_DIR, filename)

    generate_image(prompt, save_path)


if __name__ == "__main__":
    main()
