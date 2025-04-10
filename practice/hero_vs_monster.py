import random
import time

# 무기별 공격력 보너스
WEAPON_STATS = {"철검": 5, "불검": 8, "용의 검": 12}


class Character:
    def __init__(self, name, hp, atk):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.atk = atk

    def is_alive(self):
        return self.hp > 0

    def attack(self, target):
        damage = random.randint(self.atk - 2, self.atk + 2)
        target.hp = max(0, target.hp - damage)
        print(f"💥 {self.name} 이(가) {target.name}에게 {damage}의 피해를 입혔습니다!")


class Hero(Character):
    def __init__(self, name):
        super().__init__(name, hp=100, atk=10)
        self.level = 1
        self.xp = 0
        self.potions = 3
        self.inventory = []
        self.equipped_weapon = None

    def heal(self):
        if self.potions <= 0:
            print("❌ 회복 물약이 없습니다!")
            return
        heal_amount = random.randint(15, 30)
        self.hp = min(self.max_hp, self.hp + heal_amount)
        self.potions -= 1
        print(
            f"🧪 {self.name} 이(가) {heal_amount} 만큼 회복했습니다! (남은 물약: {self.potions})"
        )

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 20:
            self.level += 1
            self.max_hp += 10
            self.hp = self.max_hp
            self.atk += 2
            self.xp = 0
            print(f"✨ 레벨 업! Lv.{self.level} - HP/공격력 상승!")

    def equip_weapon(self):
        weapons = [item for item in self.inventory if item in WEAPON_STATS]
        if not weapons:
            print("🔒 장착 가능한 무기가 없습니다.")
            return

        print("🗡️ 장착 가능한 무기:")
        for i, weapon in enumerate(weapons, 1):
            print(f"{i}. {weapon} (공격력 +{WEAPON_STATS[weapon]})")

        choice = input("👉 장착할 무기 번호를 입력하세요 (0: 취소): ").strip()
        if not choice.isdigit():
            print("❌ 숫자를 입력해주세요.")
            return

        idx = int(choice)
        if idx == 0:
            return
        if idx < 1 or idx > len(weapons):
            print("❗ 올바른 번호를 입력하세요.")
            return

        selected_weapon = weapons[idx - 1]

        # 기존 무기 공격력 제거
        if self.equipped_weapon:
            self.atk -= WEAPON_STATS.get(self.equipped_weapon, 0)

        self.equipped_weapon = selected_weapon
        self.atk += WEAPON_STATS[selected_weapon]

        print(f"✅ {selected_weapon} 을(를) 장착했습니다! 현재 공격력: {self.atk}")

    def use_potion_from_inventory(self):
        if "체력 포션" not in self.inventory:
            print("❌ 인벤토리에 체력 포션이 없습니다!")
            return

        heal_amount = random.randint(15, 30)
        self.hp = min(self.max_hp, self.hp + heal_amount)
        self.inventory.remove("체력 포션")
        print(
            f"🧪 체력 포션을 사용하여 {heal_amount} 회복했습니다! (현재 HP: {self.hp})"
        )


def create_monster():
    names = ["고블린", "늑대", "해골 병사", "슬라임", "좀비"]
    name = random.choice(names)
    hp = random.randint(30, 60)
    atk = random.randint(5, 10)
    return Character(name, hp, atk)


def battle(hero, monster):
    print(f"\n⚔️ {monster.name} 이(가) 나타났다! (HP: {monster.hp})")

    while hero.is_alive() and monster.is_alive():
        print(
            f"\n🧙 {hero.name} [HP: {hero.hp}/{hero.max_hp}] - 포션: {hero.potions} - 공격력: {hero.atk}"
        )
        print(f"👾 {monster.name} [HP: {monster.hp}]")
        print("1. 공격 | 2. 회복 | 3. 도망 | 4. 인벤토리 | 5. 무기 장착 | 6. 포션 사용")
        choice = input("👉 행동 선택: ").strip()

        if choice == "1":
            hero.attack(monster)
        elif choice == "2":
            hero.heal()
        elif choice == "3":
            if random.random() < 0.5:
                print("💨 도망에 성공했습니다!")
                return
            else:
                print("🚫 도망 실패!")
        elif choice == "4":
            if not hero.inventory:
                print("📭 인벤토리에 아무것도 없습니다.")
            else:
                print("🎒 인벤토리 목록:")
                for item in hero.inventory:
                    print(f" - {item}")
            continue
        elif choice == "5":
            hero.equip_weapon()
            continue
        elif choice == "6":
            hero.use_potion_from_inventory()
            continue
        else:
            print("❗ 올바른 번호를 입력하세요.")
            continue

        time.sleep(0.5)

        if monster.is_alive():
            monster.attack(hero)
            time.sleep(0.5)

    if hero.is_alive():
        print(f"✅ {monster.name} 처치 성공!")
        hero.gain_xp(10)

        # 아이템 드랍 (50% 확률)
        if random.random() < 0.5:
            loot = random.choice(["체력 포션", "철검", "불검", "용의 검", "가죽 방패"])
            hero.inventory.append(loot)
            print(f"🎁 {monster.name} 이(가) {loot} 을(를) 떨어뜨렸습니다!")
    else:
        print("💀 당신은 쓰러졌습니다... 게임 오버.")


def main():
    print("🎮 미니 RPG에 오신 걸 환영합니다!")
    name = input("🧙 당신의 이름을 입력하세요: ").strip()
    hero = Hero(name)

    while hero.is_alive():
        monster = create_monster()
        battle(hero, monster)

    print(f"\n⚰️ {hero.name} 의 모험이 끝났습니다. Lv.{hero.level}")


if __name__ == "__main__":
    main()
