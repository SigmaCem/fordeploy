from telebot import TeleBot
from database import Database
from keyboards.keyboards import main_menu
from config import config

def register_start_handlers(bot: TeleBot, db: Database):
    
    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.from_user.id
        username = message.from_user.username or "Без username"
        
        # Проверяем реферальную ссылку
        referrer_id = None
        if len(message.text.split()) > 1:
            try:
                referrer_id = int(message.text.split()[1])
                if referrer_id == user_id:
                    referrer_id = None
            except:
                pass
        
        # Регистрируем пользователя
        if not db.user_exists(user_id):
            db.add_user(user_id, username, referrer_id)
            
            # Начисляем бонус рефереру
            if referrer_id and db.user_exists(referrer_id):
                db.update_balance(referrer_id, config.REFERRAL_BONUS)
                try:
                    bot.send_message(
                        referrer_id,
                        f"🎉 По вашей реферальной ссылке зарегистрировался новый пользователь!\n"
                        f"⭐ Вы получили {config.REFERRAL_BONUS} звезд!"
                    )
                except:
                    pass
            
            welcome_text = f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
        else:
            welcome_text = f"👋 С возвращением, {message.from_user.first_name}!\n\n"
        
        welcome_text += "🎮 <b>Доступные игры:</b>\n"
        welcome_text += "🏀 Баскетбол - попади в кольцо!\n"
        welcome_text += "   Выигрыш: позиции 4, 5\n\n"
        welcome_text += "🎲 Кубик - выбрось четное!\n"
        welcome_text += "   Выигрыш: позиции 2, 4, 6\n\n"
        welcome_text += f"⭐ <b>Ставки:</b> {', '.join(map(str, config.AVAILABLE_BETS))} или своя\n"
        welcome_text += f"🎁 <b>Выигрыш:</b> Ставка × {config.WIN_MULTIPLIER}\n\n"
        welcome_text += "💫 Пополняйте баланс и выводите выигрыш!\n"
        welcome_text += "👥 Приглашайте друзей и получайте бонусы!"
        
        bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=main_menu())
    
    @bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
    def back_to_main(message):
        bot.send_message(message.chat.id, "📱 Главное меню:", reply_markup=main_menu())
    
    @bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
    def help_command(message):
        help_text = """
ℹ️ <b>Помощь по боту</b>

🎮 <b>Игры:</b>

🏀 <b>Баскетбол</b>
   • Попади мячом в кольцо!
   • Выигрыш: позиции {basketball_win}

🎲 <b>Кубик</b>
   • Выбрось четное число!
   • Выигрыш: позиции {dice_win}

⭐ <b>Ставки:</b>
   • Быстрые: {bets}
   • Своя ставка: {min_bet}-{max_bet} звезд
   • Выигрыш: Ставка × {multiplier}

💫 <b>Баланс:</b>
   • Пополнение: через Telegram Stars
   • Курс: 1 Telegram Star = 1 ⭐ в боте
   • Пакеты: {star_packages}
   • Вывод: через подарки (мин. {min_withdrawal} ⭐)

👥 <b>Рефералы:</b>
   • Бонус за друга: {referral_bonus} ⭐
   • Ссылка: /referral

❓ По всем вопросам: @admin
        """.format(
            basketball_win=', '.join(map(str, config.BASKETBALL_WIN_POSITIONS)),
            dice_win=', '.join(map(str, config.DICE_WIN_POSITIONS)),
            bets=', '.join(map(str, config.AVAILABLE_BETS)),
            min_bet=config.MIN_CUSTOM_BET,
            max_bet=config.MAX_CUSTOM_BET,
            multiplier=config.WIN_MULTIPLIER,
            star_packages=', '.join(map(str, config.AVAILABLE_STAR_PACKAGES)),
            min_withdrawal=config.MIN_WITHDRAWAL,
            referral_bonus=config.REFERRAL_BONUS
        )
        bot.send_message(message.chat.id, help_text, parse_mode='HTML')