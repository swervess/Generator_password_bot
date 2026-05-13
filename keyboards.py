from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню с кнопками действий."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔐 Сгенерировать пароль", callback_data="generate")
    builder.button(text="📚 Моя библиотека", callback_data="library")
    builder.button(text="ℹ️ Помощь", callback_data="help")
    builder.adjust(1)  # Кнопки в столбик
    return builder.as_markup()

def password_options_keyboard() -> InlineKeyboardMarkup:
    """Меню выбора типа пароля."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔢 Простой (8 символов)", callback_data="gen_8")
    builder.button(text="🔐 Средний (12 символов)", callback_data="gen_12")
    builder.button(text="🛡️ Сложный (16 символов)", callback_data="gen_16")
    builder.button(text="⚙️ Свои настройки", callback_data="gen_custom")
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def save_or_reset_keyboard(password: str) -> InlineKeyboardMarkup:
    """Клавиатура после генерации пароля."""
    builder = InlineKeyboardBuilder()
    builder.button(text="💾 Сохранить пароль", callback_data=f"save_{password}")
    builder.button(text="🔄 Сгенерировать заново", callback_data="generate")
    builder.button(text="🔙 Главное меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def library_actions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура в библиотеке."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑️ Удалить пароль", callback_data="delete_mode")
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def delete_confirmation_keyboard(password_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, удалить", callback_data=f"confirm_delete_{password_id}")
    builder.button(text="❌ Отмена", callback_data="library")
    builder.adjust(2)
    return builder.as_markup()

def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    return builder.as_markup()