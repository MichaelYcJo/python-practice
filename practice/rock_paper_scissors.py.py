import random
from typing import Tuple, Dict


class RockPaperScissorsGame:
    def __init__(self):
        self.choices = ["가위", "바위", "보"]
        self.user_score = 0
        self.computer_score = 0
        self.total_games = 0
        self.game_history = []

    def get_user_choice(self) -> str:
        """사용자의 선택을 입력받습니다."""
        while True:
            print("\n📋 선택지:")
            for i, choice in enumerate(self.choices, 1):
                print(f"  {i}. {choice}")
            
            user_input = input("\n당신의 선택 (가위/바위/보 또는 1/2/3): ").strip()
            
            # 숫자 입력 처리
            if user_input.isdigit() and 1 <= int(user_input) <= 3:
                return self.choices[int(user_input) - 1]
            
            # 텍스트 입력 처리
            if user_input in self.choices:
                return user_input
                
            print("❗ 잘못된 입력입니다. 다시 입력해주세요.")

    def get_computer_choice(self) -> str:
        """컴퓨터의 선택을 생성합니다."""
        return random.choice(self.choices)

    def determine_winner(self, user: str, computer: str) -> Tuple[str, str]:
        """승부 결과를 판정합니다."""
        if user == computer:
            result = "무승부"
            message = "🤝 비겼습니다!"
        elif (
            (user == "가위" and computer == "보")
            or (user == "바위" and computer == "가위")
            or (user == "보" and computer == "바위")
        ):
            result = "승리"
            message = "🎉 당신이 이겼습니다!"
            self.user_score += 1
        else:
            result = "패배"
            message = "😢 컴퓨터가 이겼습니다!"
            self.computer_score += 1
        
        self.total_games += 1
        self.game_history.append({
            'user': user,
            'computer': computer,
            'result': result
        })
        
        return result, message

    def display_current_score(self) -> None:
        """현재 점수를 표시합니다."""
        print(f"\n📊 현재 점수")
        print(f"   👤 당신: {self.user_score}")
        print(f"   🤖 컴퓨터: {self.computer_score}")
        
        if self.total_games > 0:
            win_rate = (self.user_score / self.total_games) * 100
            print(f"   🎯 승률: {win_rate:.1f}% ({self.user_score}/{self.total_games})")

    def display_game_stats(self) -> None:
        """게임 통계를 표시합니다."""
        if self.total_games == 0:
            print("\n📈 아직 게임 기록이 없습니다.")
            return
            
        print(f"\n📈 게임 통계")
        print(f"   총 게임 수: {self.total_games}")
        print(f"   승리: {self.user_score}")
        print(f"   패배: {self.computer_score}")
        print(f"   무승부: {self.total_games - self.user_score - self.computer_score}")
        
        if self.total_games > 0:
            win_rate = (self.user_score / self.total_games) * 100
            print(f"   승률: {win_rate:.1f}%")

    def display_recent_history(self, count: int = 5) -> None:
        """최근 게임 이력을 표시합니다."""
        if not self.game_history:
            return
            
        print(f"\n📚 최근 {min(count, len(self.game_history))}게임 이력:")
        recent_games = self.game_history[-count:]
        
        for i, game in enumerate(recent_games, 1):
            result_emoji = {"승리": "🎉", "패배": "😢", "무승부": "🤝"}
            print(f"   {i}. 당신: {game['user']} vs 컴퓨터: {game['computer']} → {result_emoji[game['result']]} {game['result']}")

    def play_round(self) -> None:
        """한 라운드를 진행합니다."""
        print("\n" + "="*50)
        print(f"🎮 라운드 {self.total_games + 1}")
        print("="*50)
        
        user_choice = self.get_user_choice()
        computer_choice = self.get_computer_choice()
        
        print(f"\n🤖 컴퓨터의 선택: {computer_choice}")
        print(f"👤 당신의 선택: {user_choice}")
        
        result, message = self.determine_winner(user_choice, computer_choice)
        print(f"\n🏆 결과: {message}")
        
        self.display_current_score()

    def show_menu(self) -> str:
        """메뉴를 표시하고 사용자 선택을 받습니다."""
        print("\n" + "="*50)
        print("🎮 가위바위보 게임 메뉴")
        print("="*50)
        print("1. 🎯 게임 시작")
        print("2. 📊 점수 확인")
        print("3. 📈 게임 통계")
        print("4. 📚 최근 이력")
        print("5. 🔄 점수 초기화")
        print("6. 👋 게임 종료")
        
        while True:
            choice = input("\n선택하세요 (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            print("❗ 1-6 사이의 숫자를 입력해주세요.")

    def reset_scores(self) -> None:
        """점수를 초기화합니다."""
        confirm = input("정말로 점수를 초기화하시겠습니까? (y/n): ").strip().lower()
        if confirm == 'y':
            self.user_score = 0
            self.computer_score = 0
            self.total_games = 0
            self.game_history = []
            print("✅ 점수가 초기화되었습니다!")

    def main(self) -> None:
        """메인 게임 루프를 실행합니다."""
        print("🎮 가위바위보 게임에 오신 것을 환영합니다! 🎮")
        
        while True:
            choice = self.show_menu()
            
            if choice == '1':
                self.play_round()
            elif choice == '2':
                self.display_current_score()
            elif choice == '3':
                self.display_game_stats()
            elif choice == '4':
                self.display_recent_history()
            elif choice == '5':
                self.reset_scores()
            elif choice == '6':
                print("\n👋 게임을 종료합니다. 즐거우셨나요?")
                self.display_game_stats()
                break


if __name__ == "__main__":
    game = RockPaperScissorsGame()
    game.main()
