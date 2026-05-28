import os
from dotenv import load_dotenv
from typing import List

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Класс конфигурации бота"""
    
    # === Telegram Bot ===
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    ADMIN_ID: int = int(os.getenv('ADMIN_ID', '0'))
    
    # === Database ===
    DB_NAME: str = os.getenv('DB_NAME', 'bot.db')
    
    # === Game Settings ===
    BASKETBALL_WIN_POSITIONS: List[int] = [
        int(x) for x in os.getenv('BASKETBALL_WIN_POSITIONS', '4,5').split(',')
    ]
    DICE_WIN_POSITIONS: List[int] = [
        int(x) for x in os.getenv('DICE_WIN_POSITIONS', '2,4,6').split(',')
    ]
    
    # === Betting Settings ===
    AVAILABLE_BETS: List[int] = [
        int(x) for x in os.getenv('AVAILABLE_BETS', '1,3,5,10,15').split(',')
    ]
    MIN_CUSTOM_BET: int = int(os.getenv('MIN_CUSTOM_BET', '1'))
    MAX_CUSTOM_BET: int = int(os.getenv('MAX_CUSTOM_BET', '100'))
    WIN_MULTIPLIER: float = float(os.getenv('WIN_MULTIPLIER', '2'))
    
    # === Bonuses ===
    REFERRAL_BONUS: int = int(os.getenv('REFERRAL_BONUS', '5'))
    START_BALANCE: int = int(os.getenv('START_BALANCE', '10'))
    
    # === Payment Settings ===
    AVAILABLE_STAR_PACKAGES: List[int] = [
        int(x) for x in os.getenv('AVAILABLE_STAR_PACKAGES', '5,10,25,50,100,250').split(',')
    ]
    STARS_TO_BALANCE: int = int(os.getenv('STARS_TO_BALANCE', '1'))
    MIN_WITHDRAWAL: int = int(os.getenv('MIN_WITHDRAWAL', '10'))
    
    # === Game Settings ===
    RESULT_DELAY: int = int(os.getenv('RESULT_DELAY', '4'))
    
    # === Debug ===
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """Проверка обязательных параметров"""
        if not cls.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN не установлен в .env файле!")
        if cls.ADMIN_ID == 0:
            raise ValueError("❌ ADMIN_ID не установлен в .env файле!")
        return True
    
    @classmethod
    def print_config(cls):
        """Вывод конфигурации (для отладки)"""
        if cls.DEBUG:
            print("=" * 50)
            print("🔧 КОНФИГУРАЦИЯ БОТА")
            print("=" * 50)
            print(f"🤖 Bot Token: {cls.BOT_TOKEN[:10]}...")
            print(f"👤 Admin ID: {cls.ADMIN_ID}")
            print(f"💾 Database: {cls.DB_NAME}")
            print(f"🏀 Basketball Win: {cls.BASKETBALL_WIN_POSITIONS}")
            print(f"🎲 Dice Win: {cls.DICE_WIN_POSITIONS}")
            print(f"💰 Available Bets: {cls.AVAILABLE_BETS}")
            print(f"💵 Custom Bet Range: {cls.MIN_CUSTOM_BET}-{cls.MAX_CUSTOM_BET}")
            print(f"🎁 Win Multiplier: x{cls.WIN_MULTIPLIER}")
            print(f"👥 Referral Bonus: {cls.REFERRAL_BONUS}")
            print(f"💵 Start Balance: {cls.START_BALANCE}")
            print(f"⭐ Star Packages: {cls.AVAILABLE_STAR_PACKAGES}")
            print(f"⭐ Stars to Balance: 1⭐ = {cls.STARS_TO_BALANCE}")
            print(f"💸 Min Withdrawal: {cls.MIN_WITHDRAWAL}")
            print(f"⏱️ Result Delay: {cls.RESULT_DELAY}s")
            print(f"🐛 Debug Mode: {cls.DEBUG}")
            print("=" * 50)

# Создаем экземпляр конфигурации
config = Config()
