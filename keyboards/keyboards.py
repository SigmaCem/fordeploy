from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import config

def main_menu():
    """Главное меню"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🎮 Игры"))
    keyboard.add(KeyboardButton("👤 Профиль"), KeyboardButton("⭐ Баланс"))
    keyboard.add(KeyboardButton("👥 Рефералы"), KeyboardButton("ℹ️ Помощь"))
    return keyboard

def games_menu():
    """Меню игр"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🏀 Баскетбол"), KeyboardButton("🎲 Кубик"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def bet_selection_inline(game_type: str):
    """Инлайн клавиатура для выбора ставки"""
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    # Кнопки с предустановленными ставками
    buttons = []
    for bet in config.AVAILABLE_BETS:
        buttons.append(
            InlineKeyboardButton(
                f"⭐ {bet}", 
                callback_data=f"bet_{game_type}_{bet}"
            )
        )
    
    # Добавляем кнопки по 3 в ряд
    for i in range(0, len(buttons), 3):
        keyboard.row(*buttons[i:i+3])
    
    # Кнопка "Своя ставка"
    keyboard.row(
        InlineKeyboardButton(
            "✏️ Своя ставка", 
            callback_data=f"bet_{game_type}_custom"
        )
    )
    
    # Кнопка отмены
    keyboard.row(
        InlineKeyboardButton(
            "❌ Отмена", 
            callback_data="cancel_bet"
        )
    )
    
    return keyboard

def balance_menu():
    """Меню баланса"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("💫 Пополнить"))
    keyboard.add(KeyboardButton("💸 Вывести"))
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard

def stars_selection_inline():
    """Инлайн клавиатура для выбора количества звезд"""
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    # Кнопки с пакетами звезд
    buttons = []
    for stars in config.AVAILABLE_STAR_PACKAGES:
        buttons.append(
            InlineKeyboardButton(
                f"⭐ {stars}",
                callback_data=f"stars_{stars}"
            )
        )
    
    # Добавляем кнопки по 3 в ряд
    for i in range(0, len(buttons), 3):
        keyboard.row(*buttons[i:i+3])
    
    # Кнопка "Свое количество"
    keyboard.row(
        InlineKeyboardButton(
            "✏️ Свое количество",
            callback_data="stars_custom"
        )
    )
    
    # Кнопка отмены
    keyboard.row(
        InlineKeyboardButton(
            "❌ Отмена",
            callback_data="cancel_pay"
        )
    )
    
    return keyboard

def payment_inline(amount: int):
    """Инлайн кнопки для оплаты"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(f"Оплатить {amount} ⭐", pay=True))
    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_pay"))
    return keyboard

def admin_withdrawal_keyboard(trans_id: int, user_id: int):
    """Клавиатура для одобрения вывода"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{trans_id}_{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{trans_id}_{user_id}")
    )
    return keyboard

def back_button():
    """Кнопка назад"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("⬅️ Назад"))
    return keyboard