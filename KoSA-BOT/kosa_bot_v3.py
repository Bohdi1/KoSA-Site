# Для роботи цього коду потрібна бібліотека aiogram.
# Якщо у вас її немає, відкрийте термінал (командний рядок) та виконайте команду:
# pip install aiogram

import asyncio
import logging
import sys

try:
    from aiogram import Bot, Dispatcher, F, Router
    from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
    from aiogram.enums import ParseMode
    from aiogram.filters import CommandStart, Command
    from aiogram.client.default import DefaultBotProperties
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup
except ModuleNotFoundError:
    print("ПОМИЛКА: Необхідну бібліотеку 'aiogram' не знайдено.")
    print("Будь ласка, встановіть її, відкривши термінал (командний рядок) та виконавши команду:")
    print("pip install aiogram")
    print("Після успішного встановлення, будь ласка, спробуйте запустити скрипт знову.")
    sys.exit()

API_TOKEN = '7589770061:AAGRFTtTSi49bipuejyaVB5hPUWLYEJHwGA'

logging.basicConfig(level=logging.INFO)

# Створюємо бота і диспетчер
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher() # Головний диспетчер

# Роутер для діагностики
diagnostic_router = Router()

# Стани для FSM діагностики
class DiagnosticStates(StatesGroup):
    waiting_for_device_type = State() # Крок 1: Комп/Моб/Інше
    waiting_for_problem_category_pc = State() # Крок 2 для ПК
    waiting_for_screen_symptom_pc = State() # Крок 3 для екрану ПК
    waiting_for_problem_category_mobile = State() # Крок 2 для Мобільних
    waiting_for_mobile_screen_symptom = State() # ЗМІНЕНО: Крок 3 для екрану/сенсора Мобільних
    # TODO: Додати стани для інших симптомів мобільних пристроїв, якщо потрібно

    waiting_for_other_device_main_category = State() # Крок 2 для "Інша техніка" - вибір підкатегорії
    waiting_for_problem_category_office = State()    # Крок 3 для Офісної
    waiting_for_problem_category_appliance = State() # Крок 3 для Побутової
    waiting_for_problem_category_av = State()        # Крок 3 для Аудіо/Відео
    waiting_for_problem_category_etransport = State()# Крок 3 для Електротранспорту
    # TODO: Додати стани для симптомів цих категорій, якщо потрібно


# Клавіатура - додаємо кнопку "Інтерактивна діагностика"
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Адреса сервісу"), KeyboardButton(text="Контакти")],
    [KeyboardButton(text="Діагностика"), KeyboardButton(text="Що ремонтуємо?")],
    [KeyboardButton(text="🤖 Інтерактивна діагностика")]
], resize_keyboard=True)

# Текст для відповіді "Що ремонтуємо?" - ОНОВЛЕНИЙ СКОРОЧЕНИЙ СПИСОК
REPAIR_SERVICES_TEXT = (
    "<b>«КоСА-Сервіс» – ваш надійний партнер у світі технологій!</b>\n\n"
    "Ми професійно здійснюємо ремонт широкого спектру техніки. Звертайтеся до нас, якщо у вас виникли проблеми з:\n\n"
    "<b>Комп'ютерна техніка та офісне обладнання:</b>\n"
    "• Ноутбуки (всіх марок та моделей)\n• Системні блоки (ПК, комп'ютери)\n• Моноблоки\n• Планшети\n• Монітори (LCD, LED)\n• Принтери (лазерні)\n• Копіювальні пристрої (БФП)\n• Сканери\n• Джерела безперебійного живлення (ДБЖ/UPS)\n• Проектори\n• Ламінатори\n• Плотери\n• Шредери (Знищувачі паперу)\n\n"
    "<b>Мобільні пристрої:</b>\n"
    "• Мобільні телефони (смартфони, кнопкові)\n• Електронні книги\n• GPS-навігатори\n\n"
    "<b>Побутова техніка:</b>\n"
    "• Мультиварки\n• Мікрохвильові печі (НВЧ-печі)\n• Кавомашини та кавоварки (ріжкові, крапельні, автоматичні)\n• Електрочайники\n• Праски\n• Фени та стайлери для волосся\n• Пилососи (звичайні, миючі, роботи-пилососи)\n• Блендери та міксери\n• М'ясорубки\n• Тостери\n• Обігрівачі (масляні, конвекторні, інфрачервоні)\n• Зволожувачі та очищувачі повітря\n\n"
    "<b>Аудіо/Відео техніка та Розваги:</b>\n"
    "• Телевізори (LCD, LED, QLED, OLED, Smart TV)\n• Домашні кінотеатри та саундбари\n• Музичні центри та аудіосистеми\n• Портативні колонки (Bluetooth-колонки)\n• Навушники (дротові та бездротові)\n• Ігрові консолі (PlayStation, Xbox)\n\n"
    "<b>Електротранспорт (дрібний):</b>\n"
    "• Електросамокати\n• Електровелосипеди\n• Гіроборди та гіроскутери\n\n"
    "Також у нашому асортименті ви знайдете все необхідне для комфортного користування вашою технікою: зарядні пристрої, кабелі, акумулятори, клавіатури, миші, килимки, навушники, колонки, адаптери, перехідники, картриджі для принтерів, тонери, чохли, захисне скло та багато інших аксесуарів.\n\n"
    "<i>Якщо ви не знайшли свою техніку у списку – не біда! Запитайте у нас, можливо, ми зможемо допомогти!</i>\n"
    "<i>Звертайтеся до нас для консультації! Ми не просто ремонтуємо техніку, а й підвищуємо її продуктивність!</i> 😉"
)

