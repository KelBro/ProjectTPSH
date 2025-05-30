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
from sympy.physics.units import action

from config_reader import config
import math
from redis import StrictRedis as redis
from PIL import Image
from io import BytesIO
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import asyncio


r = redis(host=config.ai_host.get_secret_value(), port=6379, password=config.ai_passwd.get_secret_value())
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())
feedback_chat_id = -1002411249654
upload_id = -1



# async def delete_webhook():
#     await bot.delete_webhook()
#     await bot.session.close()
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

class User:
    def __init__(self):
        self.last_upload_id = -1
        self.st_num = 1
        self.ans = ""
        self.name = ""
        self.lang = "ru"


users_dict = defaultdict(User)

class DressStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_feedback = State()


# пересоздание клавиатуры
def get_keyboard(tr):
    kb = [
        [types.KeyboardButton(text=tr['history'])],
        [types.KeyboardButton(text=tr['feedback']),
        types.KeyboardButton(text=tr['language'])]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )


# обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.id < 0: return
    user_id = message.from_user.id
    tr = get_translations(users_dict[user_id].lang)
    await message.answer(
        f"{hbold(tr['greeting'])}"
        f"{tr['description']}"
        f"\n\n{hbold(tr['cta'])}",
        reply_markup=get_keyboard(tr),
        parse_mode="HTML"
    )

def generate_url(filters, m:str, tr):
    url = m
    # Кодируем параметры фильтров для URL
    for i in filters:
        if i != TRANSLATIONS['ru']["detail"]["nodetail"]:
            url += "+" + i.replace(" ","+")
    return url

def change_dict_lang(dict, tr):
    lan_dict = {}
    for key in dict:
        lan_dict[tr[key]["name"]] = tr[key][dict[key]]
    return lan_dict


