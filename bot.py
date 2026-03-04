import asyncio
import logging
import html
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

# ═══════════════════════════════════════════════════════════════
# ⚙️ НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════

BOT_TOKEN = "8623199291:AAFDPTyXvdqbI3VNy3VPTPftHzu_u16hA_4"
ADMIN_CHAT_ID = -1003800032106
APPLICATIONS_TOPIC_ID = 5
WELCOME_LINK = "https://t.me/+nvVGJ_E4_uI2YWMx"

# ═══════════════════════════════════════════════════════════════
# 📝 ЛОГИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# 🤖 ИНИЦИАЛИЗАЦИЯ
# ═══════════════════════════════════════════════════════════════

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# ═══════════════════════════════════════════════════════════════
# 📋 СОСТОЯНИЯ FSM
# ═══════════════════════════════════════════════════════════════

class ApplicationForm(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_phone = State()
    confirm_application = State()

# ═══════════════════════════════════════════════════════════════
# 🎨 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def escape_html(text: str) -> str:
    return html.escape(str(text))

def get_progress(step: int, total: int = 4) -> str:
    return f"{'🔹' * step}{'▫️' * (total - step)}"

# ═══════════════════════════════════════════════════════════════
# 💬 ТЕКСТЫ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════

WELCOME_MESSAGE = """
🖤 <b>B.L.A.C.K.A.N.G.E.L</b> 🖤

⚔️ <i>Семья • Честь • Сила</i>

Приветствуем тебя, воин! 👋

Ты стоишь у врат легендарной семьи, где рождаются легенды и куются нерушимые узы братства.


🏆 <b>Что мы предлагаем:</b>

🤝 Братство единомышленников
⚔️ Совместные победы
📚 Обучение и развитие
💬 Общение 24/7
🎁 Эксклюзивные ивенты
👑 Путь к величию


📜 <b>Наш кодекс:</b>

◈ Уважение к каждому брату
◈ Верность семье
◈ Честь в бою и жизни
◈ Взаимопомощь


⚡ <b>Готов стать частью легенды?</b>
"""

ABOUT_MESSAGE = """
📖 <b>О семье B.L.A.C.K.A.N.G.E.L</b>

📅 Основание: 2024 год
👥 Численность: 50+ воинов
🏆 Статус: Элитная семья


⚔️ <b>Наши достижения:</b>

🥇 Топ семья сервера
🏆 Победители турниров
⭐ 100+ совместных побед
💎 Элитный состав


<i>«В единстве — наша сила,
В братстве — наша победа»</i>

🖤 <b>B.L.A.C.K.A.N.G.E.L</b>
"""

CONTACT_MESSAGE = """
📞 <b>Связь с нами</b>


👑 <b>Руководство:</b>

🔱 Глава: @username
⚔️ Зам: @username
🛡️ Офицер: @username


💡 <b>Как связаться:</b>

📝 Подай заявку через бота
💬 Напиши руководству в ЛС
⏰ Ответ: до 24 часов

🖤 <b>B.L.A.C.K.A.N.G.E.L</b>
"""

# ═══════════════════════════════════════════════════════════════
# 🎛️ КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Подать заявку", callback_data="apply")],
        [
            InlineKeyboardButton(text="📖 О семье", callback_data="about"),
            InlineKeyboardButton(text="📞 Контакты", callback_data="contact")
        ]
    ])

def get_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить", callback_data="confirm_send")],
        [InlineKeyboardButton(text="🔄 Заново", callback_data="apply")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_application")]
    ])

def get_admin_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")
        ],
        [InlineKeyboardButton(text="💬 Написать", url=f"tg://user?id={user_id}")]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_application")]
    ])

# ═══════════════════════════════════════════════════════════════
# 📨 ОБРАБОТЧИКИ КОМАНД
# ═══════════════════════════════════════════════════════════════

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    await state.clear()
    await message.answer(
        WELCOME_MESSAGE,
        parse_mode=ParseMode.HTML,
        reply_markup=get_start_keyboard()
    )

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    await state.clear()
    await message.answer("❌ Отменено\n\nНажми /start чтобы начать")

