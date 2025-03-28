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
import asyncio

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())
upload_id = -1
user_id = 1
st_num = 1

# async def delete_webhook():
#     await bot.delete_webhook()
#
# asyncio.run(delete_webhook())

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


# обработчик получения фотографии
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    date = datetime.now().strftime("%d.%m.%Y")
    name = 'Тест платье ' + date
    description = "ПОКА ЧТО НИЧЕГО"
    connection = sqlite3.connect('data_base.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO uploads (user_id, name, description, upload_date) VALUES (?, ?, ?, ?)', (user_id, name, description, date))
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
    if new_name != tr["language"]:
        await message.answer(tr['rename_success']+new_name)
        await state.clear()

        connection = sqlite3.connect('data_base.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE uploads SET name = ? WHERE upload_id = ?', (new_name, upload_id))
        connection.commit()
        connection.close()

def lol(message: types.Message):
    connection = sqlite3.connect("data_base.db")
    cursor = connection.cursor()
    cursor.execute("""
                SELECT * 
                FROM uploads 
                WHERE user_id = ?
            """, (user_id,))
    lines = cursor.fetchall()
    x = (st_num - 1) * 5
    y = max(0, min(x+5, len(lines)))
    row = lines[x:y]
    a,b = len(row), len(lines)
    p,n = "prev", "next"
    if st_num == 1:
        p = "lol"
    elif st_num == (b//5 if b%5 == 0 else b//5+1):
        n = "lol"
    if a < 5:
        for i in range(5-a):
            row.append(["his", "lol", tr['empty']])
    print(row)
    buttons = [
        [types.InlineKeyboardButton(text=row[0][2], callback_data=f"his_{row[0][1]}")],
        [types.InlineKeyboardButton(text=row[1][2], callback_data=f"his_{row[1][1]}")],
        [types.InlineKeyboardButton(text=row[2][2], callback_data=f"his_{row[2][1]}")],
        [types.InlineKeyboardButton(text=row[3][2], callback_data=f"his_{row[3][1]}")],
        [types.InlineKeyboardButton(text=row[4][2], callback_data=f"his_{row[4][1]}")],
        [
            types.InlineKeyboardButton(text="◀", callback_data=f"his_{p}_{len(lines)}"),
            types.InlineKeyboardButton(text="▶", callback_data=f"his_{n}_{len(lines)}")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    print(buttons)
    return keyboard

# обработчик кнопки "История"
@dp.message(lambda message: message.text in [lang['history'] for lang in TRANSLATIONS.values()])
async def handle_history(message: types.Message):
    global st_num
    st_num = 1
    k = lol(message)
    await message.answer(tr['call_history'], reply_markup=k)

@dp.callback_query(F.data.startswith("his_"))
async def history_menu(callback: types.CallbackQuery):
    global st_num
    data = callback.data.split("_")
    d = int(data[2])
    if data[1] == "prev":
        if st_num > 1:
            st_num -= 1
            k = lol(callback.message)
            await callback.message.edit_text(tr['call_history'], reply_markup=k)
            await callback.answer()
    elif data[1] == "next":
        if st_num < (d//5 if d % 5 == 0 else d//5+1):
            st_num += 1
            k = lol(callback.message)
            await callback.message.edit_text(tr['call_history'], reply_markup=k)
            await callback.answer()
    elif data[1] != "lol":
        connection = sqlite3.connect("data_base.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uploads WHERE rowid = ?", (data[1]))
        line = cursor.fetchall()[0]
        print(line)
        await callback.message.answer(
            f"{hbold(str(line[2]))}"
            f"\n\n{line[3]}"
            f"\n{line[4]}",
            parse_mode="HTML"
        )


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