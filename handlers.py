from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from database import register_user, save_password, get_user_passwords, delete_password
from password_generator import generate_password
from keyboards import (
    main_menu_keyboard, password_options_keyboard, save_or_reset_keyboard,
    library_actions_keyboard, delete_confirmation_keyboard, back_to_main_keyboard
)
import io

router = Router()


delete_mode = {}


@router.message(Command("start"))
async def start_command(message: Message):
    """Обработчик команды /start."""
    user = message.from_user
    register_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        last_name=user.last_name or ""
    )
    welcome_text = (
        f"🔐 *Добро пожаловать, {user.first_name}!*\n\n"
        "Я — бот для генерации надёжных паролей и их сохранения в личную библиотеку.\n\n"
        "✨ *Мои возможности:*\n"
        "• Генерация паролей разной длины и сложности\n"
        "• Сохранение паролей с названием сервиса\n"
        "• Просмотр и удаление сохранённых паролей\n\n"
        "👇 *Выберите действие:*"
    )
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help."""
    help_text = (
        "📖 *Справка по использованию*\n\n"
        "🔹 *Генерация пароля* — выберите длину пароля или настройте параметры вручную.\n"
        "🔹 *Сохранение* — после генерации нажмите «Сохранить пароль» и укажите название сервиса.\n"
        "🔹 *Моя библиотека* — просмотр всех ваших сохранённых паролей.\n"
        "🔹 *Удаление* — в библиотеке выберите режим удаления и подтвердите действие.\n\n"
        "⚠️ *Важно:* пароли хранятся в открытом виде. Не передавайте бота третьим лицам!\n\n"
        "Команды:\n"
        "/start — главное меню\n"
        "/help — эта справка"
    )
    await message.answer(help_text, parse_mode="Markdown", reply_markup=back_to_main_keyboard())


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Возврат в главное меню."""
    await callback.message.edit_text(
        "🔐 *Главное меню*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "generate")
async def generate_menu(callback: CallbackQuery):
    """Меню выбора типа пароля."""
    await callback.message.edit_text(
        "🔐 *Выберите тип пароля:*\n\n"
        "• Простой — 8 символов (буквы + цифры)\n"
        "• Средний — 12 символов (буквы + цифры)\n"
        "• Сложный — 16 символов (буквы + цифры + спецсимволы)\n"
        "• Свои настройки — выберите длину и состав вручную",
        parse_mode="Markdown",
        reply_markup=password_options_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("gen_"))
async def generate_password_handler(callback: CallbackQuery):
    """Генерация пароля на основе выбранного типа."""
    option = callback.data.split("_")[1]

    length_map = {
        "8": 8,
        "12": 12,
        "16": 16
    }

    if option in length_map:
        length = length_map[option]
        use_digits = True
        use_punctuation = (length == 16)
    else:

        length = 12
        use_digits = True
        use_punctuation = False

    password = generate_password(length, use_digits, use_punctuation)

    await callback.message.edit_text(
        f"🔐 *Ваш пароль:*\n`{password}`\n\n"
        f"📏 *Длина:* {length} символов\n"
        f"🔢 *Цифры:* {'✅' if use_digits else '❌'}\n"
        f"🔣 *Спецсимволы:* {'✅' if use_punctuation else '❌'}\n\n"
        "Вы можете сохранить этот пароль или сгенерировать новый.",
        parse_mode="Markdown",
        reply_markup=save_or_reset_keyboard(password)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("save_"))
async def save_password_handler(callback: CallbackQuery):
    """Обработка сохранения пароля (запрос названия сервиса)."""
    password = callback.data.split("_", 1)[1]

    await callback.message.answer(
        f"💾 *Сохранение пароля*\n\n"
        f"Пароль: `{password}`\n\n"
        f"Введите название сервиса или аккаунта для этого пароля:",
        parse_mode="Markdown"
    )



    # Сохраняем данные во временный словарь (расширение функционала)
    if not hasattr(callback.message.bot, 'pending_saves'):
        callback.message.bot.pending_saves = {}
    callback.message.bot.pending_saves[callback.from_user.id] = password

    await callback.answer()



@router.message()
async def handle_save_text(message: Message):
    """Обработка ввода названия сервиса для сохранения пароля."""
    bot = message.bot
    if hasattr(bot, 'pending_saves') and message.from_user.id in bot.pending_saves:
        password = bot.pending_saves.pop(message.from_user.id)
        service_name = message.text.strip()

        if not service_name:
            await message.answer("❌ Название сервиса не может быть пустым. Попробуйте снова.")
            return

        success = save_password(message.from_user.id, service_name, password)
        if success:
            await message.answer(
                f"✅ *Пароль успешно сохранён!*\n\n"
                f"📌 *Сервис:* {service_name}\n"
                f"🔐 *Пароль:* `{password}`\n\n"
                f"Вы можете просмотреть все сохранённые пароли в разделе «Моя библиотека».",
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard()
            )
        else:
            await message.answer(
                "❌ *Ошибка сохранения.* Попробуйте позже.",
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard()
            )


@router.callback_query(F.data == "library")
async def show_library(callback: CallbackQuery):
    """Отображение библиотеки сохранённых паролей."""
    passwords = get_user_passwords(callback.from_user.id)

    if not passwords:
        await callback.message.edit_text(
            "📚 *Моя библиотека*\n\n"
            "У вас пока нет сохранённых паролей.\n\n"
            "Сгенерируйте пароль и сохраните его, чтобы он появился здесь.",
            parse_mode="Markdown",
            reply_markup=back_to_main_keyboard()
        )
        await callback.answer()
        return


    text = "📚 *Моя библиотека паролей*\n\n"
    for pid, service, pwd, date in passwords:

        masked_pwd = pwd[:4] + "*" * (len(pwd) - 4) if len(pwd) > 4 else "*" * len(pwd)
        text += f"🔹 *{service}*\n   Пароль: `{masked_pwd}`\n   ID: `{pid}`\n   📅 {date[:10]}\n\n"

    text += "Для удаления нажмите «Удалить пароль» и введите ID записи."

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=library_actions_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "delete_mode")
async def delete_mode_start(callback: CallbackQuery):
    """Включение режима удаления."""
    await callback.message.answer(
        "🗑️ *Режим удаления*\n\n"
        "Введите ID пароля, который хотите удалить.\n\n"
        "ID можно найти в библиотеке напротив каждого пароля.",
        parse_mode="Markdown"
    )

    if not hasattr(callback.message.bot, 'pending_delete'):
        callback.message.bot.pending_delete = {}
    callback.message.bot.pending_delete[callback.from_user.id] = True
    await callback.answer()


@router.message()
async def handle_delete_id(message: Message):
    """Обработка ввода ID для удаления."""
    bot = message.bot
    if hasattr(bot, 'pending_delete') and message.from_user.id in bot.pending_delete:
        del bot.pending_delete[message.from_user.id]
        try:
            password_id = int(message.text.strip())
            success = delete_password(password_id, message.from_user.id)
            if success:
                await message.answer(
                    "✅ *Пароль успешно удалён!*",
                    parse_mode="Markdown",
                    reply_markup=main_menu_keyboard()
                )
            else:
                await message.answer(
                    "❌ *Пароль не найден* или не принадлежит вам.\n"
                    "Проверьте ID и попробуйте снова.",
                    parse_mode="Markdown",
                    reply_markup=library_actions_keyboard()
                )
        except ValueError:
            await message.answer(
                "❌ *Неверный формат.* Введите числовой ID пароля.",
                parse_mode="Markdown",
                reply_markup=library_actions_keyboard()
            )


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    """Справка из callback."""
    await help_command(callback.message)
    await callback.answer()