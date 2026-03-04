import asyncio
import logging
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
# 💬 ТЕКСТЫ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════

WELCOME_MESSAGE = """
🖤✨ *Вас приветствует семья B.L.A.C.K.A.N.G.E.L* ✨🖤

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 *Добро пожаловать, путник!*

Мы рады, что ты заинтересовался нашей семьёй!

🔥 *B.L.A.C.K.A.N.G.E.L* — это не просто клан или гильдия. Это настоящая семья, где каждый готов поддержать друг друга в любой ситуации!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ *Что мы предлагаем:*

🤝 Дружный и сплочённый коллектив
📚 Помощь и обучение новичков  
🎮 Совместные активности и ивенты
💬 Общение и поддержка 24/7
🏆 Совместные достижения целей

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📜 *Наши принципы:*
• Уважение к каждому члену семьи
• Взаимопомощь и поддержка
• Активность и участие в жизни семьи
• Честность и открытость

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 *Хочешь стать частью нашей семьи?*
Нажми кнопку ниже и заполни небольшую анкету!

🖤 *С уважением, семья B.L.A.C.K.A.N.G.E.L* 🖤
"""

APPLICATION_START_MESSAGE = """
📝 *Отлично! Давай заполним анкету для вступления в семью!*

ℹ️ Ты можешь отменить заполнение в любой момент командой /cancel

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        parse_mode=ParseMode.MARKDOWN,
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
        "❌ *Заполнение анкеты отменено.*\n\n"
        "Чтобы начать заново, нажмите /start",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
🆘 *Помощь по боту*

*Доступные команды:*
/start - Начать работу с ботом
/cancel - Отменить заполнение анкеты
/help - Показать это сообщение

*Как подать заявку:*
1. Нажмите /start
2. Нажмите кнопку "Подать заявку"
3. Ответьте на все вопросы
4. Подтвердите отправку

По всем вопросам обращайтесь к администрации семьи.

🖤 *B.L.A.C.K.A.N.G.E.L*
"""
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)

# ═══════════════════════════════════════════════════════════════
# 🔘 ОБРАБОТЧИКИ CALLBACK-КНОПОК
# ═══════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await callback.message.edit_text(
        WELCOME_MESSAGE,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_start_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "about")
async def show_about(callback: types.CallbackQuery):
    """Информация о семье"""
    about_text = """
🖤 *О семье B.L.A.C.K.A.N.G.E.L* 🖤

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 *Дата основания:* 2024 год

👥 *Количество участников:* 50+

🎯 *Наши цели:*
• Создание дружного комьюнити
• Помощь друг другу в игре
• Совместное развитие
• Весёлое времяпрепровождение

🏆 *Наши достижения:*
• Топ семья сервера
• Множество побед в ивентах
• Сплочённый коллектив

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖤 *B.L.A.C.K.A.N.G.E.L — Семья превыше всего!*
"""
    await callback.message.edit_text(
        about_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "contact")
async def show_contact(callback: types.CallbackQuery):
    """Контакты"""
    contact_text = """
📞 *Связаться с нами*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Если у тебя есть вопросы, можешь связаться с администрацией:

👑 *Глава семьи:* @username
🛡️ *Заместитель:* @username

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Или просто подай заявку, и мы сами с тобой свяжемся!

🖤 *B.L.A.C.K.A.N.G.E.L*
"""
    await callback.message.edit_text(
        contact_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "apply")
