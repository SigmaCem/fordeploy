import os
import shutil

def setup():
    """Первоначальная настройка проекта"""
    print("🔧 Настройка проекта...\n")
    
    # Проверка .env файла
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Создан файл .env из .env.example")
            print("⚠️  ВАЖНО: Отредактируйте .env и укажите свои данные!\n")
        else:
            print("❌ Файл .env.example не найден!")
            return False
    else:
        print("✅ Файл .env уже существует\n")
    
    # Проверка requirements
    print("📦 Установка зависимостей...")
    result = os.system("pip install -r requirements.txt")
    
    if result == 0:
        print("\n✅ Зависимости установлены!")
    else:
        print("\n❌ Ошибка установки зависимостей")
        return False
    
    print("\n" + "="*50)
    print("✅ НАСТРОЙКА ЗАВЕРШЕНА!")
    print("="*50)
    print("\n📝 Следующие шаги:")
    print("1. Отредактируйте файл .env")
    print("2. Укажите BOT_TOKEN (получить у @BotFather)")
    print("3. Укажите ADMIN_ID (узнать у @userinfobot)")
    print("4. Запустите бота: python main.py\n")
    
    return True

if __name__ == '__main__':
    setup()