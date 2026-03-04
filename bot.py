import asyncio
import logging
import html
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from aiogram.enums import ParseMode

# ═══════════════════════════════════════════════════════════════
# ⚙️ НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════

BOT_TOKEN = "8623199291:AAFDPTyXvdqbI3VNy3VPTPftHzu_u16hA_4"  # Токен от @BotFather

# ID группы (добавьте -100 перед числом из ссылки)
ADMIN_CHAT_ID = -1003800032106

# ID топика для заявок (число после последнего / в ссылке)
APPLICATIONS_TOPIC_ID = 5

# Ссылка на раздел для принятых участников
WELCOME_LINK = "https://t.me/c/3800032106/1"

# ═══════════════════════════════════════════════════════════════
# 📝 ЛОГИРОВАНИЕ
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    waiting_for_level = State()
    waiting_for_city = State()
    waiting_for_family_understanding = State()
    confirm_application = State()

# ═══════════════════════════════════════════════════════════════
# 🎨 ДЕКОРАТИВНЫЕ ЭЛЕМЕНТЫ
# ═══════════════════════════════════════════════════════════════

def escape_html(text: str) -> str:
    """Экранирует HTML символы"""
    return html.escape(str(text))

def get_progress_bar(step: int, total: int = 6) -> str:
    """Создаёт красивый прогресс-бар"""
    filled = "▰" * step
    empty = "▱" * (total - step)
    percentage = int((step / total) * 100)
    return f"{filled}{empty} {percentage}%"

def get_step_indicator(step: int, total: int = 6) -> str:
    """Индикатор шагов"""
    steps = ""
    for i in range(1, total + 1):
        if i < step:
            steps += "✅"
        elif i == step:
            steps += "📝"
        else:
            steps += "⬜"
    return steps

# ═══════════════════════════════════════════════════════════════
# 💬 ТЕКСТЫ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════

WELCOME_MESSAGE = """
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>  🖤 <b>B.L.A.C.K.A.N.G.E.L</b> 🖤  <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

         ⚔️ <i>Семья • Честь • Сила</i> ⚔️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 <b>Приветствуем тебя, воин!</b>

Ты находишься у врат легендарной семьи
<b>B.L.A.C.K.A.N.G.E.L</b> — места, где рождаются
легенды и куются нерушимые узы братства!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🏆 ЧТО МЫ ПРЕДЛАГАЕМ:</b>

   🤝 Братство единомышленников
   ⚔️ Совместные победы и битвы
   📚 Обучение и развитие
   💬 Общение 24/7
   🎁 Эксклюзивные ивенты
   👑 Путь к величию

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📜 КОДЕКС ЧЕСТИ:</b>

   ◈ Уважение к каждому брату
   ◈ Верность семье превыше всего
   ◈ Честь в бою и в жизни
   ◈ Взаимопомощь без границ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>⚡ Готов стать частью легенды?</b>
<i>Нажми кнопку ниже и докажи свою доблесть!</i>

<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>    🖤 <i>Семья превыше всего</i> 🖤    <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>
"""

ABOUT_MESSAGE = """
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   📖 <b>ИСТОРИЯ СЕМЬИ</b> 📖   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📅 Основание:</b> 2024 год
<b>👥 Численность:</b> 50+ воинов
<b>🏆 Статус:</b> Элитная семья

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>⚔️ НАШИ ДОСТИЖЕНИЯ:</b>

   🥇 Топ-1 семья сервера
   🏆 Победители турниров
   ⭐ 100+ совместных побед
   💎 Элитный состав игроков

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 НАШИ ПРИНЦИПЫ:</b>

   ◈ Один за всех, все за одного
   ◈ Никогда не бросаем своих
   ◈ Честная игра
   ◈ Постоянное развитие

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<i>«В единстве — наша сила,
В братстве — наша победа»</i>

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>
"""

CONTACT_MESSAGE = """
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   📞 <b>СВЯЗЬ С НАМИ</b> 📞   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>👑 РУКОВОДСТВО СЕМЬИ:</b>

   🔱 <b>Глава:</b> @username
   ⚔️ <b>Зам. главы:</b> @username
   🛡️ <b>Офицеры:</b> @username

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 КАК СВЯЗАТЬСЯ:</b>

   📝 Подай заявку через бота
   💬 Напиши руководству в ЛС
   ⏰ Время ответа: до 24 часов

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<i>Мы всегда рады новым воинам!</i>

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>
"""

# ═══════════════════════════════════════════════════════════════
# 🎛️ КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════