# ═══════════════════════════════════════════════════════════════
# 🔘 CALLBACK ОБРАБОТЧИКИ
# ═══════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        WELCOME_MESSAGE,
        parse_mode=ParseMode.HTML,
        reply_markup=get_start_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery):
    await callback.message.edit_text(
        ABOUT_MESSAGE,
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "contact")
async def show_contact(callback: types.CallbackQuery):
    await callback.message.edit_text(
        CONTACT_MESSAGE,
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "apply")
async def start_application(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    progress = get_progress(1)
    
    text = f"""
📝 <b>Анкета кандидата</b>

{progress} <i>Вопрос 1 из 4</i>


🎮 <b>Твой ник в игре?</b>

Напиши свой игровой никнейм
"""
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ApplicationForm.waiting_for_nickname)
    await callback.answer("📝 Заполняем анкету!")

@dp.callback_query(F.data == "cancel_application")
async def cancel_application(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    text = """
❌ <b>Отменено</b>

Заполнение анкеты отменено.
Если передумаешь — возвращайся!

🖤 <b>B.L.A.C.K.A.N.G.E.L</b>
"""
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

# ═══════════════════════════════════════════════════════════════
# 📝 ОБРАБОТЧИКИ АНКЕТЫ
# ═══════════════════════════════════════════════════════════════

@dp.message(ApplicationForm.waiting_for_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    nickname = message.text.strip()
    
    if len(nickname) < 2 or len(nickname) > 50:
        await message.answer("⚠️ Ник должен быть от 2 до 50 символов")
        return
    
    await state.update_data(nickname=nickname)
    
    progress = get_progress(2)
    
    text = f"""
📝 <b>Анкета кандидата</b>

{progress} <i>Вопрос 2 из 4</i>

✅ Ник: <code>{escape_html(nickname)}</code>


👤 <b>Как тебя зовут?</b>

Напиши своё имя
"""
    
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_cancel_keyboard())
    await state.set_state(ApplicationForm.waiting_for_name)

@dp.message(ApplicationForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    name = message.text.strip()
    
    if len(name) < 2 or len(name) > 50:
        await message.answer("⚠️ Имя должно быть от 2 до 50 символов")
        return
    
    await state.update_data(name=name)
    data = await state.get_data()
    
    progress = get_progress(3)
    
    text = f"""
📝 <b>Анкета кандидата</b>

{progress} <i>Вопрос 3 из 4</i>

✅ Ник: <code>{escape_html(data['nickname'])}</code>
✅ Имя: <code>{escape_html(name)}</code>


📅 <b>Сколько тебе лет?</b>

Напиши свой возраст
"""
    
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_cancel_keyboard())
    await state.set_state(ApplicationForm.waiting_for_age)

@dp.message(ApplicationForm.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    age_text = message.text.strip()
    
    if not age_text.isdigit():
        await message.answer("⚠️ Введи возраст числом")
        return
    
    age = int(age_text)
    
    if age < 10 or age > 100:
        await message.answer("⚠️ Введи реальный возраст")
        return
    
    await state.update_data(age=age)
    data = await state.get_data()
    
    progress = get_progress(4)
    
    text = f"""
📝 <b>Анкета кандидата</b>

{progress} <i>Последний вопрос!</i>

✅ Ник: <code>{escape_html(data['nickname'])}</code>
✅ Имя: <code>{escape_html(data['name'])}</code>
✅ Возраст: <code>{age} лет</code>


📱 <b>Твой номер телефона в игре?</b>

Напиши свой игровой номер телефона
"""
    
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_cancel_keyboard())
    await state.set_state(ApplicationForm.waiting_for_phone)

@dp.message(ApplicationForm.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    phone = message.text.strip()
    
    if len(phone) < 2 or len(phone) > 30:
        await message.answer("⚠️ Некорректный номер телефона")
        return
    
    await state.update_data(phone=phone)
    data = await state.get_data()
    
    preview_text = f"""
✅ <b>Анкета заполнена!</b>


📋 <b>Проверь данные:</b>

🎮 Ник: <code>{escape_html(data['nickname'])}</code>
👤 Имя: <code>{escape_html(data['name'])}</code>
📅 Возраст: <code>{data['age']} лет</code>
📱 Телефон в игре: <code>{escape_html(phone)}</code>


⚡ <b>Всё верно?</b>
"""
    
    await message.answer(
        preview_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_confirm_keyboard()
    )
    
    await state.set_state(ApplicationForm.confirm_application)

# ═══════════════════════════════════════════════════════════════
# 📤 ОТПРАВКА ЗАЯВКИ
# ═══════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "confirm_send")
async def confirm_and_send_application(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    if not data:
        await callback.message.edit_text("❌ Ошибка! Нажми /start")
        await callback.answer()
        return
    
    user = callback.from_user
    username = f"@{user.username}" if user.username else "Нет username"
    
    # Заявка для админов
    application_text = f"""
🆕 <b>Новая заявка</b>


👤 <b>Кандидат:</b>

🎮 Ник: <code>{escape_html(data['nickname'])}</code>
📝 Имя: <code>{escape_html(data['name'])}</code>
📅 Возраст: <code>{data['age']} лет</code>
📱 Телефон в игре: <code>{escape_html(data['phone'])}</code>


📱 <b>Контакт:</b>
{username}
ID: <code>{user.id}</code>
🕐 {datetime.now().strftime("%d.%m.%Y %H:%M")}
"""
    
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            message_thread_id=APPLICATIONS_TOPIC_ID,
            text=application_text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_admin_keyboard(user.id)
        )
        
        success_text = f"""
🎉 <b>Заявка отправлена!</b>

Спасибо, <b>{escape_html(data['name'])}</b>!

Твоя заявка отправлена на рассмотрение руководству семьи.


⏳ <b>Что дальше:</b>

📋 Заявка рассматривается
⏰ Срок: 1-24 часа
📱 Уведомим тебя о решении


💡 Не отключай уведомления!

🖤 <b>B.L.A.C.K.A.N.G.E.L</b>
"""
        
        await callback.message.edit_text(success_text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await callback.message.edit_text("❌ Ошибка отправки!\n\nПопробуй позже или напиши /start")
    
    await state.clear()
    await callback.answer("✅ Отправлено!")

# ═══════════════════════════════════════════════════════════════
# 👑 РЕШЕНИЯ АДМИНОВ
# ═══════════════════════════════════════════════════════════════

@dp.callback_query(F.data.startswith("accept_"))
async def accept_application(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    admin = callback.from_user
    
    try:
        accept_text = f"""
🎉 <b>Поздравляем!</b>

Твоя заявка в семью <b>B.L.A.C.K.A.N.G.E.L</b> одобрена!

Добро пожаловать в семью! 🖤


🔗 <b>Ссылка для вступления:</b>
👉 <a href="{WELCOME_LINK}">Нажми сюда</a>


📌 <b>Важно:</b>

◈ Прочитай правила
◈ Представься в чате
◈ Добавь тег семьи в ник


Вместе мы — сила! 💪

🖤 <b>B.L.A.C.K.A.N.G.E.L</b>
"""
        
        await bot.send_message(
            chat_id=user_id,
            text=accept_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        admin_name = escape_html(admin.username or admin.first_name)
        new_text = callback.message.text + f"\n\n✅ <b>Принято</b> — @{admin_name}"
        
        await callback.message.edit_text(new_text, parse_mode=ParseMode.HTML)
        await callback.answer("✅ Принято!", show_alert=True)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await callback.answer("❌ Не удалось уведомить", show_alert=True)

@dp.callback_query(F.data.startswith("reject_"))
async def reject_application(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    admin = callback.from_user
    
    try:
        reject_text = """
😔 <b>К сожалению...</b>

Твоя заявка в семью <b>B.L.A.C.K.A.N.G.E.L</b> отклонена.


💡 <b>Возможные причины:</b>

◈ Недостаточный уровень
◈ Неполная анкета
◈ Другие причины


📝 Ты можешь подать заявку позже, когда будешь готов.

Не расстраивайся!
Двери открыты для достойных. 🍀

🖤 <b>B.L.A.C.K.A.N.G.E.L</b>
"""
        
        await bot.send_message(
            chat_id=user_id,
            text=reject_text,
            parse_mode=ParseMode.HTML
        )
        
        admin_name = escape_html(admin.username or admin.first_name)
        new_text = callback.message.text + f"\n\n❌ <b>Отклонено</b> — @{admin_name}"
        
        await callback.message.edit_text(new_text, parse_mode=ParseMode.HTML)
        await callback.answer("❌ Отклонено!", show_alert=True)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await callback.answer("❌ Не удалось уведомить", show_alert=True)

# ═══════════════════════════════════════════════════════════════
# 🚫 ИГНОР ГРУПП
# ═══════════════════════════════════════════════════════════════

@dp.message()
async def handle_other(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("👋 Нажми /start")

# ═══════════════════════════════════════════════════════════════
# 🚀 ЗАПУСК
# ═══════════════════════════════════════════════════════════════

async def main():
    logger.info("🖤 Бот B.L.A.C.K.A.N.G.E.L запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
