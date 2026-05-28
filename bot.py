import telebot
from config import config, Config
from database import Database
from handlers import register_handlers
import sys

def main():
    print("🚀 Запуск бота...\n")
    
    # Проверка конфигурации
    try:
        Config.validate()
        Config.print_config()
    except ValueError as e:
        print(f"\n❌ ОШИБКА КОНФИГУРАЦИИ: {e}")
        print("\n📝 Инструкция:")
        print("1. Скопируйте .env.example в .env")
        print("2. Заполните .env своими данными")
        print("3. Запустите бота снова\n")
        sys.exit(1)
    
    # Инициализация бота и БД
    bot = telebot.TeleBot(config.BOT_TOKEN)
    db = Database()
        
        # Проверка подключения к Telegram
    bot_info = bot.get_me()
    print(f"\n✅ Подключено к Telegram")
    print(f"🤖 Бот: @{bot_info.username}")
    print(f"📛 Имя: {bot_info.first_name}")
    print(f"🆔 ID: {bot_info.id}")
        
    
    # Регистрация всех обработчиков
    register_handlers(bot, db)
    print("✅ Обработчики зарегистрированы")
    
    # Вывод статистики
    stats = db.get_stats()
    print(f"\n📊 Статистика бота:")
    print(f"👥 Пользователей: {stats['total_users']}")
    print(f"🎮 Игр сыграно: {stats['total_games']}")
    print(f"💰 Сумма ставок: {stats['total_bets']}")
    print(f"🏆 Сумма выигрышей: {stats['total_wins']}")
    
    print(f"\n{'='*50}")
    print("🟢 БОТ УСПЕШНО ЗАПУЩЕН!")
    print(f"{'='*50}\n")
    
    # Запуск бота
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка бота...")
        db.close()
        print("✅ Бот остановлен")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        db.close()
        sys.exit(1)

if __name__ == '__main__':
    main()