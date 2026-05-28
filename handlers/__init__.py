from .start import register_start_handlers
from .games import register_game_handlers
from .profile import register_profile_handlers
from .payment import register_payment
from .admin import register_admin_handlers

def register_handlers(bot, db):
    """Регистрация всех обработчиков"""
    register_start_handlers(bot, db)
    register_game_handlers(bot, db)
    register_profile_handlers(bot, db)
    register_payment(bot, db)
    register_admin_handlers(bot, db)
