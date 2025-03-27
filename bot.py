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

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())
upload_id = -1
st_num = 1

# Инициализация базы данных
def init_db():
    connection = sqlite3.connect('data_base.db')
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

TRANSLATIONS = json.load(open("languages.json", encoding="utf-8"))
def get_translations(lang):
    return TRANSLATIONS[lang]
tr = get_translations("ru")

class DressStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_photo = State()

# пересоздание клавиатуры
def get_keyboard(tr):
    kb = [
        [types.KeyboardButton(text=tr['upload'])],
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
    global tr
    tr = get_translations("ru")
    await message.answer(
        f"{hbold(tr['greeting'])}"
        f"{tr['description']}"
        f"\n\n{hbold(tr['cta'])}",
        reply_markup=get_keyboard(tr),
        parse_mode="HTML"
    )

# обработчик кнопки загрузка
@dp.message(lambda message: message.text in [lang['upload'] for lang in TRANSLATIONS.values()])
async def handle_upload(message: types.Message, state: FSMContext):
    await state.set_state(DressStates.waiting_for_photo)
    await message.answer(tr['request_photo'])

# обработчик получения фотографии
@dp.message(F.photo, DressStates.waiting_for_photo)
async def handle_photo(message: types.Message, state: FSMContext):
    date = datetime.now().strftime("%d.%m.%Y")
    name = 'Тест платье ' + date
    description = "ПОКА ЧТО НИЧЕГО"
    connection = sqlite3.connect('data_base.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO uploads (user_id, name, description, upload_date) VALUES (?, ?, ?, ?)', (message.from_user.id, name, description, date))
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
    await message.answer(
        f"{tr['photo_received']}",
        reply_markup=keyboard
    )
    await state.clear()

# вывод ошибки для фото отправленных без нажатия "Загрузка"
@dp.message(F.photo)
async def handle_incorrect_photo(message: types.Message):
    await message.answer(tr['invalid_photo_input'])

# обработчик инлайн-кнопок подтверждения фото
@dp.callback_query(F.data.startswith("ph_"))
async def handle_photo_callback(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "yes":
        await callback.message.answer(tr['rename_prompt'])
        await state.set_state(DressStates.waiting_for_name)
    elif action == "no":
        await callback.message.edit_text(tr['rename_cancel'])
    await callback.answer()

# изменение названия платья
@dp.message(DressStates.waiting_for_name)
async def process_dress_name(message: types.Message, state: FSMContext):
    new_name = message.text
    await message.answer(tr['rename_success']+new_name)
    await state.clear()

    connection = sqlite3.connect('data_base.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE uploads SET name = ? WHERE upload_id = ?', (new_name, upload_id))
    connection.commit()
    connection.close()

# обработчик кнопки "История"
@dp.message(lambda message: message.text in [lang['history'] for lang in TRANSLATIONS.values()])
async def handle_history(message: types.Message):
    connection = sqlite3.connect("data_base.db")
    cursor = connection.cursor()
    cursor.execute("""
            SELECT * 
            FROM uploads 
            WHERE user_id = ?
        """, (message.from_user.id,))
    lines = cursor.fetchall()
    x = (st_num-1)*5
    y = x + 5
    row = lines[x:y]
    buttons = [
        [types.InlineKeyboardButton(text=row[0][2], callback_data="his_this")],
        [types.InlineKeyboardButton(text=row[1][2], callback_data="his_this")],
        [types.InlineKeyboardButton(text=row[2][2], callback_data="his_this")],
        [types.InlineKeyboardButton(text=row[3][2], callback_data="his_this")],
        [types.InlineKeyboardButton(text=row[4][2], callback_data="his_this")],
        [
            types.InlineKeyboardButton(text="◀", callback_data="his_prev"),
            types.InlineKeyboardButton(text="▶", callback_data="his_next")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(tr['call_history'], reply_markup=keyboard)

@dp.callback_query(F.data.startswith("ph_"))
async def handle_photo_callback(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "yes":
        await callback.message.answer(tr['rename_prompt'])
        await state.set_state(DressStates.waiting_for_name)
    elif action == "no":
        await callback.message.edit_text(tr['rename_cancel'])
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