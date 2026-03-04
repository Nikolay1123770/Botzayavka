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
# ⚙️ НАСТРОЙКИ - ОБЯЗАТЕЛЬНО ЗАМЕНИТЕ НА СВОИ ДАННЫЕ
# ═══════════════════════════════════════════════════════════════

BOT_TOKEN = "8623199291:AAFDPTyXvdqbI3VNy3VPTPftHzu_u16hA_4"  # Токен от @BotFather
ADMIN_CHAT_ID = -5211230298  # ID чата/группы для уведомлений о заявках

# ═══════════════════════════════════════════════════════════════
# 📝 НАСТРОЙКА ЛОГИРОВАНИЯ
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# 🤖 ИНИЦИАЛИЗАЦИЯ БОТА
# ═══════════════════════════════════════════════════════════════

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# ═══════════════════════════════════════════════════════════════
# 📋 СОСТОЯНИЯ ДЛЯ АНКЕТЫ (FSM)
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
# 🔧 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════

def escape_html(text: str) -> str:
    """Экранирует HTML символы в тексте"""
    return html.escape(str(text))

# ═══════════════════════════════════════════════════════════════
# 💬 ТЕКСТЫ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════

WELCOME_MESSAGE = """
🖤✨ <b>Вас приветствует семья B.L.A.C.K.A.N.G.E.L</b> ✨🖤

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 <b>Добро пожаловать, путник!</b>

Мы рады, что ты заинтересовался нашей семьёй!

🔥 <b>B.L.A.C.K.A.N.G.E.L</b> — это не просто клан или гильдия. Это настоящая семья, где каждый готов поддержать друг друга в любой ситуации!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ <b>Что мы предлагаем:</b>

🤝 Дружный и сплочённый коллектив
📚 Помощь и обучение новичков  
🎮 Совместные активности и ивенты
💬 Общение и поддержка 24/7
🏆 Совместные достижения целей

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📜 <b>Наши пр��нципы:</b>
• Уважение к каждому члену семьи
• Взаимопомощь и поддержка
• Активность и участие в жизни семьи
• Честность и открытость

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 <b>Хочешь стать частью нашей семьи?</b>
Нажми кнопку ниже и заполни небольшую анкету!

🖤 <b>С уважением, семья B.L.A.C.K.A.N.G.E.L</b> 🖤
"""

# ═══════════════════════════════════════════════════════════════
# 🎛️ КЛАВИАТУРЫ
# ═══════════════════════════════════════════════════════════════

def get_start_keyboard():
    """Клавиатура для стартового сообщения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Подать заявку", callback_data="apply")],
        [InlineKeyboardButton(text="ℹ️ О семье", callback_data="about")],
        [InlineKeyboardButton(text="📞 Связаться с нами", callback_data="contact")]
    ])

def get_confirm_keyboard():
    """Клавиатура подтверждения заявки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить заявку", callback_data="confirm_send")],
        [InlineKeyboardButton(text="🔄 Заполнить заново", callback_data="apply")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_application")]
    ])

def get_admin_keyboard(user_id: int):
    """Клавиатура для админов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")
        ],
        [InlineKeyboardButton(text="💬 Написать", url=f"tg://user?id={user_id}")]
    ])

def get_back_to_menu_keyboard():
    """Клавиатура возврата в меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Вернуться в меню", callback_data="back_to_menu")]
    ])

