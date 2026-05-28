from telebot import TeleBot
from database import Database
from keyboards.keyboards import main_menu

def register_profile_handlers(bot: TeleBot, db: Database):
    
    @bot.message_handler(func=lambda message: message.text == "👤 Профиль")
    def profile(message):
        user_id = message.from_user.id
        user = db.get_user(user_id)
        
        if not user:
            bot.send_message(message.chat.id, "❌ Ошибка! Используйте /start")
            return
        
        # Расчет статистики
        win_rate = 0
        if user['total_games'] > 0:
            win_rate = (user['total_wins'] / user['total_games']) * 100
        
        net_profit = user['total_win_amount'] - user['total_bet_amount']
        referrals = db.get_referrals_count(user_id)
        
        profile_text = f"👤 <b>Ваш профиль</b>\n\n"
        profile_text += f"🆔 ID: <code>{user_id}</code>\n"
        profile_text += f"👤 Username: @{user['username']}\n"
        profile_text += f"📅 Регистрация: {user['registration_date'][:10]}\n\n"
        
        profile_text += f"⭐ <b>Баланс:</b> {user['balance']} звезд\n\n"
        
        profile_text += f"📊 <b>Статистика игр:</b>\n"
        profile_text += f"🎮 Всего игр: {user['total_games']}\n"
        profile_text += f"✅ Побед: {user['total_wins']}\n"
        profile_text += f"❌ Поражений: {user['total_losses']}\n"
        profile_text += f"📈 Винрейт: {win_rate:.1f}%\n\n"
        
        profile_text += f"💵 <b>Финансы:</b>\n"
        profile_text += f"📤 Всего поставлено: ⭐ {user['total_bet_amount']}\n"
        profile_text += f"📥 Всего выиграно: ⭐ {user['total_win_amount']}\n"
        
        if net_profit > 0:
            profile_text += f"💹 Чистая прибыль: <b>+{net_profit}</b> ⭐ 📈\n\n"
        elif net_profit < 0:
            profile_text += f"📉 Чистый убыток: <b>{net_profit}</b> ⭐ 📉\n\n"
        else:
            profile_text += f"➖ Чистая прибыль: 0 ⭐\n\n"
        
        profile_text += f"👥 <b>Рефералы:</b> {referrals}"
        
        bot.send_message(message.chat.id, profile_text, parse_mode='HTML')
    
    @bot.message_handler(commands=['referral'])
    @bot.message_handler(func=lambda message: message.text == "👥 Рефералы")
    def referral(message):
        user_id = message.from_user.id
        bot_username = bot.get_me().username
        referral_link = f"https://t.me/{bot_username}?start={user_id}"
        
        referrals = db.get_referrals_count(user_id)
        from config import config
        
        ref_text = f"👥 <b>Реферальная программа</b>\n\n"
        ref_text += f"🎁 Бонус за друга: ⭐ {config.REFERRAL_BONUS}\n"
        ref_text += f"👤 Ваших рефералов: {referrals}\n"
        ref_text += f"⭐ Заработано: {referrals * config.REFERRAL_BONUS} звезд\n\n"
        ref_text += f"🔗 <b>Ваша реферальная ссылка:</b>\n"
        ref_text += f"<code>{referral_link}</code>\n\n"
        ref_text += f"📱 Отправьте эту ссылку друзьям!\n"
        ref_text += f"💡 За каждого друга вы получите ⭐ {config.REFERRAL_BONUS}"
        
        bot.send_message(message.chat.id, ref_text, parse_mode='HTML')