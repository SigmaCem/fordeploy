from telebot import TeleBot
from telebot.types import CallbackQuery, Message
from database import Database
from keyboards.keyboards import games_menu, main_menu, bet_selection_inline
from config import config
import time
import threading

# Словарь для хранения временных данных пользователей
user_game_data = {}

def register_game_handlers(bot: TeleBot, db: Database):
    
    @bot.message_handler(func=lambda message: message.text == "🎮 Игры")
    def games(message):
        balance = db.get_balance(message.from_user.id)
        
        text = "🎮 <b>Выберите игру:</b>\n\n"
        text += f"🏀 <b>Баскетбол</b> - попади в кольцо!\n"
        text += f"   Выигрыш на позициях: {', '.join(map(str, config.BASKETBALL_WIN_POSITIONS))}\n\n"
        text += f"🎲 <b>Кубик</b> - выбрось четное число!\n"
        text += f"   Выигрыш на позициях: {', '.join(map(str, config.DICE_WIN_POSITIONS))}\n\n"
        text += f"⭐ <b>Ваш баланс:</b> {balance} звезд\n"
        text += f"🎁 <b>Выигрыш:</b> Ставка × {config.WIN_MULTIPLIER}\n"
        text += f"💵 <b>Доступные ставки:</b> {', '.join(map(str, config.AVAILABLE_BETS))} или своя"
        
        bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=games_menu())
    
    @bot.message_handler(func=lambda message: message.text == "🏀 Баскетбол")
    def basketball(message):
        user_id = message.from_user.id
        balance = db.get_balance(user_id)
        
        text = f"🏀 <b>Баскетбол</b>\n\n"
        text += f"⭐ Ваш баланс: {balance} звезд\n"
        text += f"🎯 Выигрышные позиции: {', '.join(map(str, config.BASKETBALL_WIN_POSITIONS))}\n"
        text += f"🎁 Множитель: ×{config.WIN_MULTIPLIER}\n\n"
        text += f"💰 Выберите ставку:"
        
        bot.send_message(
            message.chat.id, 
            text, 
            parse_mode='HTML',
            reply_markup=bet_selection_inline('basketball')
        )
    
    @bot.message_handler(func=lambda message: message.text == "🎲 Кубик")
    def dice(message):
        user_id = message.from_user.id
        balance = db.get_balance(user_id)
        
        text = f"🎲 <b>Кубик</b>\n\n"
        text += f"⭐ Ваш баланс: {balance} звезд\n"
        text += f"🎯 Выигрышные позиции: {', '.join(map(str, config.DICE_WIN_POSITIONS))}\n"
        text += f"💡 Выбросьте четное число!\n"
        text += f"🎁 Множитель: ×{config.WIN_MULTIPLIER}\n\n"
        text += f"💰 Выберите ставку:"
        
        bot.send_message(
            message.chat.id, 
            text, 
            parse_mode='HTML',
            reply_markup=bet_selection_inline('dice')
        )
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('bet_'))
    def bet_callback(call: CallbackQuery):
        user_id = call.from_user.id
        data_parts = call.data.split('_')
        
        if len(data_parts) < 3:
            return
        
        game_type = data_parts[1]
        bet_value = data_parts[2]
        
        if bet_value == 'custom':
            user_game_data[user_id] = {'game_type': game_type, 'waiting_for_bet': True}
            
            text = f"✏️ <b>Введите свою ставку</b>\n\n"
            text += f"⭐ Ваш баланс: {db.get_balance(user_id)} звезд\n"
            text += f"📊 Диапазон: {config.MIN_CUSTOM_BET} - {config.MAX_CUSTOM_BET} звезд\n\n"
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
            bet_amount = int(bet_value)
            play_game(bot, db, call.message, user_id, game_type, bet_amount, call.id)
            
        except ValueError:
            bot.answer_callback_query(call.id, "❌ Ошибка ставки!", show_alert=True)
    
    @bot.callback_query_handler(func=lambda call: call.data == 'cancel_bet')
    def cancel_bet(call: CallbackQuery):
        user_id = call.from_user.id
        if user_id in user_game_data:
            del user_game_data[user_id]
        
        bot.edit_message_text(
            "❌ Ставка отменена",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    @bot.message_handler(func=lambda message: message.from_user.id in user_game_data and 
                         user_game_data[message.from_user.id].get('waiting_for_bet'))
    def custom_bet_handler(message: Message):
        user_id = message.from_user.id
        
        if user_id not in user_game_data:
            return
        
        try:
            bet_amount = int(message.text)
            
            if bet_amount < config.MIN_CUSTOM_BET:
                bot.send_message(
                    message.chat.id,
                    f"❌ Минимальная ставка: ⭐ {config.MIN_CUSTOM_BET}"
                )
                return
            
            if bet_amount > config.MAX_CUSTOM_BET:
                bot.send_message(
                    message.chat.id,
                    f"❌ Максимальная ставка: ⭐ {config.MAX_CUSTOM_BET}"
                )
                return
            
            game_type = user_game_data[user_id]['game_type']
            del user_game_data[user_id]
            
            play_game(bot, db, message, user_id, game_type, bet_amount)
            
        except ValueError:
            bot.send_message(message.chat.id, "❌ Введите число!")
    
    def play_game(bot: TeleBot, db: Database, message, user_id: int, game_type: str, 
                  bet_amount: int, callback_id: str = None):
        """Основная функция игры с задержкой результата"""
        
        balance = db.get_balance(user_id)
        
        # Проверка баланса
        if balance < bet_amount:
            error_text = f"❌ <b>Недостаточно звезд!</b>\n\n"
            error_text += f"⭐ Ваш баланс: {balance}\n"
            error_text += f"💳 Необходимо: {bet_amount}\n\n"
            error_text += f"💫 Пополните баланс в меню ⭐ Баланс"
            
            if callback_id:
                bot.answer_callback_query(callback_id, "❌ Недостаточно звезд!", show_alert=True)
                bot.edit_message_text(error_text, message.chat.id, message.message_id, parse_mode='HTML')
            else:
                bot.send_message(message.chat.id, error_text, parse_mode='HTML')
            return
        
        # Снимаем ставку
        db.update_balance(user_id, -bet_amount)
        
        # Информируем о начале игры
        game_emoji = "🏀" if game_type == "basketball" else "🎲"
        game_name = "Баскетбол" if game_type == "basketball" else "Кубик"
        start_text = f"{game_emoji} <b>{game_name}</b>\n\n⭐ Ставка {bet_amount} звезд принята!\n🎲 Бросаем..."
        
        if callback_id:
            bot.answer_callback_query(callback_id)
            bot.edit_message_text(start_text, message.chat.id, message.message_id, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, start_text, parse_mode='HTML')
        
        # Отправляем игру
        sent_game = bot.send_dice(message.chat.id, emoji=game_emoji)
        dice_value = sent_game.dice.value
        
        # Определяем выигрышные позиции
        win_positions = (config.BASKETBALL_WIN_POSITIONS if game_type == "basketball" 
                        else config.DICE_WIN_POSITIONS)
        
        # Запускаем отложенную отправку результата
        def send_result():
            # Задержка для просмотра анимации
            time.sleep(config.RESULT_DELAY)
            
            # Проверяем результат
            if dice_value in win_positions:
                # ВЫИГРЫШ
                win_amount = bet_amount * config.WIN_MULTIPLIER
                db.update_balance(user_id, win_amount)
                db.add_game(user_id, game_type, 'win', bet_amount, win_amount, dice_value)
                
                profit = win_amount - bet_amount
                new_balance = db.get_balance(user_id)
                
                result_text = f"🎉 <b>ПОБЕДА!</b> 🎉\n\n"
                result_text += f"{game_emoji} Выпало: <b>{dice_value}</b>\n"
                result_text += f"⭐ Ставка: {bet_amount} звезд\n"
                result_text += f"🏆 Выигрыш: {win_amount} звезд\n"
                result_text += f"📈 Прибыль: <b>+{profit}</b> звезд\n\n"
                result_text += f"💰 Новый баланс: <b>{new_balance}</b> ⭐"
                
            else:
                # ПРОИГРЫШ
                db.add_game(user_id, game_type, 'loss', bet_amount, 0, dice_value)
                new_balance = db.get_balance(user_id)
                
                result_text = f"😔 <b>Не повезло...</b>\n\n"
                result_text += f"{game_emoji} Выпало: <b>{dice_value}</b>\n"
                result_text += f"💸 Ставка: {bet_amount} звезд\n"
                result_text += f"❌ Проигрыш: <b>-{bet_amount}</b> звезд\n\n"
                result_text += f"💰 Новый баланс: <b>{new_balance}</b> ⭐\n\n"
                result_text += f"🍀 Попробуйте еще раз!"
            
            try:
                bot.send_message(message.chat.id, result_text, parse_mode='HTML')
            except Exception as e:
                if config.DEBUG:
                    print(f"Ошибка отправки результата: {e}")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=send_result)
        thread.start()