# Словник ключових слів і відповідей (тексти адрес та контактів винесені для перевикористання)
ADRESY_TEXT = (
    "<b>Наші сервісні центри KoSA:</b>\n\n"
    "<b>м. Буча:</b>\n"
    "📍 Вул. Руденко, 2 (Вхід з бульвару Б. Хмельницького)\n"
    "🕒 Графік: Пн–Пт: 09:00–18:00, Сб: 10:00–16:00\n\n"
    "<b>м. Ірпінь:</b>\n"
    "📍 Вул. Соборна, 103 (За магазином \"Рошен\" ліворуч)\n"
    "🕒 Графік: Пн–Пт: 09:00–18:00\n\n"
    "<b>смт. Гостомель:</b>\n"
    "📍 Вул. Свято-Покровська, 108-Б (На ринку)\n"
    "🕒 Графік: Вт–Пт: 09:00–18:00, Сб: 10:00–16:00\n\n"
    "<i>Обирай найближчий та принось свою техніку!</i> 😉"
)
KONTAKTY_TEXT = (
    "<b>Наші контакти:</b>\n"
    "📞 <code>+380443338648</code> (Багатоканальний)\n"
    "📞 <code>+380635342228</code> (LifeCell)\n"
    "📞 <code>+380961090110</code> (Kyivstar)\n"
    "📞 <code>+380951053838</code> (Vodafone/MTS)\n\n"
    "<i>Дзвони, якщо є питання!</i>"
)
GRAFIK_ROBOTY_TEXT = (
    "<b>Графік роботи сервісних центрів KoSA:</b>\n\n"
    "<b>м. Буча</b> (Вул. Руденко, 2):\n"
    "🕒 Пн–Пт: 09:00–18:00\n🕒 Сб: 10:00–16:00\n\n"
    "<b>м. Ірпінь</b> (Вул. Соборна, 103):\n"
    "🕒 Пн–Пт: 09:00–18:00\n\n"
    "<b>смт. Гостомель</b> (Вул. Свято-Покровська, 108-Б):\n"
    "🕒 Вт–Пт: 09:00–18:00\n🕒 Сб: 10:00–16:00\n\n"
    "<i>Чекаємо на тебе!</i>"
)
DIAGNOSTYKA_TEXT = (
    "🔍 <b>Діагностика техніки в KoSA Service – це перший крок до порятунку твого гаджета!</b>\n\n"
    "<b>Що ми робимо під час діагностики:</b>\n"
    "👀 Оглядаємо пристрій на видимі пошкодження.\n⚙️ Тестуємо основні компоненти та функції.\n💻 Перевіряємо програмне забезпечення (якщо потрібно).\n🎯 Точно визначаємо причину несправності.\n\n"
    "<b>Скільки часу це займає?</b>\n"
    "Зазвичай, діагностика триває від 1 до 5 робочих днів, залежно від складності проблеми. Іноді, для \"плаваючих\" несправностей, може знадобитися більше часу.\n"
    "Після чого погоджуємо вартість ремонту.\n\n"
    "<b>Щодо оплати:</b>\n"
    "✅ <b>Діагностика безкоштовна</b>, якщо ти залишаєш техніку на подальший ремонт у нас.\n"
    "⚠️ У випадку відмови від подальшого ремонту після проведення діагностики, вартість послуги діагностики складає <b>450 грн</b>.\n\n"
    "<b>Що брати з собою?</b>\n"
    "Бажано принести сам пристрій та його зарядний пристрій (особливо для ноутбуків та електротранспорту). Якщо проблема специфічна (наприклад, не працює з конкретним аксесуаром), візьми і його.\n\n"
    "<i>Не гадай, що зламалося – довірся професіоналам KoSA Service! Ми знайдемо корінь проблеми.</i> 😉"
)

