from telebot import TeleBot
from database import Database
from keyboards.keyboards import admin_withdrawal_keyboard
from config import config

def register_admin_handlers(bot: TeleBot, db: Database):
    
    @bot.message_handler(commands=['admin'])
    def admin_panel(message):
        if message.from_user.id != config.ADMIN_ID:
            return
        
        withdrawals = db.get_pending_withdrawals()
        stats = db.get_stats()
        
        text = f"🔐 <b>Админ-панель</b>\n\n"
        text += f"📊 <b>Статистика:</b>\n"
        text += f"👥 Пользователей: {stats['total_users']}\n"
        text += f"🎮 Игр сыграно: {stats['total_games']}\n"
        text += f"⭐ Сумма ставок: {stats['total_bets']}\n"
        text += f"🏆 Сумма выигрышей: {stats['total_wins']}\n\n"
        
        if withdrawals:
            text += f"📋 <b>Заявки на вывод ({len(withdrawals)}):</b>\n\n"
            for w in withdrawals:
                text += f"🆔 ID: {w['id']}\n"
                text += f"👤 @{w['username']} (ID: {w['user_id']})\n"
                text += f"⭐ Сумма: {w['amount']} звезд\n"
                text += f"📅 Дата: {w['date']}\n"
                text += "—" * 30 + "\n\n"
        else:
            text += "📭 Нет заявок на вывод"
        
        bot.send_message(message.chat.id, text, parse_mode='HTML')
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
    def handle_withdrawal(call):
        if call.from_user.id != config.ADMIN_ID:
            return
        
        action, trans_id, user_id = call.data.split('_')
        trans_id = int(trans_id)
        user_id = int(user_id)
        
        if action == 'approve':
            db.update_transaction_status(trans_id, 'completed')
            
            try:
                bot.send_message(
                    user_id,
                    "✅ <b>Ваша заявка на вывод одобрена!</b>\n\n"
                    "🎁 Подарок отправлен вам в личные сообщения\n"
                    "💰 Проверьте полученные подарки",
                    parse_mode='HTML'
                )
            except:
                pass
            
            bot.edit_message_text(
                f"✅ <b>Заявка #{trans_id} одобрена</b>\n\n"
                f"👤 User ID: {user_id}\n"
                f"📦 Отправьте подарок пользователю",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='HTML'
            )
        
        else:  # reject
            transaction = db.cursor.execute(
                'SELECT amount FROM transactions WHERE id = ?',
                (trans_id,)
            ).fetchone()
            
            if transaction:
                amount = transaction[0]
                db.update_balance(user_id, amount)
                db.update_transaction_status(trans_id, 'rejected')
                
                try:
                    bot.send_message(
                        user_id,
                        f"❌ <b>Ваша заявка на вывод отклонена</b>\n\n"
                        f"⭐ Сумма {amount} звезд возвращена на баланс\n"
                        f"📧 Обратитесь к администратору для уточнения",
                        parse_mode='HTML'
                    )
                except:
                    pass
                
                bot.edit_message_text(
                    f"❌ <b>Заявка #{trans_id} отклонена</b>\n\n"
                    f"👤 User ID: {user_id}\n"
                    f"⭐ {amount} звезд возвращены",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='HTML'
                )
        
        bot.answer_callback_query(call.id)

def notify_admin_withdrawal(bot: TeleBot, db: Database, trans_id: int, user_id: int, username: str, amount: int):
    """Уведомление админа о новой заявке"""
    text = f"🔔 <b>Новая заявка на вывод!</b>\n\n"
    text += f"🆔 ID заявки: {trans_id}\n"
    text += f"👤 Пользователь: @{username}\n"
    text += f"🆔 User ID: <code>{user_id}</code>\n"
    text += f"⭐ Сумма: {amount} звезд"
    
    try:
        bot.send_message(
            config.ADMIN_ID,
            text,
            parse_mode='HTML',
            reply_markup=admin_withdrawal_keyboard(trans_id, user_id)
        )
    except Exception as e:
        if config.DEBUG:
            print(f"❌ Ошибка отправки уведомления админу: {e}")
