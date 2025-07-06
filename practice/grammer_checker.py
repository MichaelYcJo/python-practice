import os
import sys
import time
from typing import List, Optional, Tuple
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from colorama import init, Fore, Back, Style

# Colorama 초기화
init(autoreset=True)

class GrammarChecker:
    def __init__(self, model_name: str = "prithivida/grammar_error_correcter_v1"):
        """문법 검사기 초기화"""
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
    
    def load_model(self):
        """모델 및 토크나이저 로드"""
        try:
            print(f"{Fore.YELLOW}🔄 모델을 로딩 중입니다...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            print(f"{Fore.GREEN}✅ 모델 로딩 완료! ({self.device} 사용)")
        except Exception as e:
            print(f"{Fore.RED}❌ 모델 로딩 실패: {e}")
            sys.exit(1)
    
    def correct_sentence(self, text: str) -> Tuple[str, float]:
        """단일 문장 문법 교정"""
        try:
            start_time = time.time()
            inputs = self.tokenizer.encode(text, return_tensors="pt", max_length=128, truncation=True)
            inputs = inputs.to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs, 
                    max_length=128, 
                    num_beams=5,
                    early_stopping=True
                )
            
            corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            processing_time = time.time() - start_time
            return corrected, processing_time
        except Exception as e:
            print(f"{Fore.RED}❌ 문장 처리 중 오류 발생: {e}")
            return text, 0.0
    
    def correct_multiple_sentences(self, sentences: List[str], show_details: bool = True):
        """여러 문장을 순차적으로 교정"""
        if not sentences:
            print(f"{Fore.YELLOW}⚠️ 처리할 문장이 없습니다.")
            return
        
        print(f"{Fore.CYAN}📝 문장 교정 결과:")
        print("=" * 60)
        
        total_time = 0
        for i, sentence in enumerate(sentences, 1):
            if show_details:
                print(f"{Fore.BLUE}{i}. 원문: {sentence}")
            
            corrected, processing_time = self.correct_sentence(sentence)
            total_time += processing_time
            
            if show_details:
                print(f"{Fore.GREEN}   교정본: {corrected}")
                print(f"{Fore.YELLOW}   처리시간: {processing_time:.3f}초")
                print("-" * 60)
        
        if show_details:
            print(f"{Fore.MAGENTA}총 처리시간: {total_time:.3f}초")
    
    def interactive_mode(self):
        """대화형 모드"""
        print(f"{Fore.CYAN}🎯 대화형 문법 검사 모드")
        print(f"{Fore.YELLOW}종료하려면 'quit' 또는 'exit'를 입력하세요.")
        print("-" * 40)
        
        while True:
            try:
                user_input = input(f"{Fore.GREEN}문장을 입력하세요: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '종료']:
                    print(f"{Fore.YELLOW}👋 프로그램을 종료합니다.")
                    break
                
                if not user_input:
                    continue
                
                corrected, processing_time = self.correct_sentence(user_input)
                print(f"{Fore.BLUE}원문: {user_input}")
                print(f"{Fore.GREEN}교정본: {corrected}")
                print(f"{Fore.YELLOW}처리시간: {processing_time:.3f}초")
                print("-" * 40)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 프로그램을 종료합니다.")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ 오류 발생: {e}")
    
    def process_file(self, file_path: str, output_path: Optional[str] = None):
        """파일에서 문장을 읽어와서 처리"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 문장 분리 (간단한 방법)
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            
            print(f"{Fore.CYAN}📄 파일 처리 중: {file_path}")
            print(f"{Fore.YELLOW}발견된 문장 수: {len(sentences)}")
            
            results = []
            for i, sentence in enumerate(sentences, 1):
                print(f"{Fore.BLUE}처리 중... ({i}/{len(sentences)})")
                corrected, _ = self.correct_sentence(sentence)
                results.append(f"원문: {sentence}\n교정본: {corrected}\n")
            
            # 결과 저장
            if output_path is None:
                output_path = f"corrected_{Path(file_path).stem}.txt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("문법 교정 결과\n")
                f.write("=" * 40 + "\n\n")
                f.writelines(results)
            
            print(f"{Fore.GREEN}✅ 결과가 {output_path}에 저장되었습니다.")
            
        except FileNotFoundError:
            print(f"{Fore.RED}❌ 파일을 찾을 수 없습니다: {file_path}")
        except Exception as e:
            print(f"{Fore.RED}❌ 파일 처리 중 오류 발생: {e}")

def main():
    """메인 함수"""
    print(f"{Fore.CYAN}🔍 고급 문법 검사기")
    print(f"{Fore.YELLOW}개선된 버전 - 에러 처리, 한국어 지원, 대화형 모드 포함")
    print("=" * 50)
    
    checker = GrammarChecker()
    
    while True:
        print(f"\n{Fore.CYAN}📋 메뉴를 선택하세요:")
        print(f"{Fore.GREEN}1. 대화형 모드")
        print(f"{Fore.GREEN}2. 파일에서 문장 처리")
        print(f"{Fore.GREEN}3. 예시 문장 테스트")
        print(f"{Fore.GREEN}4. 종료")
        
        choice = input(f"\n{Fore.YELLOW}선택 (1-4): ").strip()
        
        if choice == "1":
            checker.interactive_mode()
        elif choice == "2":
            file_path = input(f"{Fore.YELLOW}파일 경로를 입력하세요: ").strip()
            if file_path:
                checker.process_file(file_path)
        elif choice == "3":
            test_sentences = [
                "He go to school everyday.",
                "They is playing in the park.",
                "What time she wake up?",
                "The informations are incorrect.",
                "I has a apple.",
                "한국어 문장도 테스트해보겠습니다.",
                "나는 학교에 갑니다."
            ]
            checker.correct_multiple_sentences(test_sentences)
        elif choice == "4":
            print(f"{Fore.YELLOW}👋 프로그램을 종료합니다.")
            break
        else:
            print(f"{Fore.RED}❌ 잘못된 선택입니다. 1-4 중에서 선택해주세요.")

if __name__ == "__main__":
    main()