# ═══════════════════════════════════════════════════════════════
# 📨 ОБРАБОТЧИКИ КОМАНД
# ═══════════════════════════════════════════════════════════════

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    logger.info(f"Пользователь {message.from_user.id} ({message.from_user.username}) запустил бота")
    
    await message.answer(
        WELCOME_MESSAGE,
        parse_mode=ParseMode.HTML,
        reply_markup=get_start_keyboard()
    )

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Обработчик команды /cancel"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "🤷 Нечего отменять. Вы не заполняете анкету.\n"
            "Нажмите /start чтобы начать."
        )
        return
    
    await state.clear()
    
    await message.answer(
        "❌ <b>Заполнение анкеты отменено.</b>\n\n"
        "Чтобы начать заново, нажмите /start",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
🆘 <b>Помощь по боту</b>

<b>Доступные команды:</b>
/start - Начать работу с ботом
/cancel - Отменить заполнение анкеты
/help - Показать это сообщение

<b>Как подать заявку:</b>
1. Нажмите /start
2. Нажмите кнопку "Подать заявку"
3. Ответьте на все вопросы
4. Подтвердите отправку

По всем вопросам обращайтесь к администрации семьи.

🖤 <b>B.L.A.C.K.A.N.G.E.L</b>
"""
    await message.answer(help_text, parse_mode=ParseMode.HTML)

# ═══════════════════════════════════════════════════════════════
# 🔘 ОБРАБОТЧИКИ CALLBACK-КНОПОК
# ═══════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await callback.message.edit_text(
        WELCOME_MESSAGE,
        parse_mode=ParseMode.HTML,
        reply_markup=get_start_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery):
    """Информация о семье"""
    about_text = """
🖤 <b>О семье B.L.A.C.K.A.N.G.E.L</b> 🖤

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 <b>Дата основания:</b> 2024 год

👥 <b>Количество участников:</b> 50+

🎯 <b>Наши цели:</b>
• Создание дружного комьюнити
• Помощь друг другу в игре
• Совместное развитие
• Весёлое времяпрепровождение

🏆 <b>Наши достижения:</b>
• Топ семья сервера
• Множество побед в ивентах
• Сплочённый коллектив

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖤 <b>B.L.A.C.K.A.N.G.E.L — Семья превыше всего!</b>
"""
    await callback.message.edit_text(
        about_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "contact")
async def show_contact(callback: types.CallbackQuery):
    """Контакты"""
    contact_text = """
📞 <b>Связаться с нами</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Если у тебя есть вопросы, можешь связаться с администрацией:

👑 <b>Глава семьи:</b> @username
🛡️ <b>Заместитель:</b> @username

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Или просто подай заявку, и мы сами с тобой свяжемся!

🖤 <b>B.L.A.C.K.A.N.G.E.L</b>
"""
    await callback.message.edit_text(
        contact_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "apply")
async def start_application(callback: types.CallbackQuery, state: FSMContext):
    """Начало заполнения анкеты"""
    await state.clear()
    
    text = """
📝 <b>Отлично! Давай заполним анкету для вступления в семью!</b>

ℹ️ Ты можешь отменить заполнение в любой момент командой /cancel

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ <b>Вопрос 1 из 6:</b>

🎮 Напиши свой <b>ник в игре</b>:
"""
    
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML)
    await state.set_state(ApplicationForm.waiting_for_nickname)
    await callback.answer()

@dp.callback_query(F.data == "cancel_application")
async def cancel_application(callback: types.CallbackQuery, state: FSMContext):
    """Отмена заявки"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ <b>Заявка отменена.</b>\n\n"
        "Если передумаешь — возвращайся!\n"
        "Нажми /start чтобы начать заново.\n\n"
        "🖤 <b>B.L.A.C.K.A.N.G.E.L</b>",
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# ═══════════════════════════════════════════════════════════════
# 📝 ОБРАБОТЧИКИ СОСТОЯНИЙ АНКЕТЫ
# ═══════════════════════════════════════════════════════════════

@dp.message(ApplicationForm.waiting_for_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    """Получаем ник в игре"""
    nickname = message.text.strip()
    
    if len(nickname) < 2:
        await message.answer(
            "⚠️ Ник слишком короткий. Введи корректный ник:",
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(nickname) > 50:
        await message.answer(
            "⚠️ Ник слишком длинный. Введи корректный ник:",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(nickname=nickname)
    
    await message.answer(
        "✅ Отлично!\n\n"
        "❓ <b>Вопрос 2 из 6:</b>\n\n"
        "👤 Как тебя <b>зовут</b>? (твоё имя)",
        parse_mode=ParseMode.HTML
    )
    
    await state.set_state(ApplicationForm.waiting_for_name)

@dp.message(ApplicationForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Получаем имя"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer(
            "⚠️ Имя слишком короткое. Введи корректное имя:",
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(name) > 50:
        await message.answer(
            "⚠️ Имя слишком длинное. Введи корректное имя:",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(name=name)
    
    safe_name = escape_html(name)
    
    await message.answer(
        f"✅ Приятно познакомиться, <b>{safe_name}</b>!\n\n"
        "❓ <b>Вопрос 3 из 6:</b>\n\n"
        "📅 <b>Сколько тебе лет?</b>",
        parse_mode=ParseMode.HTML
    )
    
    await state.set_state(ApplicationForm.waiting_for_age)

@dp.message(ApplicationForm.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    """Получаем возраст"""
    age_text = message.text.strip()
    
    if not age_text.isdigit():
        await message.answer(
            "⚠️ Пожалуйста, введи возраст <b>числом</b>:",
            parse_mode=ParseMode.HTML
        )
        return
    
    age = int(age_text)
    
    if age < 10 or age > 100:
        await message.answer(
            "⚠️ Пожалуйста, введи <b>реальный</b> возраст:",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(age=age)
    
    await message.answer(
        "✅ Записал!\n\n"
        "❓ <b>Вопрос 4 из 6:</b>\n\n"
        "⚔️ Какой у тебя <b>уровень в игре</b>?",
        parse_mode=ParseMode.HTML
    )
    
    await state.set_state(ApplicationForm.waiting_for_level)

@dp.message(ApplicationForm.waiting_for_level)
async def process_level(message: types.Message, state: FSMContext):
    """Получаем уровень"""
    level = message.text.strip()
    
    if len(level) > 30:
        await message.answer(
            "⚠️ Слишком длинный ответ. Просто напиши свой уровень:",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(level=level)
    
    await message.answer(
        "✅ Хороший уровень!\n\n"
        "❓ <b>Вопрос 5 из 6:</b>\n\n"
        "🏙️ <b>С какого ты города?</b>",
        parse_mode=ParseMode.HTML
    )
    
    await state.set_state(ApplicationForm.waiting_for_city)

@dp.message(ApplicationForm.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    """Получаем город"""
    city = message.text.strip()
    
    if len(city) < 2:
        await message.answer(
            "⚠️ Название города слишком короткое. Введи корректно:",
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(city) > 50:
        await message.answer(
            "⚠️ Название города слишком длинное. Введи корректно:",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(city=city)
    
    await message.answer(
        "✅ Отлично!\n\n"
        "❓ <b>Вопрос 6 из 6 (последний):</b>\n\n"
        "👨‍👩‍👧‍👦 <b>Какое у тебя понимание семьи?</b>\n\n"
        "<i>Напиши, что для тебя значит быть частью игровой семьи, "
        "чего ты ожидаешь от семьи и что готов дать взамен:</i>",
        parse_mode=ParseMode.HTML
    )
    
    await state.set_state(ApplicationForm.waiting_for_family_understanding)

@dp.message(ApplicationForm.waiting_for_family_understanding)
async def process_family_understanding(message: types.Message, state: FSMContext):
    """Получаем понимание семьи"""
    understanding = message.text.strip()
    
    if len(understanding) < 10:
        await message.answer(
            "⚠️ Пожалуйста, напиши более развёрнутый ответ (минимум 10 символов):",
            parse_mode=ParseMode.HTML
        )
        return
    
    if len(understanding) > 1000:
        await message.answer(
            "⚠️ Ответ слишком длинный. Пожалуйста, сократи его:",
            parse_mode=ParseMode.HTML
        )
        return
    
    await state.update_data(family_understanding=understanding)
    
    # Получаем все данные для предпросмотра
    data = await state.get_data()
    
    # Экранируем все пользовательские данные
    safe_nickname = escape_html(data['nickname'])
    safe_name = escape_html(data['name'])
    safe_level = escape_html(data['level'])
    safe_city = escape_html(data['city'])
    safe_understanding = escape_html(data['family_understanding'])
    
    preview_text = f"""
✅ <b>Отлично! Анкета заполнена!</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 <b>Проверь свои данные:</b>

🎮 <b>Ник в игре:</b> {safe_nickname}
👤 <b>Имя:</b> {safe_name}
📅 <b>Возраст:</b> {data['age']} лет
⚔️ <b>Уровень:</b> {safe_level}
🏙️ <b>Город:</b> {safe_city}

💭 <b>Понимание семьи:</b>
<i>{safe_understanding}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Всё верно? Отправляем заявку?
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
    """Подтверждение и отправка заявки"""
    data = await state.get_data()
    
    if not data:
        await callback.message.edit_text(
            "❌ Произошла ошибка. Данные анкеты не найдены.\n"
            "Пожалуйста, заполните анкету заново: /start"
        )
        await callback.answer()
        return
    
    user = callback.from_user
    username = f"@{user.username}" if user.username else "Не указан"
    
    # Экранируем все пользовательские данные
    safe_nickname = escape_html(data['nickname'])
    safe_name = escape_html(data['name'])
    safe_level = escape_html(data['level'])
    safe_city = escape_html(data['city'])
    safe_understanding = escape_html(data['family_understanding'])
    
    # Формируем текст заявки для администраторов
    application_text = f"""
🆕 <b>НОВАЯ ЗАЯВКА В СЕМЬЮ B.L.A.C.K.A.N.G.E.L</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 <b>Информация о кандидате:</b>

🎮 <b>Ник в игре:</b> {safe_nickname}
📝 <b>Имя:</b> {safe_name}
📅 <b>Возраст:</b> {data['age']} лет
⚔️ <b>Уровень:</b> {safe_level}
🏙️ <b>Город:</b> {safe_city}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💭 <b>Понимание семьи:</b>
<i>{safe_understanding}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 <b>Telegram:</b> {username}
🆔 <b>User ID:</b> <code>{user.id}</code>
📆 <b>Дата заявки:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Отправляем заявку в чат администраторов
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=application_text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_admin_keyboard(user.id)
        )
        
        logger.info(f"Заявка от пользователя {user.id} ({user.username}) успешно отправлена")
        
        # Подтверждение пользователю
        success_text = f"""
🎉 <b>Спасибо, {safe_name}! Твоя заявка успешно отправлена!</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 <b>Твоя анкета:</b>
• Ник: {safe_nickname}
• Имя: {safe_name}
• Возраст: {data['age']} лет
• Уровень: {safe_level}
• Город: {safe_city}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ <b>Что дальше?</b>
Администрация рассмотрит твою заявку и свяжется с тобой в ближайшее время.

💡 Обычно рассмотрение занимает от нескольких часов до 1-2 дней.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖤 <b>С уважением, семья B.L.A.C.K.A.N.G.E.L</b> 🖤
Ожидай ответа! Удачи! 🍀
"""
        
        await callback.message.edit_text(
            success_text,
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки заявки: {e}")
        
        await callback.message.edit_text(
            "❌ <b>Произошла ошибка при отправке заявки.</b>\n\n"
            "Пожалуйста, попробуй позже или свяжись с администратором напрямую.\n\n"
            "Нажми /start чтобы попробовать снова.",
            parse_mode=ParseMode.HTML
        )
    
    await state.clear()
    await callback.answer("Заявка отправлена! ✅")

# ═══════════════════════════════════════════════════════════════
# 👑 ОБРАБОТЧИКИ ДЛЯ АДМИНИСТРАТОРОВ
# ═══════════════════════════════════════════════════════════════

@dp.callback_query(F.data.startswith("accept_"))
async def accept_application(callback: types.CallbackQuery):
    """Принятие заявки администратором"""
    user_id = int(callback.data.split("_")[1])
    admin = callback.from_user
    
    try:
        # Уведомляем пользователя о принятии
        await bot.send_message(
            chat_id=user_id,
            text="""
🎉 <b>ПОЗДРАВЛЯЕМ!</b> 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Твоя заявка в семью <b>B.L.A.C.K.A.N.G.E.L</b> была <b>ОДОБРЕНА</b>!

🖤 <b>Добро пожаловать в семью!</b> 🖤

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 <b>Что дальше:</b>
Скоро с тобой свяжется администрация для дальнейших инструкций по вступлению.

Рады видеть тебя в наших рядах! 💪

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖤 <b>B.L.A.C.K.A.N.G.E.L — Семья превыше всего!</b> 🖤
""",
            parse_mode=ParseMode.HTML
        )
        
        # Обновляем сообщение с заявкой
        admin_name = escape_html(admin.username or admin.first_name)
        new_text = callback.message.text + f"\n\n✅ <b>ЗАЯВКА ПРИНЯТА</b>\n👤 Принял: @{admin_name}"
        
        await callback.message.edit_text(
            new_text,
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"Заявка пользователя {user_id} принята администратором {admin.id}")
        await callback.answer("✅ Заявка принята! Пользователь уведомлён.", show_alert=True)
        
    except Exception as e:
        logger.error(f"Ошибка при принятии заявки: {e}")
        await callback.answer(f"❌ Ошибка: не удалось уведомить пользователя", show_alert=True)

@dp.callback_query(F.data.startswith("reject_"))
async def reject_application(callback: types.CallbackQuery):
    """Отклонение заявки администратором"""
    user_id = int(callback.data.split("_")[1])
    admin = callback.from_user
    
    try:
        # Уведомляем пользователя об отклонении
        await bot.send_message(
            chat_id=user_id,
            text="""
😔 <b>К сожалению...</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Твоя заявка в семью <b>B.L.A.C.K.A.N.G.E.L</b> была отклонена.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 <b>Возможные причины:</b>
• Не соответствие требованиям
• Недостаточно информации в анкете
• Другие причины

📝 Ты можешь попробовать подать заявку позже, более подробно заполнив анкету.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Удачи тебе! 🍀

🖤 <b>B.L.A.C.K.A.N.G.E.L</b>
""",
            parse_mode=ParseMode.HTML
        )
        
        # Обновляем сообщение с заявкой
        admin_name = escape_html(admin.username or admin.first_name)
        new_text = callback.message.text + f"\n\n❌ <b>ЗАЯВКА ОТКЛОНЕНА</b>\n👤 Отклонил: @{admin_name}"
        
        await callback.message.edit_text(
            new_text,
            parse_mode=ParseMode.HTML
        )
        
        logger.info(f"Заявка пользователя {user_id} отклонена администратором {admin.id}")
        await callback.answer("❌ Заявка отклонена. Пользователь уведомлён.", show_alert=True)
        
    except Exception as e:
        logger.error(f"Ошибка при отклонении заявки: {e}")
        await callback.answer(f"❌ Ошибка: не удалось уведомить пользователя", show_alert=True)

# ═══════════════════════════════════════════════════════════════
# 🚫 ОБРАБОТЧИК НЕИЗВЕСТНЫХ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════

@dp.message()
async def handle_unknown_message(message: types.Message, state: FSMContext):
    """Обработчик неизвестных сообщений"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "🤔 Не понимаю эту команду.\n\n"
            "Используй /start чтобы начать работу с ботом\n"
            "или /help для получения справки."
        )

# ═══════════════════════════════════════════════════════════════
# 🚀 ЗАПУСК БОТА
# ═══════════════════════════════════════════════════════════════

async def on_startup():
    """Действия при запуске бота"""
    logger.info("=" * 50)
    logger.info("🤖 Бот B.L.A.C.K.A.N.G.E.L запускается...")
    logger.info("=" * 50)
    
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот успешно авторизован: @{bot_info.username}")
    except Exception as e:
        logger.error(f"❌ Ошибка авторизации: {e}")
        return
    
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🟢 <b>Бот B.L.A.C.K.A.N.G.E.L запущен и готов к работе!</b>\n\n"
                 f"📅 Время запуска: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
            parse_mode=ParseMode.HTML
        )
        logger.info(f"✅ Доступ к чату администраторов подтверждён")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось отправить сообщение в чат админов: {e}")

async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("🔴 Бот остановлен")

async def main():
    """Главная функция запуска"""
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
