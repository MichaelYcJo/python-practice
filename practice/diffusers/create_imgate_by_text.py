# pip install diffusers transformers accelerate safetensors
# 모델 다운로드 경로 ~/.cache/huggingface/hub


from diffusers import StableDiffusionPipeline
import torch


def generate_image(prompt: str, output_path="./output.png"):
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float32
    )
    pipe = pipe.to("cpu")

    print(f"🎨 '{prompt}'에 대한 이미지를 생성 중입니다...")
    image = pipe(prompt).images[0]
    image.save(output_path)
    image.show()
    print(f"✅ 이미지 생성 완료: {output_path}")


def main():
    print("📝 생성할 이미지의 설명을 입력하세요:")
    prompt = input("> ")
    generate_image(prompt)
    # "A cute cat astronaut floating in space"


if __name__ == "__main__":
    main()