keyword_responses = {
    "ремонт пк": "🔧 Займаємось ремонтом ПК. Щось тріщить, не вмикається, перегрівається — неси, подивимось.",
    "комп'ютер": "🧠 Компи — наше хобі. Що з ним сталося? Можемо апгрейдити, почистити, або воскресити з мертвих.",
    "ноут": "💻 Ремонтуємо ноутбуки: тріщини, залиття, глюки Windows — усе фіксимо. Напиши, що саме трапилось.",
    "екран": "🖥️ Якщо екран темний, тріснув, або видно тільки спогади про минуле — швидше за все, під заміну.",
    "телефон": "📱 Телефони лагодимо. Екран, батарея, зарядка — пиши, розберемося.",
    "зарядка": "🔌 Проблема з зарядкою? Це може бути роз'єм, шнур або сама плата. Принось — підкинем на діагностику.",
    "не вмикається": "😵 Не вмикається? Є шанс, що не все втрачено. Принеси — розберемо.",
    "адреса": ADRESY_TEXT,
    "адреса сервісу": ADRESY_TEXT,
    "адреси": ADRESY_TEXT,
    "де знайти": ADRESY_TEXT,
    "графік роботи": GRAFIK_ROBOTY_TEXT,
    "години роботи": GRAFIK_ROBOTY_TEXT,
    "контакти": KONTAKTY_TEXT,
    "гарантія": "🛡️ Даємо гарантію на все, що ремонтуємо. Але якщо розбирали вдома — то тільки хрестик на удачу.",
    "діагностика": DIAGNOSTYKA_TEXT,
    "що ремонтуємо?": REPAIR_SERVICES_TEXT,
    "що ремонтуєте": REPAIR_SERVICES_TEXT,
    "види техніки": REPAIR_SERVICES_TEXT,
}

# --- Початок блоку інтерактивної діагностики ---