async def start_application(callback: types.CallbackQuery, state: FSMContext):
    """Начало заполнения анкеты"""
    await state.clear()
    
    await callback.message.edit_text(
        APPLICATION_START_MESSAGE + 
        "❓ *Вопрос 1 из 6:*\n\n"
        "🎮 Напиши свой *ник в игре*:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    await state.set_state(ApplicationForm.waiting_for_nickname)
    await callback.answer()

@dp.callback_query(F.data == "cancel_application")
async def cancel_application(callback: types.CallbackQuery, state: FSMContext):
    """Отмена заявки"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ *Заявка отменена.*\n\n"
        "Если передумаешь — возвращайся!\n"
        "Нажми /start чтобы начать заново.\n\n"
        "🖤 *B.L.A.C.K.A.N.G.E.L*",
        parse_mode=ParseMode.MARKDOWN
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
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if len(nickname) > 50:
        await message.answer(
            "⚠️ Ник слишком длинный. Введи корректный ник:",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await state.update_data(nickname=nickname)
    
    await message.answer(
        "✅ Отлично!\n\n"
        "❓ *Вопрос 2 из 6:*\n\n"
        "👤 Как тебя *зовут*? (твоё имя)",
        parse_mode=ParseMode.MARKDOWN
    )
    
    await state.set_state(ApplicationForm.waiting_for_name)

@dp.message(ApplicationForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Получаем имя"""
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer(
            "⚠️ Имя слишком короткое. Введи корректное имя:",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if len(name) > 50:
        await message.answer(
            "⚠️ Имя слишком длинное. Введи корректное имя:",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await state.update_data(name=name)
    
    await message.answer(
        f"✅ Приятно познакомиться, *{name}*!\n\n"
        "❓ *Вопрос 3 из 6:*\n\n"
        "📅 *Сколько тебе лет?*",
        parse_mode=ParseMode.MARKDOWN
    )
    
    await state.set_state(ApplicationForm.waiting_for_age)

@dp.message(ApplicationForm.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    """Получаем возраст"""
    age_text = message.text.strip()
    
    # Проверяем, что это число
    if not age_text.isdigit():
        await message.answer(
            "⚠️ Пожалуйста, введи возраст *числом*:",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    age = int(age_text)
    
    if age < 10 or age > 100:
        await message.answer(
            "⚠️ Пожалуйста, введи *реальный* возраст:",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await state.update_data(age=age)
    
    await message.answer(
        "✅ Записал!\n\n"
        "❓ *Вопрос 4 из 6:*\n\n"
        "⚔️ Какой у тебя *уровень в игре*?",
        parse_mode=ParseMode.MARKDOWN
    )
    
    await state.set_state(ApplicationForm.waiting_for_level)

@dp.message(ApplicationForm.waiting_for_level)
async def process_level(message: types.Message, state: FSMContext):
    """Получаем уровень"""
    level = message.text.strip()
    
    if len(level) > 30:
        await message.answer(
            "⚠️ Слишком длинный ответ. Просто напиши свой уровень:",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await state.update_data(level=level)
    
    await message.answer(
        "✅ Хороший уровень!\n\n"
        "❓ *Вопрос 5 из 6:*\n\n"
        "🏙️ *С какого ты города?*",
        parse_mode=ParseMode.MARKDOWN
    )
    
    await state.set_state(ApplicationForm.waiting_for_city)

@dp.message(ApplicationForm.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    """Получаем город"""
    city = message.text.strip()
    
    if len(city) < 2:
        await message.answer(
            "⚠️ Название города слишком короткое. Введи корректно:",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if len(city) > 50:
        await message.answer(
            "⚠️ Название города слишком длинное. Введи корректно:",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await state.update_data(city=city)
    
    await message.answer(
        "✅ Отлично!\n\n"
        "❓ *Вопрос 6 из 6 (последний):*\n\n"
        "👨‍👩‍👧‍👦 *Какое у тебя понимание семьи?*\n\n"
        "_Напиши, что для тебя значит быть частью игровой семьи, "
        "чего ты ожидаешь от семьи и что готов дать взамен:_",
        parse_mode=ParseMode.MARKDOWN
    )
    
    await state.set_state(ApplicationForm.waiting_for_family_understanding)

@dp.message(ApplicationForm.waiting_for_family_understanding)
async def process_family_understanding(message: types.Message, state: FSMContext):
    """Получаем понимание семьи"""
    understanding = message.text.strip()
    
    if len(understanding) < 10:
        await message.answer(
            "⚠️ Пожалуйста, напиши более развёрнутый ответ (минимум 10 символов):",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if len(understanding) > 1000:
        await message.answer(
            "⚠️ Ответ слишком длинный. Пожалуйста, сократи его:",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await state.update_data(family_understanding=understanding)
    
    # Получаем все данные для предпросмотра
    data = await state.get_data()
    
    preview_text = f"""
✅ *Отлично! Анкета заполнена!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 *Проверь свои данные:*

🎮 *Ник в игре:* {data['nickname']}
👤 *Имя:* {data['name']}
📅 *Возраст:* {data['age']} лет
⚔️ *Уровень:* {data['level']}
🏙️ *Город:* {data['city']}

💭 *Понимание семьи:*
_{data['family_understanding']}_

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Всё верно? Отправляем заявку?
"""
    
    await message.answer(
        preview_text,
        parse_mode=ParseMode.MARKDOWN,
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
    
    # Формируем текст заявки для администраторов
    application_text = f"""
🆕 *НОВАЯ ЗАЯВКА В СЕМЬЮ B.L.A.C.K.A.N.G.E.L*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 *Информация о кандидате:*

🎮 *Ник в игре:* {data['nickname']}
📝 *Имя:* {data['name']}
📅 *Возраст:* {data['age']} лет
⚔️ *Уровень:* {data['level']}
🏙️ *Город:* {data['city']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💭 *Понимание семьи:*
_{data['family_understanding']}_

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 *Telegram:* {username}
🆔 *User ID:* `{user.id}`
📆 *Дата заявки:* {datetime.now().strftime("%d.%m.%Y %H:%M")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Отправляем заявку в чат администраторов
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=application_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_admin_keyboard(user.id)
        )
        
        logger.info(f"Заявка от пользователя {user.id} ({user.username}) успешно отправлена")
        
        # Подтверждение пользователю
        success_text = f"""
🎉 *Спасибо, {data['name']}! Твоя заявка успешно отправлена!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 *Твоя анкета:*
• Ник: {data['nickname']}
• Имя: {data['name']}
• Возраст: {data['age']} лет
• Уровень: {data['level']}
• Город: {data['city']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ *Что дальше?*
Администрация рассмотрит твою заявку и свяжется с тобой в ближайшее время.

💡 Обычно рассмотрение занимает от нескольких часов до 1-2 дней.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖤 *С уважением, семья B.L.A.C.K.A.N.G.E.L* 🖤
Ожидай ответа! Удачи! 🍀
"""
        
        await callback.message.edit_text(
            success_text,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки заявки: {e}")
        
        await callback.message.edit_text(
            "❌ *Произошла ошибка при отправке заявки.*\n\n"
            "Пожалуйста, попробуй позже или свяжись с администратором напрямую.\n\n"
            "Нажми /start чтобы попробовать снова.",
            parse_mode=ParseMode.MARKDOWN
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
🎉 *ПОЗДРАВЛЯЕМ!* 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Твоя заявка в семью *B.L.A.C.K.A.N.G.E.L* была *ОДОБРЕНА*!

🖤 *Добро пожаловать в семью!* 🖤

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 *Что дальше:*
Скоро с тобой свяжется администрация для дальнейших инструкций по вступлению.

Рады видеть тебя в наших рядах! 💪

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖤 *B.L.A.C.K.A.N.G.E.L — Семья превыше всего!* 🖤
""",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Обновляем сообщение с заявкой
        new_text = callback.message.text + f"\n\n✅ *ЗАЯВКА ПРИНЯТА*\n👤 Принял: @{admin.username or admin.first_name}"
        await callback.message.edit_text(
            new_text,
            parse_mode=ParseMode.MARKDOWN
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
😔 *К сожалению...*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Твоя заявка в семью *B.L.A.C.K.A.N.G.E.L* была отклонена.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *Возможные причины:*
• Не соответствие требованиям
• Недостаточно информации в анкете
• Другие причины

📝 Ты можешь попробовать подать заявку позже, более подробно заполнив анкету.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Удачи тебе! 🍀

🖤 *B.L.A.C.K.A.N.G.E.L*
""",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Обновляем сообщение с заявкой
        new_text = callback.message.text + f"\n\n❌ *ЗАЯВКА ОТКЛОНЕНА*\n👤 Отклонил: @{admin.username or admin.first_name}"
        await callback.message.edit_text(
            new_text,
            parse_mode=ParseMode.MARKDOWN
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
    
    # Проверяем токен
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот успешно авторизован: @{bot_info.username}")
    except Exception as e:
        logger.error(f"❌ Ошибка авторизации: {e}")
        return
    
    # Проверяем доступ к чату администраторов
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text="🟢 *Бот B.L.A.C.K.A.N.G.E.L запущен и готов к работе!*\n\n"
                 f"📅 Время запуска: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"✅ Доступ к чату администраторов подтверждён")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось отправить сообщение в чат админов: {e}")
        logger.warning("Проверьте ADMIN_CHAT_ID и убедитесь, что бот добавлен в чат")

async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("🔴 Бот остановлен")
    
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text="🔴 *Бот B.L.A.C.K.A.N.G.E.L остановлен*",
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        pass

async def main():
    """Главная функция запуска"""
    # Регистрируем хуки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запускаем бота
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