def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ ПОДАТЬ ЗАЯВКУ ⚔️", callback_data="apply")],
        [
            InlineKeyboardButton(text="📖 О семье", callback_data="about"),
            InlineKeyboardButton(text="📞 Контакты", callback_data="contact")
        ],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])

def get_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ ОТПРАВИТЬ ЗАЯВКУ", callback_data="confirm_send")],
        [InlineKeyboardButton(text="🔄 Заполнить заново", callback_data="apply")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_application")]
    ])

def get_admin_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ ПРИНЯТЬ", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton(text="❌ ОТКЛОНИТЬ", callback_data=f"reject_{user_id}")
        ],
        [InlineKeyboardButton(text="💬 Написать кандидату", url=f"tg://user?id={user_id}")]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ])

def get_cancel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить заполнение", callback_data="cancel_application")]
    ])

# ═══════════════════════════════════════════════════════════════
# 📨 ОБРАБОТЧИКИ КОМАНД
# ═══════════════════════════════════════════════════════════════

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # Игнорируем сообщения из групп
    if message.chat.type != "private":
        return
    
    await state.clear()
    logger.info(f"Пользователь {message.from_user.id} запустил бота")
    
    await message.answer(
        WELCOME_MESSAGE,
        parse_mode=ParseMode.HTML,
        reply_markup=get_start_keyboard()
    )

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "🤷 Нечего отменять.\nНажми /start чтобы начать."
        )
        return
    
    await state.clear()
    await message.answer(
        "❌ <b>Заполнение отменено</b>\n\n"
        "Нажми /start чтобы начать заново.",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    if message.chat.type != "private":
        return
    
    help_text = """
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   ❓ <b>ПОМОЩЬ</b> ❓   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

<b>📜 КОМАНДЫ:</b>

   /start — Главное меню
   /cancel — Отменить заполнение
   /help — Эта справка

<b>📝 КАК ПОДАТЬ ЗАЯВКУ:</b>

   1️⃣ Нажми "Подать заявку"
   2️⃣ Ответь на 6 вопросов
   3️⃣ Проверь данные
   4️⃣ Подтверди отправку
   5️⃣ Жди ответа!

<b>⏰ СРОКИ:</b>
   Рассмотрение: 1-24 часа

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>
"""
    await message.answer(help_text, parse_mode=ParseMode.HTML, reply_markup=get_back_keyboard())

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

@dp.callback_query(F.data == "help")
async def show_help(callback: types.CallbackQuery):
    help_text = """
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   ❓ <b>ПОМОЩЬ</b> ❓   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

<b>📝 КАК ПОДАТЬ ЗАЯВКУ:</b>

   1️⃣ Нажми "Подать заявку"
   2️⃣ Ответь на 6 вопросов
   3️⃣ Проверь данные
   4️⃣ Подтверди отправку
   5️⃣ Жди ответа!

<b>⏰ СРОКИ РАССМОТРЕНИЯ:</b>
   От 1 часа до 24 часов

<b>💡 СОВЕТЫ:</b>
   ◈ Отвечай честно
   ◈ Пиши подробно
   ◈ Будь собой!

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>
"""
    await callback.message.edit_text(
        help_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "apply")
async def start_application(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    step = 1
    progress = get_progress_bar(step)
    steps = get_step_indicator(step)
    
    text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   📝 <b>АНКЕТА КАНДИДАТА</b> 📝   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

{steps}
<b>{progress}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>❓ ВОПРОС {step} ИЗ 6</b>

🎮 <b>Как тебя зовут в игре?</b>

<i>Напиши свой игровой никнейм:</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ApplicationForm.waiting_for_nickname)
    await callback.answer("📝 Начинаем заполнение анкеты!")

@dp.callback_query(F.data == "cancel_application")
async def cancel_application(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    text = """
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   ❌ <b>ОТМЕНЕНО</b> ❌   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

Заполнение анкеты отменено.

<i>Если передумаешь — возвращайся!
Мы всегда рады новым воинам.</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>
"""
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_keyboard()
    )
    await callback.answer("❌ Заявка отменена")

# ═══════════════════════════════════════════════════════════════
# 📝 ОБРАБОТЧИКИ АНКЕТЫ
# ═══════════════════════════════════════════════════════════════

@dp.message(ApplicationForm.waiting_for_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    nickname = message.text.strip()
    
    if len(nickname) < 2 or len(nickname) > 50:
        await message.answer(
            "⚠️ <b>Некорректный ник!</b>\n"
            "Длина должна быть от 2 до 50 символов.",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(nickname=nickname)
    
    step = 2
    progress = get_progress_bar(step)
    steps = get_step_indicator(step)
    
    text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   📝 <b>АНКЕТА КАНДИДАТА</b> 📝   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

{steps}
<b>{progress}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ <b>Ник:</b> <code>{escape_html(nickname)}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>❓ ВОПРОС {step} ИЗ 6</b>

👤 <b>Как тебя зовут?</b>

<i>Напиши своё реальное имя:</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_cancel_keyboard())
    await state.set_state(ApplicationForm.waiting_for_name)

@dp.message(ApplicationForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    name = message.text.strip()
    
    if len(name) < 2 or len(name) > 50:
        await message.answer(
            "⚠️ <b>Некорректное имя!</b>\n"
            "Длина должна быть от 2 до 50 символов.",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(name=name)
    data = await state.get_data()
    
    step = 3
    progress = get_progress_bar(step)
    steps = get_step_indicator(step)
    
    text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   📝 <b>АНКЕТА КАНДИДАТА</b> 📝   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

{steps}
<b>{progress}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ <b>Ник:</b> <code>{escape_html(data['nickname'])}</code>
✅ <b>Имя:</b> <code>{escape_html(name)}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>❓ ВОПРОС {step} ИЗ 6</b>

📅 <b>Сколько тебе лет?</b>

<i>Напиши свой возраст числом:</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_cancel_keyboard())
    await state.set_state(ApplicationForm.waiting_for_age)

@dp.message(ApplicationForm.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    age_text = message.text.strip()
    
    if not age_text.isdigit():
        await message.answer(
            "⚠️ <b>Введи возраст числом!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    age = int(age_text)
    
    if age < 10 or age > 100:
        await message.answer(
            "⚠️ <b>Введи реальный возраст!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(age=age)
    data = await state.get_data()
    
    step = 4
    progress = get_progress_bar(step)
    steps = get_step_indicator(step)
    
    text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   📝 <b>АНКЕТА КАНДИДАТА</b> 📝   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

{steps}
<b>{progress}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ <b>Ник:</b> <code>{escape_html(data['nickname'])}</code>
✅ <b>Имя:</b> <code>{escape_html(data['name'])}</code>
✅ <b>Возраст:</b> <code>{age} лет</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>❓ ВОПРОС {step} ИЗ 6</b>

⚔️ <b>Какой у тебя уровень в игре?</b>

<i>Напиши свой текущий уровень:</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_cancel_keyboard())
    await state.set_state(ApplicationForm.waiting_for_level)

@dp.message(ApplicationForm.waiting_for_level)
async def process_level(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    level = message.text.strip()
    
    if len(level) > 30:
        await message.answer(
            "⚠️ <b>Слишком длинный ответ!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(level=level)
    data = await state.get_data()
    
    step = 5
    progress = get_progress_bar(step)
    steps = get_step_indicator(step)
    
    text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   📝 <b>АНКЕТА КАНДИДАТА</b> 📝   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

{steps}
<b>{progress}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ <b>Ник:</b> <code>{escape_html(data['nickname'])}</code>
✅ <b>Имя:</b> <code>{escape_html(data['name'])}</code>
✅ <b>Возраст:</b> <code>{data['age']} лет</code>
✅ <b>Уровень:</b> <code>{escape_html(level)}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>❓ ВОПРОС {step} ИЗ 6</b>

🏙️ <b>С какого ты города?</b>

<i>Напиши название своего города:</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_cancel_keyboard())
    await state.set_state(ApplicationForm.waiting_for_city)

@dp.message(ApplicationForm.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    city = message.text.strip()
    
    if len(city) < 2 or len(city) > 50:
        await message.answer(
            "⚠️ <b>Некорректное название города!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(city=city)
    data = await state.get_data()
    
    step = 6
    progress = get_progress_bar(step)
    steps = get_step_indicator(step)
    
    text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   📝 <b>АНКЕТА КАНДИДАТА</b> 📝   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

{steps}
<b>{progress}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ <b>Ник:</b> <code>{escape_html(data['nickname'])}</code>
✅ <b>Имя:</b> <code>{escape_html(data['name'])}</code>
✅ <b>Возраст:</b> <code>{data['age']} лет</code>
✅ <b>Уровень:</b> <code>{escape_html(data['level'])}</code>
✅ <b>Город:</b> <code>{escape_html(city)}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>❓ ПОСЛЕДНИЙ ВОПРОС!</b>

👨‍👩‍👧‍👦 <b>Что для тебя значит семья?</b>

<i>Напиши, что для тебя значит быть частью
игровой семьи, чего ожидаешь и что
готов дать взамен:</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=get_cancel_keyboard())
    await state.set_state(ApplicationForm.waiting_for_family_understanding)

@dp.message(ApplicationForm.waiting_for_family_understanding)
async def process_family_understanding(message: types.Message, state: FSMContext):
    if message.chat.type != "private":
        return
    
    understanding = message.text.strip()
    
    if len(understanding) < 10:
        await message.answer(
            "⚠️ <b>Напиши более развёрнутый ответ!</b>\n"
            "<i>Минимум 10 символов</i>",
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(understanding) > 1000:
        await message.answer(
            "⚠️ <b>Слишком длинный ответ!</b>\n"
            "<i>Сократи до 1000 символов</i>",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(family_understanding=understanding)
    data = await state.get_data()
    
    # Экранируем данные
    safe_nickname = escape_html(data['nickname'])
    safe_name = escape_html(data['name'])
    safe_level = escape_html(data['level'])
    safe_city = escape_html(data['city'])
    safe_understanding = escape_html(understanding)
    
    preview_text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>   ✅ <b>АНКЕТА ЗАПОЛНЕНА!</b> ✅   <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

✅✅✅✅✅✅
<b>▰▰▰▰▰▰ 100%</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 ТВОЯ АНКЕТА:</b>

   🎮 <b>Ник:</b> <code>{safe_nickname}</code>
   👤 <b>Имя:</b> <code>{safe_name}</code>
   📅 <b>Возраст:</b> <code>{data['age']} лет</code>
   ⚔️ <b>Уровень:</b> <code>{safe_level}</code>
   🏙️ <b>Город:</b> <code>{safe_city}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💭 ПОНИМАНИЕ СЕМЬИ:</b>

<i>{safe_understanding}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>⚡ Всё верно? Отправляем?</b>

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>
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
        await callback.message.edit_text(
            "❌ Ошибка! Данные не найдены.\nНажми /start"
        )
        await callback.answer()
        return
    
    user = callback.from_user
    username = f"@{user.username}" if user.username else "Не указан"
    
    # Экранируем данные
    safe_nickname = escape_html(data['nickname'])
    safe_name = escape_html(data['name'])
    safe_level = escape_html(data['level'])
    safe_city = escape_html(data['city'])
    safe_understanding = escape_html(data['family_understanding'])
    
    # Заявка для админов
    application_text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>  🆕 <b>НОВАЯ ЗАЯВКА</b> 🆕  <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

<b>👤 ДАННЫЕ КАНДИДАТА:</b>

   🎮 <b>Ник:</b> <code>{safe_nickname}</code>
   📝 <b>Имя:</b> <code>{safe_name}</code>
   📅 <b>Возраст:</b> <code>{data['age']} лет</code>
   ⚔️ <b>Уровень:</b> <code>{safe_level}</code>
   🏙️ <b>Город:</b> <code>{safe_city}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💭 ПОНИМАНИЕ СЕМЬИ:</b>

<i>{safe_understanding}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📱 КОНТАКТ:</b>

   👤 <b>Telegram:</b> {username}
   🆔 <b>ID:</b> <code>{user.id}</code>
   📆 <b>Дата:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    try:
        # Отправляем в топик заявок
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            message_thread_id=APPLICATIONS_TOPIC_ID,
            text=application_text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_admin_keyboard(user.id)
        )
        
        logger.info(f"Заявка от {user.id} отправлена")
        
        # Подтверждение пользователю
        success_text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>  🎉 <b>ЗАЯВКА ОТПРАВЛЕНА!</b> 🎉  <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

<b>Спасибо, {safe_name}!</b>

Твоя заявка успешно отправлена
на рассмотрение руководству семьи.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>⏳ ЧТО ДАЛЬШЕ:</b>

   📋 Заявка на рассмотрении
   ⏰ Срок: от 1 до 24 часов
   📱 Уведомим тебя о решении

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 СОВЕТ:</b>
Не отключай уведомления, чтобы
не пропустить наш ответ!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<i>Желаем удачи, воин!</i> ⚔️

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>
"""
        
        await callback.message.edit_text(
            success_text,
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        
        await callback.message.edit_text(
            "❌ <b>Ошибка отправки!</b>\n\n"
            "Попробуй позже или свяжись с админом.\n"
            "Нажми /start",
            parse_mode=ParseMode.HTML
        )
    
    await state.clear()
    await callback.answer("✅ Заявка отправлена!")

# ═══════════════════════════════════════════════════════════════
# 👑 ОБРАБОТКА РЕШЕНИЙ АДМИНОВ
# ═══════════════════════════════════════════════════════════════

@dp.callback_query(F.data.startswith("accept_"))
async def accept_application(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    admin = callback.from_user
    
    try:
        # Уведомление пользователю о принятии
        accept_text = f"""
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>  🎉 <b>ПОЗДРАВЛЯЕМ!</b> 🎉  <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

   ✅ <b>ТВОЯ ЗАЯВКА ОДОБРЕНА!</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖤 <b>Добро пожаловать в семью
   B.L.A.C.K.A.N.G.E.L!</b> 🖤

Ты стал частью легенды!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🔗 ССЫЛКА ДЛЯ ВСТУПЛЕНИЯ:</b>

👉 <a href="{WELCOME_LINK}">НАЖМИ СЮДА</a> 👈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📌 ВАЖНО:</b>

   ◈ Прочитай правила семьи
   ◈ Представься в чате
   ◈ Добавь тег семьи в ник

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<i>Рады видеть тебя в наших рядах!</i>
<i>Вместе мы — сила!</i> 💪

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>
<b>⚔️ Семья • Честь • Сила ⚔️</b>
"""
        
        await bot.send_message(
            chat_id=user_id,
            text=accept_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        # Обновляем сообщение с заявкой
        admin_name = escape_html(admin.username or admin.first_name)
        new_text = callback.message.text + f"\n\n✅ <b>ПРИНЯТО</b>\n👤 Принял: @{admin_name}\n⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        await callback.message.edit_text(
            new_text,
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"Заявка {user_id} принята админом {admin.id}")
        await callback.answer("✅ Заявка принята! Кандидат уведомлён.", show_alert=True)
        
    except Exception as e:
        logger.error(f"Ошибка при принятии: {e}")
        await callback.answer("❌ Не удалось уведомить пользователя", show_alert=True)

@dp.callback_query(F.data.startswith("reject_"))
async def reject_application(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    admin = callback.from_user
    
    try:
        # Уведомление пользователю об отказе
        reject_text = """
<b>┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓</b>
<b>┃</b>  😔 <b>К СОЖАЛЕНИЮ...</b> 😔  <b>┃</b>
<b>┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛</b>

   ❌ <b>ТВОЯ ЗАЯВКА ОТКЛОНЕНА</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💡 ВОЗМОЖНЫЕ ПРИЧИНЫ:</b>

   ◈ Недостаточный уровень
   ◈ Неполная анкета
   ◈ Другие причины

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📝 ЧТО ДЕЛАТЬ:</b>

Ты можешь подать заявку повторно
через некоторое время, когда:

   ◈ Повысишь уровень
   ◈ Заполнишь анкету подробнее
   ◈ Подготовишься лучше

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<i>Не расстраивайся!
Двери всегда открыты для достойных.</i>

<b>🖤 B.L.A.C.K.A.N.G.E.L 🖤</b>
"""
        
        await bot.send_message(
            chat_id=user_id,
            text=reject_text,
            parse_mode=ParseMode.HTML
        )
        
        # Обновляем сообщение с заявкой
        admin_name = escape_html(admin.username or admin.first_name)
        new_text = callback.message.text + f"\n\n❌ <b>ОТКЛОНЕНО</b>\n👤 Отклонил: @{admin_name}\n⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        await callback.message.edit_text(
            new_text,
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"Заявка {user_id} отклонена админом {admin.id}")
        await callback.answer("❌ Заявка отклонена. Кандидат уведомлён.", show_alert=True)
        
    except Exception as e:
        logger.error(f"Ошибка при отклонении: {e}")
        await callback.answer("❌ Не удалось уведомить пользователя", show_alert=True)

# ═══════════════════════════════════════════════════════════════
# 🚫 ИГНОРИРУЕМ СООБЩЕНИЯ В ГРУППАХ
# ═══════════════════════════════════════════════════════════════

@dp.message()
async def handle_other_messages(message: types.Message, state: FSMContext):
    # Игнорируем все сообщения из групп
    if message.chat.type != "private":
        return
    
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "🤔 Не понимаю команду.\n\n"
            "Нажми /start чтобы начать."
        )

# ═══════════════════════════════════════════════════════════════
# 🚀 ЗАПУСК
# ═══════════════════════════════════════════════════════════════

async def on_startup():
    logger.info("=" * 50)
    logger.info("🖤 Бот B.L.A.C.K.A.N.G.E.L запускается...")
    logger.info("=" * 50)
    
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот: @{bot_info.username}")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

async def main():
    dp.startup.register(on_startup)
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