# Клавіатури для діагностики
def get_device_type_kb(): # Крок 1
    buttons = [
        [InlineKeyboardButton(text="💻 Комп'ютер / Ноутбук", callback_data="diag_device_pc")],
        [InlineKeyboardButton(text="📱 Смартфон / Планшет", callback_data="diag_device_mobile")],
        [InlineKeyboardButton(text="🛠️ Інша техніка", callback_data="diag_device_other_category_selection")], # Веде до вибору підкатегорії
        [InlineKeyboardButton(text="⬅️ Скасувати діагностику", callback_data="diag_cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Клавіатури для Комп'ютер / Ноутбук ---
def get_pc_problem_category_kb(): # Крок 2 для ПК
    buttons = [
        [InlineKeyboardButton(text="⚡ Проблеми з включенням", callback_data="diag_pc_cat_power")],
        [InlineKeyboardButton(text="🐢 Низька продуктивність", callback_data="diag_pc_cat_performance")],
        [InlineKeyboardButton(text="🖥️ Проблеми з екраном", callback_data="diag_pc_cat_screen")],
        [InlineKeyboardButton(text="🔊 Проблеми зі звуком", callback_data="diag_pc_cat_sound")],
        [InlineKeyboardButton(text="🔥 Перегрів", callback_data="diag_pc_cat_overheat")],
        [InlineKeyboardButton(text="🌐 Проблеми з інтернетом", callback_data="diag_pc_cat_internet")],
        [InlineKeyboardButton(text="⌨️ Проблеми з клавіатурою/тачпадом", callback_data="diag_pc_cat_input")],
        [InlineKeyboardButton(text="💾 Проблеми з диском/пам'яттю", callback_data="diag_pc_cat_storage")],
        [InlineKeyboardButton(text="⚙️ Інша проблема з ПК", callback_data="diag_pc_cat_other")],
        [InlineKeyboardButton(text="⬅️ Назад (вибір пристрою)", callback_data="diag_back_to_device_choice")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_pc_screen_symptoms_kb(): # Крок 3 для екрану ПК
    buttons = [
        [InlineKeyboardButton(text="Екран не вмикається", callback_data="diag_pc_screen_no_power")],
        [InlineKeyboardButton(text="Екран мерехтить", callback_data="diag_pc_screen_flicker")],
        [InlineKeyboardButton(text="На екрані смуги/артефакти", callback_data="diag_pc_screen_artifacts")], # Уточнено
        [InlineKeyboardButton(text="Екран фізично пошкоджений", callback_data="diag_pc_screen_damaged")],
        [InlineKeyboardButton(text="Дуже тьмяне зображення", callback_data="diag_pc_screen_dim")],
        [InlineKeyboardButton(text="⬅️ Назад (вибір проблеми ПК)", callback_data="diag_back_to_pc_category")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Клавіатури для Смартфон / Планшет ---
def get_mobile_problem_category_kb(): # Крок 2 для Мобільних
    buttons = [
        [InlineKeyboardButton(text="🔋 Не вмикається / Не заряджається", callback_data="diag_mob_cat_power")],
        [InlineKeyboardButton(text="📱 Проблеми з екраном/сенсором", callback_data="diag_mob_cat_screen")],
        [InlineKeyboardButton(text="🔊 Проблеми зі звуком (динамік/мікрофон)", callback_data="diag_mob_cat_sound")],
        [InlineKeyboardButton(text="📸 Проблеми з камерою", callback_data="diag_mob_cat_camera")],
        [InlineKeyboardButton(text="⏳ Швидко розряджається / Проблеми з батареєю", callback_data="diag_mob_cat_battery")],
        [InlineKeyboardButton(text="⚙️ Проблеми з ПЗ / Зависає / Перезавантажується", callback_data="diag_mob_cat_software")],
        [InlineKeyboardButton(text="💧 Потрапила вода / Фізичне пошкодження", callback_data="diag_mob_cat_damage")],
        [InlineKeyboardButton(text="🌐 Проблеми з мережею/Wi-Fi/Bluetooth", callback_data="diag_mob_cat_connectivity")],
        [InlineKeyboardButton(text="🔧 Інша проблема з мобільним", callback_data="diag_mob_cat_other")],
        [InlineKeyboardButton(text="⬅️ Назад (вибір пристрою)", callback_data="diag_back_to_device_choice")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# НОВИЙ КОД: Клавіатура для симптомів екрану мобільного
def get_mobile_screen_symptoms_kb(): # Крок 3 для екрану/сенсора Мобільних
    buttons = [
        [InlineKeyboardButton(text="Екран не реагує на дотики", callback_data="diag_mob_screen_no_touch")],
        [InlineKeyboardButton(text="Смуги / плями / биті пікселі", callback_data="diag_mob_screen_artifacts")],
        [InlineKeyboardButton(text="Екран тріснутий / пошкоджений", callback_data="diag_mob_screen_damaged")],
        [InlineKeyboardButton(text="Чорний екран (не світиться)", callback_data="diag_mob_screen_no_light")],
        [InlineKeyboardButton(text="Мерехтить зображення", callback_data="diag_mob_screen_flicker")],
        [InlineKeyboardButton(text="⬅️ Назад (вибір проблеми мобільного)", callback_data="diag_back_to_mobile_category")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
# КІНЕЦЬ НОВОГО КОДУ

# --- Клавіатури для "Інша техніка" ---
def get_other_device_main_category_kb(): # Крок 2 для "Інша техніка"
    buttons = [
        [InlineKeyboardButton(text="📠 Офісна техніка", callback_data="diag_other_maincat_office")],
        [InlineKeyboardButton(text="🍳 Побутова техніка", callback_data="diag_other_maincat_appliance")],
        [InlineKeyboardButton(text="📺 Аудіо/Відео та Розваги", callback_data="diag_other_maincat_av")],
        [InlineKeyboardButton(text="🛴 Електротранспорт", callback_data="diag_other_maincat_etransport")],
        [InlineKeyboardButton(text="⬅️ Назад (вибір пристрою)", callback_data="diag_back_to_device_choice")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_generic_problem_categories_kb(device_category_prefix: str): # Крок 3 для підкатегорій "Іншої техніки"
    buttons = [
        [InlineKeyboardButton(text="⚡ Не вмикається", callback_data=f"diag_{device_category_prefix}_problem_no_power")],
        [InlineKeyboardButton(text="⚠️ Не працює належним чином", callback_data=f"diag_{device_category_prefix}_problem_malfunction")],
        [InlineKeyboardButton(text="🔊 Дивні звуки / запахи", callback_data=f"diag_{device_category_prefix}_problem_noise_smell")],
        [InlineKeyboardButton(text="🛠️ Механічне пошкодження", callback_data=f"diag_{device_category_prefix}_problem_damage")],
        [InlineKeyboardButton(text="❓ Інша проблема", callback_data=f"diag_{device_category_prefix}_problem_other")],
        [InlineKeyboardButton(text="⬅️ Назад (вибір категорії ін. техніки)", callback_data="diag_back_to_other_main_category_selection")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_final_diagnostic_kb():
    buttons = [
        [InlineKeyboardButton(text="🔄 Почати спочатку", callback_data="diag_restart")],
        [InlineKeyboardButton(text="📞 Зв'язатися з нами", callback_data="diag_show_contacts")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Обробник кнопки "Інтерактивна діагностика"
@dp.message(F.text == "🤖 Інтерактивна діагностика")
async def start_interactive_diagnostic(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Діагностика комп'ютерних проблем</b>\n"
        "Дайте відповіді на кілька запитань, і ми допоможемо визначити можливу проблему з вашим пристроєм.\n\n"
        "<b>Крок 1: Виберіть тип пристрою</b>",
        reply_markup=get_device_type_kb()
    )
    await state.set_state(DiagnosticStates.waiting_for_device_type)

# Обробник скасування діагностики
@diagnostic_router.callback_query(F.data == "diag_cancel")
async def cancel_diagnostic_handler(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer("Діагностику не розпочато.", show_alert=True)
        try:
            await callback.message.delete()
        except Exception:
            pass
        return
    await state.clear()
    await callback.message.edit_text("Діагностику скасовано. Чим ще можу допомогти?", reply_markup=None)
    await callback.answer()

# Обробник вибору типу пристрою (Крок 1)
@diagnostic_router.callback_query(DiagnosticStates.waiting_for_device_type, F.data.startswith("diag_device_"))
async def device_type_chosen(callback: CallbackQuery, state: FSMContext):
    device_choice = callback.data.split("diag_device_")[-1]
    await state.update_data(device_type_choice=device_choice)

    if device_choice == "pc":
        await callback.message.edit_text(
            "<b>Крок 2: Яка проблема вас турбує (Комп'ютер / Ноутбук)?</b>",
            reply_markup=get_pc_problem_category_kb()
        )
        await state.set_state(DiagnosticStates.waiting_for_problem_category_pc)
    elif device_choice == "mobile":
        await callback.message.edit_text(
            "<b>Крок 2: Яка проблема вас турбує (Смартфон / Планшет)?</b>",
            reply_markup=get_mobile_problem_category_kb()
        )
        await state.set_state(DiagnosticStates.waiting_for_problem_category_mobile)
    elif device_choice == "other_category_selection":
        await callback.message.edit_text(
            "<b>Крок 2: Виберіть категорію вашої техніки</b>",
            reply_markup=get_other_device_main_category_kb()
        )
        await state.set_state(DiagnosticStates.waiting_for_other_device_main_category)
    await callback.answer()

# Функція для показу фінального результату (узагальненого)
async def show_diagnostic_result(message_or_callback: Message | CallbackQuery, state: FSMContext, problem_description: str = "Для точного визначення проблеми потрібна професійна діагностика в сервісному центрі."):
    user_data = await state.get_data()
    device_type_choice = user_data.get("device_type_choice", "невідомий пристрій")

    text = (
        f"<b>Результат діагностики (попередній) для: {device_type_choice.replace('_', ' ').capitalize()}</b>\n\n"
        f"<b>Можлива проблема:</b>\n{problem_description}\n\n"
        "<b>Рекомендації:</b>\nРекомендуємо звернутися до сервісного центру KoSA для детальної діагностики та ремонту вашого пристрою.\n\n" +
        ADRESY_TEXT
    )
    reply_markup = get_final_diagnostic_kb()

    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(text, reply_markup=reply_markup)
    elif isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(text, reply_markup=reply_markup)

    await state.clear()


# --- Обробники для Комп'ютер / Ноутбук ---
@diagnostic_router.callback_query(DiagnosticStates.waiting_for_problem_category_pc, F.data.startswith("diag_pc_cat_"))
async def pc_problem_category_chosen(callback: CallbackQuery, state: FSMContext):
    problem_category = callback.data.split("diag_pc_cat_")[-1]
    await state.update_data(pc_problem_category=problem_category)

    if problem_category == "screen":
        await callback.message.edit_text(
            "<b>Крок 3: Уточніть симптоми (Проблеми з екраном ПК)</b>",
            reply_markup=get_pc_screen_symptoms_kb()
        )
        await state.set_state(DiagnosticStates.waiting_for_screen_symptom_pc)
    else:
        problem_description_map = {
            "power": "Проблеми з живленням або компонентами, що відповідають за старт системи.",
            "performance": "Проблеми з програмним забезпеченням, жорстким диском, оперативною пам'яттю або перегрівом.",
            "sound": "Проблеми з аудіо драйверами, динаміками або звуковою картою.",
            "overheat": "Проблеми з системою охолодження, термопастою або надмірним навантаженням.",
            "internet": "Проблеми з мережевою картою, драйверами, налаштуваннями або Wi-Fi модулем.",
            "input": "Проблеми з клавіатурою, тачпадом, їх підключенням або драйверами.",
            "storage": "Проблеми з жорстким диском (HDD/SSD) або оперативною пам'яттю.",
            "other": "Необхідна детальна діагностика для визначення специфічної проблеми."
        }
        description = problem_description_map.get(problem_category, "Для точного визначення проблеми потрібна професійна діагностика.")
        await show_diagnostic_result(callback, state, problem_description=description)
    await callback.answer()

@diagnostic_router.callback_query(DiagnosticStates.waiting_for_screen_symptom_pc, F.data.startswith("diag_pc_screen_"))
async def pc_screen_symptom_chosen(callback: CallbackQuery, state: FSMContext):
    screen_symptom = callback.data.split("diag_pc_screen_")[-1]
    await state.update_data(pc_screen_symptom=screen_symptom)

    symptom_description_map = {
        "no_power": "Можливі проблеми з матрицею, шлейфом, відеокартою або живленням екрану.",
        "flicker": "Можливі проблеми зі шлейфом матриці, відеокартою або драйверами.",
        "artifacts": "Часто вказує на проблеми з відеокартою або її пам'яттю, рідше - шлейфом.",
        "damaged": "Необхідна заміна матриці екрану.",
        "dim": "Можливі проблеми з підсвіткою матриці або інвертором."
    }
    description = symptom_description_map.get(screen_symptom, "Проблеми з відображенням на екрані.")
    await show_diagnostic_result(callback, state, problem_description=description)
    await callback.answer()

# --- Обробники для Смартфон / Планшет ---
# ЗМІНЕНО: Обробник вибору категорії проблеми мобільного пристрою
@diagnostic_router.callback_query(DiagnosticStates.waiting_for_problem_category_mobile, F.data.startswith("diag_mob_cat_"))
async def mobile_problem_category_chosen(callback: CallbackQuery, state: FSMContext):
    problem_category = callback.data.split("diag_mob_cat_")[-1]
    await state.update_data(mobile_problem_category=problem_category)

    if problem_category == "screen": # Якщо обрано проблеми з екраном
        await callback.message.edit_text(
            "<b>Крок 3: Уточніть симптоми (Проблеми з екраном/сенсором мобільного)</b>",
            reply_markup=get_mobile_screen_symptoms_kb() # Показуємо нову клавіатуру
        )
        await state.set_state(DiagnosticStates.waiting_for_mobile_screen_symptom) # Переходимо в новий стан
    else:
        # Для інших категорій проблем мобільних - залишаємо поточну логіку
        problem_description_map = {
            "power": "Проблеми з батареєю, роз'ємом зарядки, контролером живлення або програмним збоєм.",
            # "screen": "Проблеми з дисплеєм, тачскріном, шлейфом або програмним забезпеченням.", # Видалено, бо обробляється окремо
            "sound": "Проблеми з динаміком, мікрофоном, аудіокодеком або програмним забезпеченням.",
            "camera": "Проблеми з модулем камери, шлейфом або програмним забезпеченням.",
            "battery": "Знос батареї, проблеми з контролером заряду або програмним забезпеченням.",
            "software": "Програмні збої, віруси, необхідність оновлення або перепрошивки.",
            "damage": "Механічні пошкодження корпусу, внутрішніх компонентів або потрапляння рідини.",
            "connectivity": "Проблеми з антеною, модулями Wi-Fi/Bluetooth/GSM або програмним забезпеченням.",
            "other": "Необхідна детальна діагностика для визначення специфічної проблеми."
        }
        description = problem_description_map.get(problem_category, "Для точного визначення проблеми потрібна професійна діагностика.")
        await show_diagnostic_result(callback, state, problem_description=description)
    await callback.answer()
# КІНЕЦЬ ЗМІН

# НОВИЙ КОД: Обробник вибору симптому проблеми з екраном мобільного
@diagnostic_router.callback_query(DiagnosticStates.waiting_for_mobile_screen_symptom, F.data.startswith("diag_mob_screen_"))
async def mobile_screen_symptom_chosen(callback: CallbackQuery, state: FSMContext):
    screen_symptom = callback.data.split("diag_mob_screen_")[-1]
    await state.update_data(mobile_screen_symptom=screen_symptom)

    symptom_description_map = {
        "no_touch": "Проблема, ймовірно, пов'язана з тачскріном (сенсорною панеллю) або його контролером. Може знадобитися заміна дисплейного модуля.",
        "artifacts": "Смуги, плями або биті пікселі часто вказують на несправність самої матриці дисплея або шлейфу.",
        "damaged": "Фізичне пошкодження екрану (тріщини, сколи) зазвичай вимагає заміни дисплейного модуля.",
        "no_light": "Якщо екран залишається чорним, але телефон реагує (наприклад, є звук), проблема може бути в підсвітці дисплея, шлейфі або самому дисплеї.",
        "flicker": "Мерехтіння може бути спричинене проблемами зі шлейфом, програмним збоєм або несправністю дисплея."
    }
    description = symptom_description_map.get(screen_symptom, "Проблеми з відображенням або сенсором на мобільному пристрої.")
    await show_diagnostic_result(callback, state, problem_description=description)
    await callback.answer()
# КІНЕЦЬ НОВОГО КОДУ

# --- Обробники для "Інша техніка" ---
@diagnostic_router.callback_query(DiagnosticStates.waiting_for_other_device_main_category, F.data.startswith("diag_other_maincat_"))
async def other_main_category_chosen(callback: CallbackQuery, state: FSMContext):
    main_category = callback.data.split("diag_other_maincat_")[-1]
    await state.update_data(other_main_category=main_category)

    category_name_map = {
        "office": "Офісна техніка",
        "appliance": "Побутова техніка",
        "av": "Аудіо/Відео та Розваги",
        "etransport": "Електротранспорт"
    }
    category_name = category_name_map.get(main_category, "Обрана техніка")

    await callback.message.edit_text(
        f"<b>Крок 3: Яка проблема вас турбує ({category_name})?</b>",
        reply_markup=get_generic_problem_categories_kb(main_category)
    )
    if main_category == "office":
        await state.set_state(DiagnosticStates.waiting_for_problem_category_office)
    elif main_category == "appliance":
        await state.set_state(DiagnosticStates.waiting_for_problem_category_appliance)
    elif main_category == "av":
        await state.set_state(DiagnosticStates.waiting_for_problem_category_av)
    elif main_category == "etransport":
        await state.set_state(DiagnosticStates.waiting_for_problem_category_etransport)
    await callback.answer()

async def handle_other_subcategory_problem(callback: CallbackQuery, state: FSMContext, category_prefix: str):
    problem_type = callback.data.split(f"diag_{category_prefix}_problem_")[-1]
    await state.update_data(specific_problem_type=problem_type)

    description = f"Проблеми з роботою пристрою категорії '{category_prefix}'. Необхідна детальна діагностика."
    if problem_type == "no_power":
        description = f"Пристрій категорії '{category_prefix}' не вмикається. Можливі проблеми з живленням або внутрішніми компонентами."
    elif problem_type == "malfunction":
        description = f"Пристрій категорії '{category_prefix}' не виконує свої функції належним чином."

    await show_diagnostic_result(callback, state, problem_description=description)
    await callback.answer()

@diagnostic_router.callback_query(DiagnosticStates.waiting_for_problem_category_office, F.data.startswith("diag_office_problem_"))
async def office_problem_chosen(callback: CallbackQuery, state: FSMContext):
    await handle_other_subcategory_problem(callback, state, "office")

@diagnostic_router.callback_query(DiagnosticStates.waiting_for_problem_category_appliance, F.data.startswith("diag_appliance_problem_"))
async def appliance_problem_chosen(callback: CallbackQuery, state: FSMContext):
    await handle_other_subcategory_problem(callback, state, "appliance")

@diagnostic_router.callback_query(DiagnosticStates.waiting_for_problem_category_av, F.data.startswith("diag_av_problem_"))
async def av_problem_chosen(callback: CallbackQuery, state: FSMContext):
    await handle_other_subcategory_problem(callback, state, "av")

@diagnostic_router.callback_query(DiagnosticStates.waiting_for_problem_category_etransport, F.data.startswith("diag_etransport_problem_"))
async def etransport_problem_chosen(callback: CallbackQuery, state: FSMContext):
    await handle_other_subcategory_problem(callback, state, "etransport")


# --- Обробники кнопок "Назад" ---
@diagnostic_router.callback_query(F.data == "diag_back_to_device_choice")
async def back_to_device_choice(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Крок 1: Виберіть тип пристрою</b>",
        reply_markup=get_device_type_kb()
    )
    await state.set_state(DiagnosticStates.waiting_for_device_type)
    await callback.answer()

@diagnostic_router.callback_query(F.data == "diag_back_to_pc_category")
async def back_to_pc_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Крок 2: Яка проблема вас турбує (Комп'ютер / Ноутбук)?</b>",
        reply_markup=get_pc_problem_category_kb()
    )
    await state.set_state(DiagnosticStates.waiting_for_problem_category_pc)
    await callback.answer()

# НОВИЙ КОД: Обробник кнопки "Назад" з вибору симптому екрану мобільного
@diagnostic_router.callback_query(F.data == "diag_back_to_mobile_category")
async def back_to_mobile_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Крок 2: Яка проблема вас турбує (Смартфон / Планшет)?</b>",
        reply_markup=get_mobile_problem_category_kb() # Повертаємось до клавіатури категорій проблем моб.
    )
    await state.set_state(DiagnosticStates.waiting_for_problem_category_mobile) # Встановлюємо відповідний стан
    await callback.answer()
# КІНЕЦЬ НОВОГО КОДУ

@diagnostic_router.callback_query(F.data == "diag_back_to_other_main_category_selection")
async def back_to_other_main_category_selection(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Крок 2: Виберіть категорію вашої техніки</b>",
        reply_markup=get_other_device_main_category_kb()
    )
    await state.set_state(DiagnosticStates.waiting_for_other_device_main_category)
    await callback.answer()


# Обробник кнопки "Почати спочатку" у фінальному повідомленні
@diagnostic_router.callback_query(F.data == "diag_restart")
async def restart_diagnostic_flow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "<b>Діагностика комп'ютерних проблем</b>\n"
        "Дайте відповіді на кілька запитань, і ми допоможемо визначити можливу проблему з вашим пристроєм.\n\n"
        "<b>Крок 1: Виберіть тип пристрою</b>",
        reply_markup=get_device_type_kb()
    )
    await state.set_state(DiagnosticStates.waiting_for_device_type)
    await callback.answer()

# Обробник кнопки "Зв'язатися з нами" у фінальному повідомленні
@diagnostic_router.callback_query(F.data == "diag_show_contacts")
async def show_contacts_from_diag(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(KONTAKTY_TEXT, reply_markup=None)
    await callback.answer("Контакти надіслано.")


# --- Кінець блоку інтерактивної діагностики ---


@dp.message(CommandStart())
async def handle_start(message: Message):
    await message.answer("Пиши, що болить. Якщо знатиму — відповім. Якщо ні — передам людині.", reply_markup=main_kb)

@dp.message(Command("help"))
async def handle_help(message: Message):
    help_text = (
        "<b>Допомога по боту KoSA Service:</b>\n\n"
        "Я можу надати інформацію за наступними запитами:\n"
        "➡️ Натисніть кнопку <b>\"Адреса сервісу\"</b>, щоб дізнатися адреси та графіки роботи наших сервісних центрів.\n"
        "➡️ Натисніть кнопку <b>\"Контакти\"</b>, щоб побачити наші телефонні номери.\n"
        "➡️ Натисніть кнопку <b>\"Діагностика\"</b>, щоб дізнатися деталі про нашу послугу діагностики техніки.\n"
        "➡️ Натисніть кнопку <b>\"Що ремонтуємо?\"</b>, щоб побачити перелік техніки, яку ми ремонтуємо, та інформацію про аксесуари.\n"
        "➡️ Натисніть кнопку <b>\"🤖 Інтерактивна діагностика\"</b>, щоб спробувати визначити проблему з пристроєм крок за кроком.\n\n"
        "Також ви можете просто написати мені ключові слова, наприклад:\n"
        "• <code>ремонт пк</code>\n• <code>не вмикається</code>\n• <code>графік роботи</code>\n• <code>гарантія</code>\n"
        "і я спробую допомогти!\n\n"
        "Для початку роботи з ботом використовуйте команду /start."
    )
    await message.answer(help_text, reply_markup=main_kb)

@dp.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    current_fsm_state = await state.get_state()
    if current_fsm_state is not None:
        return

    text = message.text.lower()
    response_text = None

    if text in keyword_responses:
        response_val = keyword_responses[text]
        response_text = response_val() if callable(response_val) else response_val
    else:
        for keyword, reply_val in keyword_responses.items():
            if isinstance(keyword, str) and keyword in text and text != keyword:
                response_text = reply_val() if callable(reply_val) else reply_val
                break

    if response_text:
        await message.answer(response_text)
    else:
        await message.answer("Не зовсім вловив(ла) суть. Може, натисни кнопку або спробуй перефразувати? 😉 Або використай команду /help для довідки.")

async def main():
    dp.include_router(diagnostic_router)

    # from aiogram.types import BotCommand
    # commands = [
    #     BotCommand(command="/start", description="🚀 Запустити/перезапустити бота"),
    #     BotCommand(command="/help", description="ℹ️ Допомога по командах")
    # ]
    # await bot.set_my_commands(commands)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