# обработчик получения фотографии
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    if message.chat.id < 0: return
    user_id = message.from_user.id
    tr = get_translations(users_dict[user_id].lang)
    date = message.date
    proc = await message.answer(tr["processing"])
    await bot.send_chat_action(message.chat.id, "typing")
    photo_info = await bot.get_file(message.photo[-1].file_id)
    photo = await bot.download_file(photo_info.file_path)
    photo_buff = BytesIO()
    photo = Image.open(photo)
    photo.save(photo_buff, 'JPEG')
    photo_bytes = photo_buff.getvalue()
    photo_id = f'{user_id}{date.hour}{date.minute}{date.second}{date.microsecond}'
    len_id = len(photo_id)

    photo_request = len_id.to_bytes(1,'big') + photo_id.encode(encoding='utf-8') + photo_bytes

    r.lpush('aitasks', photo_request)
    while True:
        if r.exists(photo_id):
            desc_dict = eval(r.get(photo_id).decode(encoding='utf-8'))
            # print("lool",desc_dict)
            r.delete(photo_id)
            break

    date = datetime.now().strftime("%d.%m.%Y")

    description = ""
    for i in desc_dict:
        description += f'{i}: {desc_dict[i]}\n'
    description.strip()


    await proc.delete()
    if desc_dict['department'] != 'it not a dress':
        # Перевод описания
        lan_description = ''
        d = change_dict_lang(desc_dict, tr)
        for i in d:
            # print(i)
            if i != "":
                lan_description += f"{i}: {d[i]}\n"
        lan_description = lan_description.strip()

        # Сохранение в базу данных
        name = tr["name_start"] + tr["a dress with color"][desc_dict["a dress with color"]] + " " + date
        users_dict[user_id].name = name

        connection = sqlite3.connect('data_base.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO uploads (user_id, name, description, upload_date) VALUES (?, ?, ?, ?)',
                       (user_id, name, str(desc_dict), date))
        global upload_id
        upload_id = cursor.lastrowid
        users_dict[user_id].last_upload_id = upload_id
        connection.commit()
        connection.close()

        buttons = [
            [
            types.InlineKeyboardButton(text=tr['yes'], callback_data="ph_yes"),
            types.InlineKeyboardButton(text=tr['no'], callback_data="ph_no")
            ]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        # Ссылки на маркетплейсы
        filters = [TRANSLATIONS['ru']["a dress with color"][desc_dict["a dress with color"]], TRANSLATIONS['ru']["hemline"][desc_dict["hemline"]], TRANSLATIONS['ru']["detail"][desc_dict["detail"]], TRANSLATIONS['ru']["pattern"][desc_dict["pattern"]]]
        ans = (f'{lan_description}\n'+
            f'<a href="{generate_url(filters, "https://www.wildberries.ru/catalog/0/search.aspx?search=платье", tr).replace("%20","+")}">{tr["link_vb"]}</a>'+
            f'<a href="{generate_url(filters, "https://www.ozon.ru/search/?text=платье", tr).replace("%20","+")}">{tr["link_ozon"]}</a>'+
            f'<a href="{generate_url(filters, "https://www.lamoda.ru/catalogsearch/result/?q=платье", tr).replace("%20","+")}">{tr["link_lamoda"]}</a>'+
            # f'<a href="{generate_url(filters, "https://m.aliexpress.com/wholesale?SearchText=платье")}">{tr["link_alik"]}</a>'+
            f'<a href="{generate_url(filters, "https://market.yandex.ru/search?text=платье", tr).replace("%20","+")}">{tr["link_yandex"]}</a>')
        users_dict[user_id].ans = ans
        await bot.send_message(text=
            f"{tr['photo_received1']}\n"+
            ans+
            f"{tr['photo_received2']}{name}{tr['photo_received22']}",
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True,
            chat_id=message.chat.id,
            reply_to_message_id=message.message_id
        )
    else:
        await bot.send_message(text=tr["not_a_dress"],
                               chat_id=message.chat.id,
                               reply_to_message_id=message.message_id)


# обработчик инлайн-кнопок подтверждения фото
@dp.callback_query(F.data.startswith("ph_"))
async def handle_photo_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    tr = get_translations(users_dict[user_id].lang)
    ans = users_dict[user_id].ans
    name = users_dict[user_id].name
    action = callback.data.split("_")[1]

    await callback.message.edit_reply_markup(reply_markup=None)

    if action == "yes":
        await callback.message.answer(tr['rename_prompt'])
        await state.set_state(DressStates.waiting_for_name)
    elif action == "no":
        await callback.message.edit_text(tr['rename_cancel']+ans+tr['photo_received2']+name, reply_markup=None,parse_mode="HTML",disable_web_page_preview=True)
    await callback.answer()

# изменение названия платья
@dp.message(DressStates.waiting_for_name)
async def process_dress_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    last_upload_id = users_dict[user_id].last_upload_id
    tr = get_translations(users_dict[user_id].lang)
    ans = users_dict[user_id].ans
    new_name = message.text
    if new_name != tr["language"] and new_name != tr["history"]:
        await message.answer(
            ans +
            f"{tr['photo_received2']}{new_name}",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        await state.clear()

        connection = sqlite3.connect('data_base.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE uploads SET name = ? WHERE upload_id = ?', (new_name, last_upload_id))
        connection.commit()
        connection.close()


# Обработчик любого текстового сообщения (кроме команд и состояний)
# Обработчик любого текстового сообщения (кроме команд и состояний)
@dp.message(F.text)
async def handle_any_text(message: types.Message, state: FSMContext):
    if message.chat.id < 0:
        return

    user_id = message.from_user.id
    tr = get_translations(users_dict[user_id].lang)

    # Проверяем текущее состояние
    current_state = await state.get_state()

    # Обрабатываем команды/кнопки независимо от состояния
    if message.text == get_translations('ru')['history'] or message.text == get_translations('en')['history']:
        await handle_history(message)
        return
    elif message.text == get_translations('ru')['feedback'] or message.text == get_translations('en')['feedback']:
        await handle_feedback(message, state)
        return
    elif message.text == get_translations('ru')['language'] or message.text == get_translations('en')['language']:
        await handle_language(message)
        return
    elif message.text == '/start':
        await cmd_start(message)
        return
    elif message.text == '/help':
        await cmd_help(message)
        return

    # Если есть активное состояние, пропускаем остальную обработку
    if current_state == DressStates.waiting_for_name.state:
        await process_dress_name(message, state)
        return
    elif current_state == DressStates.waiting_for_feedback.state:
        await process_feedback(message, state)
        return

    # Если сообщение не является командой и не в состоянии - выводим сообщение
    await message.answer(tr["cannot_write"])


def get_history_keyboard(user_id, tr):
    connection = sqlite3.connect("data_base.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * 
        FROM uploads 
        WHERE user_id = ?
    """, (user_id,))
    lines = (cursor.fetchall())[::-1]
    connection.close()
    st_num = users_dict[user_id].st_num

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
    user_id = message.from_user.id
    tr = get_translations(users_dict[user_id].lang)
    if message.chat.id < 0: return
    user_id = message.from_user.id
    users_dict[user_id].st_num = 1
    keyboard = get_history_keyboard(user_id, tr)
    await message.answer(tr['call_history'], reply_markup=keyboard)


@dp.callback_query(F.data.startswith("his_"))
async def history_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    tr = get_translations(users_dict[user_id].lang)
    data = callback.data.split("_")
    action = data[1]

    if action == "prev":
        users_dict[user_id].st_num -= 1
        keyboard = get_history_keyboard(user_id, tr)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()
    elif action == "next":
        users_dict[user_id].st_num += 1
        keyboard = get_history_keyboard(user_id, tr)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()
    elif action == "empty":
        await callback.answer()
    else:
        # Показ деталей элемента
        upload_id = int(action)
        connection = sqlite3.connect("data_base.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM uploads WHERE upload_id = ?", (upload_id,))
        item = cursor.fetchone()
        connection.close()

        if item:
            lan_description = ""
            dict = json.loads(item[3].replace("'", '"'))
            d = change_dict_lang(dict, get_translations(users_dict[user_id].lang))
            for i in d:
                if i != "":
                    lan_description += f"{i}: {d[i]}\n"
            lan_description = lan_description.strip()
            filters = [tr["a dress with color"][dict["a dress with color"]], tr["hemline"][dict["hemline"]],tr["detail"][dict["detail"]], tr["pattern"][dict["pattern"]]]
            links = (f'<a href="{generate_url(filters, "https://www.wildberries.ru/catalog/0/search.aspx?search=платье", tr).replace("%20","+")}">{tr["link_vb"]}</a>' +
                   f'<a href="{generate_url(filters, "https://www.ozon.ru/search/?text=платье", tr).replace("%20","+")}">{tr["link_ozon"]}</a>' +
                   f'<a href="{generate_url(filters, "https://www.lamoda.ru/catalogsearch/result/?q=платье", tr).replace("%20","+")}">{tr["link_lamoda"]}</a>' +
                   # f'<a href="{generate_url(filters, "https://m.aliexpress.com/wholesale?SearchText=платье")}">{tr["link_alik"]}</a>'+
                   f'<a href="{generate_url(filters, "https://market.yandex.ru/search?text=платье", tr).replace("%20","+")}">{tr["link_yandex"]}</a>')
            await callback.message.answer(
                f"{hbold(item[2])}\n\n{lan_description}\n{links}\n{item[4]}",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        await callback.answer()


# обработчик кнопки "Язык"
@dp.message(lambda message: message.text in [lang['language'] for lang in TRANSLATIONS.values()])
async def handle_language(message: types.Message):
    if message.chat.id < 0: return
    user_id = message.from_user.id
    tr = get_translations(users_dict[user_id].lang)
    buttons = [
        [types.InlineKeyboardButton(text=tr['options']['ru'], callback_data="lan_ru")],
        [types.InlineKeyboardButton(text=tr['options']['en'], callback_data="lan_en")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(tr['select'], reply_markup=keyboard)


# обработчик инлайн-кнопок языка
@dp.callback_query(F.data.startswith("lan_"))
async def handle_language_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    action = callback.data.split("_")[1]
    users_dict[user_id].lang = action
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
    if message.chat.id < 0: return
    user_id = message.from_user.id
    tr = get_translations(users_dict[user_id].lang)
    await message.answer(tr['help'], parse_mode="HTML")

@dp.message(lambda message: message.text in [lang['feedback'] for lang in TRANSLATIONS.values()])
async def handle_feedback(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    tr = get_translations(users_dict[user_id].lang)
    await message.answer(tr['feedback_promt'])
    await state.set_state(DressStates.waiting_for_feedback)


@dp.message(DressStates.waiting_for_feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    if message.chat.id < 0: return
    user_id = message.from_user.id
    tr = get_translations(users_dict[user_id].lang)
    feedback = message.text
    if len(feedback)<3:
        await message.answer(tr["feedback_error"])
        return
    await bot.send_message(chat_id=feedback_chat_id, text=f'({user_id}){message.from_user.username}: {feedback}')
    await message.answer(tr["feedback_right"])
    await state.clear()
