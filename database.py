import sqlite3
from datetime import datetime
from typing import Optional, Dict, List
from config import config

class Database:
    def __init__(self, db_file: str = None):
        """Инициализация базы данных"""
        if db_file is None:
            db_file = config.DB_NAME
            
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_tables()
        
        if config.DEBUG:
            print(f"💾 База данных инициализирована: {db_file}")
    
    def create_tables(self):
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 100,
                referrer_id INTEGER,
                registration_date TEXT,
                total_games INTEGER DEFAULT 0,
                total_wins INTEGER DEFAULT 0,
                total_losses INTEGER DEFAULT 0,
                total_bet_amount INTEGER DEFAULT 0,
                total_win_amount INTEGER DEFAULT 0
            )
                            ''')
        
        # Таблица игр
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                game_type TEXT,
                result TEXT,
                bet INTEGER,
                win_amount INTEGER,
                dice_value INTEGER,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица транзакций
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount INTEGER,
                stars INTEGER DEFAULT 0,
                status TEXT,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.connection.commit()
    
    def add_user(self, user_id: int, username: str, referrer_id: Optional[int] = None):
        try:
            self.cursor.execute('''
                INSERT INTO users (user_id, username, referrer_id, registration_date, balance)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, referrer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), config.START_BALANCE))
            self.connection.commit()
            
            if config.DEBUG:
                print(f"✅ Новый пользователь: {user_id} (@{username})")
            
            return True
        except sqlite3.IntegrityError:
            return False
    
    def user_exists(self, user_id: int) -> bool:
        result = self.cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        return result.fetchone() is not None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        result = self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = result.fetchone()
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'balance': row[2],
                'referrer_id': row[3],
                'registration_date': row[4],
                'total_games': row[5],
                'total_wins': row[6],
                'total_losses': row[7],
                'total_bet_amount': row[8],
                'total_win_amount': row[9]
            }
        return None
    
    def update_balance(self, user_id: int, amount: int):
        self.cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        self.connection.commit()
        
        if config.DEBUG:
            new_balance = self.get_balance(user_id)
            print(f"💰 Баланс изменен: user_id={user_id}, amount={amount:+d}, new_balance={new_balance}")
    
    def get_balance(self, user_id: int) -> int:
        result = self.cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        row = result.fetchone()
        return row[0] if row else 0
    
    def add_game(self, user_id: int, game_type: str, result: str, bet: int, win_amount: int, dice_value: int):
        self.cursor.execute('''
            INSERT INTO games (user_id, game_type, result, bet, win_amount, dice_value, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, game_type, result, bet, win_amount, dice_value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Обновляем статистику
        if result == 'win':
            self.cursor.execute('''
                UPDATE users SET 
                    total_games = total_games + 1, 
                    total_wins = total_wins + 1,
                    total_bet_amount = total_bet_amount + ?,
                    total_win_amount = total_win_amount + ?
                WHERE user_id = ?
            ''', (bet, win_amount, user_id))
        else:
            self.cursor.execute('''
                UPDATE users SET 
                    total_games = total_games + 1,
                    total_losses = total_losses + 1,
                    total_bet_amount = total_bet_amount + ?
                WHERE user_id = ?
            ''', (bet, user_id))
        
        self.connection.commit()
        
        if config.DEBUG:
            print(f"🎮 Игра: user_id={user_id}, type={game_type}, result={result}, bet={bet}, win={win_amount}, dice={dice_value}")
    
    def add_transaction(self, user_id: int, trans_type: str, amount: int, stars: int = 0, status: str = 'pending'):
        self.cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, stars, status, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, trans_type, amount, stars, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.connection.commit()
        
        trans_id = self.cursor.lastrowid
        
        if config.DEBUG:
            print(f"💳 Транзакция: id={trans_id}, user_id={user_id}, type={trans_type}, amount={amount}, stars={stars}, status={status}")
        
        return trans_id
    
    def get_pending_withdrawals(self) -> List[Dict]:
        result = self.cursor.execute('''
            SELECT t.id, t.user_id, u.username, t.amount, t.date 
            FROM transactions t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.type = 'withdrawal' AND t.status = 'pending'
        ''')
        
        withdrawals = []
        for row in result.fetchall():
            withdrawals.append({
                'id': row[0],
                'user_id': row[1],
                'username': row[2],
                'amount': row[3],
                'date': row[4]
            })
        return withdrawals
    
    def update_transaction_status(self, trans_id: int, status: str):
        self.cursor.execute('UPDATE transactions SET status = ? WHERE id = ?', (status, trans_id))
        self.connection.commit()
        
        if config.DEBUG:
            print(f"✅ Транзакция {trans_id} обновлена: status={status}")
    
    def get_referrals_count(self, user_id: int) -> int:
        result = self.cursor.execute('SELECT COUNT(*) FROM users WHERE referrer_id = ?', (user_id,))
        return result.fetchone()[0]
    
    def get_stats(self) -> Dict:
        """Получить общую статистику бота"""
        stats = {}
        
        # Общее количество пользователей
        result = self.cursor.execute('SELECT COUNT(*) FROM users')
        stats['total_users'] = result.fetchone()[0]
        
        # Общее количество игр
        result = self.cursor.execute('SELECT COUNT(*) FROM games')
        stats['total_games'] = result.fetchone()[0]
        
        # Общая сумма ставок
        result = self.cursor.execute('SELECT SUM(bet) FROM games')
        stats['total_bets'] = result.fetchone()[0] or 0
        
        # Общая сумма выигрышей
        result = self.cursor.execute('SELECT SUM(win_amount) FROM games WHERE result = "win"')
        stats['total_wins'] = result.fetchone()[0] or 0
        
        return stats
    
    def close(self):
        self.connection.close()
        if config.DEBUG:
            print("💾 База данных закрыта")