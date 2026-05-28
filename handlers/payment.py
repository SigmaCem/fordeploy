from telebot import TeleBot
from telebot.types import LabeledPrice, Message
from database import Database
from keyboards.keyboards import balance_menu, stars_selection_inline, payment_inline, main_menu
from config import config

# Словарь для хранения данных о пополнении
user_payment_data = {}

def register_payment(bot: TeleBot, db: Database):
    
    @bot.message_handler(func=lambda message: message.text == "⭐ Баланс")
    def balance(message):
        user_id = message.from_user.id
        current_balance = db.get_balance(user_id)
        
        text = f"⭐ <b>Ваш баланс:</b> {current_balance} звезд\n\n"
        text += f"💫 <b>Пополнение:</b>\n"
        text += f"   • Пакеты: {', '.join(map(str, config.AVAILABLE_STAR_PACKAGES))}\n"
        text += f"   • Курс: 1 Telegram Star = 1 ⭐ в боте\n\n"
        text += f"💸 <b>Вывод:</b>\n"
        text += f"   • Минимум: ⭐ {config.MIN_WITHDRAWAL}\n"
        
        bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=balance_menu())
    
    @bot.message_handler(func=lambda message: message.text == "💫 Пополнить")
    def deposit(message):
        text = "💫 <b>Пополнение баланса</b>\n\n"
        text += f"Выберите пакет Telegram Stars:\n\n"
        
        for stars in config.AVAILABLE_STAR_PACKAGES:
            text += f"• {stars} Telegram Stars = ⭐ {stars} в боте\n"
        
        text += f"\n💡 Курс: 1 к 1"
        
        bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=stars_selection_inline()
        )
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('stars_'))
    def stars_callback(call):
        user_id = call.from_user.id
        data_parts = call.data.split('_')
        
        if len(data_parts) < 2:
            return
        
        stars_value = data_parts[1]
        
        if stars_value == 'custom':
            user_payment_data[user_id] = {'waiting_for_stars': True}
            
            text = f"✏️ <b>Введите количество Telegram Stars</b>\n\n"
            text += f"📊 Диапазон: 1 - 2500\n"
            text += f"💡 1 Telegram Star = 1 ⭐ в боте\n\n"
            text += f"Введите число:"
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id)
            return
        
        try:
            stars = int(stars_value)
            create_invoice(bot, call.message, user_id, stars, call.id)
            
        except ValueError:
            bot.answer_callback_query(call.id, "❌ Ошибка!", show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == 'cancel_pay')
    def cancel_payment(call):
        user_id = call.from_user.id
        if user_id in user_payment_data:
            del user_payment_data[user_id]
        
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "❌ Оплата отменена")
        bot.answer_callback_query(call.id)
    
    @bot.message_handler(func=lambda message: message.from_user.id in user_payment_data and 
                         user_payment_data[message.from_user.id].get('waiting_for_stars'))
    def custom_stars_handler(message: Message):
        user_id = message.from_user.id
        
        if user_id not in user_payment_data:
            return
        
        try:
            stars = int(message.text)
            
            if stars < 1:
                bot.send_message(message.chat.id, "❌ Минимум: 1 Telegram Star")
                return
            
            if stars > 2500:
                bot.send_message(message.chat.id, "❌ Максимум: 2500 Telegram Stars")
                return
            
            del user_payment_data[user_id]
            create_invoice(bot, message, user_id, stars)
            
        except ValueError:
            bot.send_message(message.chat.id, "❌ Введите число!")
    
    def create_invoice(bot: TeleBot, message, user_id: int, stars: int, callback_id: str = None):
        """Создание счета для оплаты"""
        
        # Создаем счет
        prices = [LabeledPrice(label=f"{stars} Telegram Stars", amount=stars)]
        
        description = f"Пополнение баланса на ⭐ {stars}"
        
        if callback_id:
            bot.answer_callback_query(callback_id)
            bot.delete_message(message.chat.id, message.message_id)
        
        bot.send_invoice(
            message.chat.id,
            title=f"Пополнение на ⭐ {stars}",
            description=description,
            invoice_payload=f"deposit_{stars}_{user_id}",
            provider_token="",
            currency="XTR",
            prices=prices,
            reply_markup=payment_inline(stars)
        )
    
    @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout(pre_checkout_query):
        bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=True
        )
    
    @bot.message_handler(content_types=['successful_payment'])
    def successful_payment(message):
        payload_parts = message.successful_payment.invoice_payload.split('_')
        stars = int(payload_parts[1])
        user_id = int(payload_parts[2])
        
        amount = stars * config.STARS_TO_BALANCE
        
        # Начисляем звезды
        db.update_balance(user_id, amount)
        db.add_transaction(user_id, 'deposit', amount, stars, 'completed')
        
        new_balance = db.get_balance(user_id)
        
        text = f"✅ <b>Пополнение успешно!</b>\n\n"
        text += f"💫 Оплачено: {stars} Telegram Stars\n"
        text += f"⭐ Начислено: {amount} звезд\n"
        text += f"💰 Новый баланс: <b>{new_balance}</b> ⭐\n\n"
        text += f"🎮 Приятной игры!"
        
        bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=main_menu())
    
    @bot.message_handler(func=lambda message: message.text == "💸 Вывести")
    def withdraw(message):
        user_id = message.from_user.id
        balance = db.get_balance(user_id)
        
        if balance < config.MIN_WITHDRAWAL:
            bot.send_message(
                message.chat.id,
                f"❌ <b>Недостаточно средств для вывода</b>\n\n"
                f"⭐ Ваш баланс: {balance}\n"
                f"💳 Минимум: ⭐ {config.MIN_WITHDRAWAL}\n\n"
                f"🎮 Продолжайте играть!",
                parse_mode='HTML'
            )
            return
        
        text = f"💸 <b>Вывод средств</b>\n\n"
        text += f"⭐ Ваш баланс: {balance} звезд\n"
        text += f"💳 Минимум: ⭐ {config.MIN_WITHDRAWAL}\n"
        text += f"📦 Вывод через подарки бота\n\n"
        text += f"Укажите сумму для вывода:"
        
        msg = bot.send_message(message.chat.id, text, parse_mode='HTML')
        bot.register_next_step_handler(msg, process_withdrawal)
    
    def process_withdrawal(message):
        try:
            amount = int(message.text)
            user_id = message.from_user.id
            balance = db.get_balance(user_id)
            
            if amount < config.MIN_WITHDRAWAL:
                bot.send_message(
                    message.chat.id,
                    f"❌ Минимальная сумма: ⭐ {config.MIN_WITHDRAWAL}"
                )
                return
            
            if amount > balance:
                bot.send_message(
                    message.chat.id,
                    f"❌ Недостаточно средств!\n⭐ Баланс: {balance}"
                )
                return
            
            # Снимаем средства
            db.update_balance(user_id, -amount)
            trans_id = db.add_transaction(user_id, 'withdrawal', amount, 0, 'pending')
            
            # Уведомляем пользователя
            bot.send_message(
                message.chat.id,
                f"✅ <b>Заявка на вывод создана!</b>\n\n"
                f"⭐ Сумма: {amount} звезд\n"
                f"🆔 ID заявки: {trans_id}\n"
                f"⏳ Ожидайте одобрения администратора\n\n"
                f"📦 Подарок будет отправлен после проверки",
                parse_mode='HTML',
                reply_markup=main_menu()
            )
            
            # Уведомляем админа
            from handlers.admin import notify_admin_withdrawal
            notify_admin_withdrawal(bot, db, trans_id, user_id, message.from_user.username, amount)
            
        except ValueError:
            bot.send_message(message.chat.id, "❌ Введите число!")
