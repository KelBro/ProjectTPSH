import json
import logging
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.markdown import hbold, hitalic
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config_reader import config
import math

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())
upload_id = -1
user_id = 1
st_num = 1


# Инициализация базы данных
def init_db():
    connection = sqlite3.connect('../data_base.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS uploads (
        user_id INTEGER,
        upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        upload_date TEXT
    )
    ''')

    connection.commit()
    connection.close()


init_db()

TRANSLATIONS = json.load(open("../languages.json", encoding="utf-8"))


def get_translations(lang):
    return TRANSLATIONS[lang]


tr = get_translations("ru")


class DressStates(StatesGroup):
    waiting_for_name = State()


# пересоздание клавиатуры
def get_keyboard(tr):
    kb = [
        [types.KeyboardButton(text=tr['history']),
         types.KeyboardButton(text=tr['language'])]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )


# обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global user_id
    user_id = message.from_user.id
    global tr
    tr = get_translations("ru")
    await message.answer(
        f"{hbold(tr['greeting'])}"
        f"{tr['description']}"
        f"\n\n{hbold(tr['cta'])}",
        reply_markup=get_keyboard(tr),
        parse_mode="HTML"
    )

def generate_url(filters, m:str, p:str):
    url = m

    # Кодируем параметры фильтров для URL
    for i in filters:
        url += p + i
    return url

# вб озон ламода алик яндекс маркет
# обработчик получения фотографии
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    date = datetime.now().strftime("%d.%m.%Y")
    name = 'Тест платье ' + date
    description = "ПОКА ЧТО НИЧЕГО"
    connection = sqlite3.connect('../data_base.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO uploads (user_id, name, description, upload_date) VALUES (?, ?, ?, ?)',
                   (user_id, name, description, date))
    global upload_id
    upload_id = cursor.lastrowid
    connection.commit()
    connection.close()

    buttons = [
        [
            types.InlineKeyboardButton(text=tr['yes'], callback_data="ph_yes"),
            types.InlineKeyboardButton(text=tr['no'], callback_data="ph_no")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    filters = ["красное", "длинное", "пышное"]
    await message.answer(
        f"{tr['photo_received1']}"
        f'<a href="{generate_url(filters, "https://www.wildberries.ru/catalog/0/search.aspx?search=платье", "%20")}">{tr["link_vb"]}</a>'
        f'<a href="{generate_url(filters, "https://www.ozon.ru/search/?text=платье", "+")}">{tr["link_ozon"]}</a>'
        f'<a href="{generate_url(filters, "https://www.lamoda.ru/catalogsearch/result/?q=платье", "+")}">{tr["link_lamoda"]}</a>'
        f'<a href="{generate_url(filters, "https://m.aliexpress.com/wholesale?SearchText=платье", "+")}">{tr["link_alik"]}</a>'
        f'<a href="{generate_url(filters, "https://market.yandex.ru/search?text=платье", "+")}">{tr["link_yandex"]}</a>'
        f"{tr['photo_received2']}",
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# обработчик инлайн-кнопок подтверждения фото
@dp.callback_query(F.data.startswith("ph_"))
async def handle_photo_callback(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "yes":
        await callback.message.answer(tr['rename_prompt'])
        await state.set_state(DressStates.waiting_for_name)
    elif action == "no":
        await callback.message.edit_text(tr['rename_cancel'], reply_markup=None)
    await callback.answer()

# изменение названия платья
@dp.message(DressStates.waiting_for_name)
async def process_dress_name(message: types.Message, state: FSMContext):
    new_name = message.text
    if new_name != tr["language"] and new_name != tr["history"]:
        await message.answer(tr['rename_success'] + new_name)
        await state.clear()

        connection = sqlite3.connect('../data_base.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE uploads SET name = ? WHERE upload_id = ?', (new_name, upload_id))
        connection.commit()
        connection.close()


def get_history_keyboard():
    connection = sqlite3.connect("../data_base.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * 
        FROM uploads 
        WHERE user_id = ?
    """, (user_id,))
    lines = cursor.fetchall()
    connection.close()

    total_items = len(lines)
    items_per_page = 5
    max_page = math.ceil(total_items / items_per_page)
    start_idx = (st_num - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    current_items = lines[start_idx:end_idx]

    buttons = []
    # Добавляем кнопки для текущих элементов
    for item in current_items:
        buttons.append([types.InlineKeyboardButton(text=item[2], callback_data=f"his_{item[1]}")])

    # Добавляем заглушки для оставшихся мест
    for _ in range(items_per_page - len(current_items)):
        buttons.append([types.InlineKeyboardButton(text=tr['empty'], callback_data="his_empty")])

    # Кнопки навигации
    nav_buttons = []
    if st_num > 1:
        nav_buttons.append(types.InlineKeyboardButton(text="◀", callback_data="his_prev"))
    if st_num < max_page and total_items > 0:
        nav_buttons.append(types.InlineKeyboardButton(text="▶", callback_data="his_next"))
    if nav_buttons:
        buttons.append(nav_buttons)

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


# обработчик кнопки "История"
@dp.message(lambda message: message.text in [lang['history'] for lang in TRANSLATIONS.values()])
async def handle_history(message: types.Message):
    global st_num
    st_num = 1
    keyboard = get_history_keyboard()
    await message.answer(tr['call_history'], reply_markup=keyboard)


@dp.callback_query(F.data.startswith("his_"))
async def history_menu(callback: types.CallbackQuery):
    global st_num
    data = callback.data.split("_")
    action = data[1]

    if action == "prev":
        st_num -= 1
        keyboard = get_history_keyboard()
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()
    elif action == "next":
        st_num += 1
        keyboard = get_history_keyboard()
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()
    elif action == "empty":
        await callback.answer()
    else:
        # Показ деталей элемента
        upload_id = int(action)
        connection = sqlite3.connect("../data_base.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uploads WHERE upload_id = ?", (upload_id,))
        item = cursor.fetchone()
        connection.close()

        if item:
            await callback.message.answer(
                f"{hbold(item[2])}\n\n{item[3]}\n{item[4]}",
                parse_mode="HTML"
            )
        await callback.answer()


# обработчик кнопки "Язык"
@dp.message(lambda message: message.text in [lang['language'] for lang in TRANSLATIONS.values()])
async def handle_language(message: types.Message):
    buttons = [
        [types.InlineKeyboardButton(text=tr['options']['ru'], callback_data="lan_ru")],
        [types.InlineKeyboardButton(text=tr['options']['en'], callback_data="lan_en")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(tr['select'], reply_markup=keyboard)


# обработчик инлайн-кнопок языка
@dp.callback_query(F.data.startswith("lan_"))
async def handle_language_callback(callback: types.CallbackQuery):
    global tr
    action = callback.data.split("_")[1]
    tr = get_translations(action)
    await callback.message.delete()
    await callback.message.answer(
        tr[f'changed_{action}'],
        reply_markup=get_keyboard(tr)
    )
    await callback.answer()


# обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(tr['help'])

