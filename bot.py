import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.markdown import hbold, hitalic
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config_reader import config
import asyncio

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())

class DressStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_photo = State()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Загрузка")],
        [types.KeyboardButton(text="История"),
        types.KeyboardButton(text="Язык")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True # для более аккуратных кнопок
    )
    await message.answer(f"{hbold('Здравствуй! 👋')}"
                         "\n\nЭто бот-ассистент по шоппингу! 🧥✨"
                         "\nОтправь фото вещи — и бот отправит её детальную характеристику"
                         f"\n\n{hbold('Попробуй сейчас — загрузи фото! 📸')}",
                         reply_markup=keyboard,
                         parse_mode="HTML")

# Обработчик кнопки "Загрузка"
@dp.message(F.text == "Загрузка")
async def handle_upload(message: types.Message, state: FSMContext):
    await state.set_state(DressStates.waiting_for_photo)
    await message.answer("Отправьте фотографию вашей одежды")

# Обработчик получения фотографии
@dp.message(F.photo, DressStates.waiting_for_photo)
async def handle_photo(message: types.Message, state: FSMContext):
    buttons = [
        [
            types.InlineKeyboardButton(text="Да", callback_data="ph_yes"),
            types.InlineKeyboardButton(text="Нет", callback_data="ph_no")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(
        "Фото получено. Тут будет описание одежды\nНазвание:\n[цвет] платье [дата]\nИзменить?",
        reply_markup=keyboard
    )
    await state.clear()

# Вывод ошибки для фото, отправленных без нажатия "Загрузка"
@dp.message(F.photo)
async def handle_incorrect_photo(message: types.Message):
    await message.answer("Нажмите кнопку 'Загрузка' чтобы загрузить фото")

# Обработчик инлайн-кнопок подтверждения фото
@dp.callback_query(F.data.startswith("ph_"))
async def handle_photo_callback(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "yes":
        await callback.message.answer("Введите новое название для платья:")
        await state.set_state(DressStates.waiting_for_name)
    elif action == "no":
        await callback.message.edit_text("Изменения отменены.\nТут будет описание одежды\nНазвание:\n[цвет] платье [дата]")
    await callback.answer()

# изменение названия платья
@dp.message(DressStates.waiting_for_name)
async def process_dress_name(message: types.Message, state: FSMContext):
    new_name = message.text
    await message.answer(f"Имя платья успешно изменено на: {new_name}")
    await state.clear()

# Обработчик кнопки "История"
@dp.message(F.text == "История")
async def handle_history(message: types.Message):
    buttons = [
        [types.InlineKeyboardButton(text="Синее платье 04.10", callback_data="num_finish")],
        [types.InlineKeyboardButton(text="Зеленое платье 30.01", callback_data="num_finish")],
        [types.InlineKeyboardButton(text="Красное платье 28.03", callback_data="num_finish")],
        [types.InlineKeyboardButton(text="Тумба-юмба", callback_data="num_finish")],
        [types.InlineKeyboardButton(text="Платье 1", callback_data="num_finish")],
        [
            types.InlineKeyboardButton(text="◀", callback_data="num_decr"),
            types.InlineKeyboardButton(text="▶", callback_data="num_incr")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("История ваших запросов", reply_markup=keyboard)

# Обработчик кнопки "Язык"
@dp.message(F.text == "Язык")
async def handle_language(message: types.Message):
    buttons = [
        [types.InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lan_ru")],
        [types.InlineKeyboardButton(text="Английский 🇬🇧", callback_data="lan_en")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите язык", reply_markup=keyboard)

# Обработчик инлайн-кнопок языка
@dp.callback_query(F.data.startswith("lan_"))
async def handle_language_callback(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    if action == "ru":
        await callback.message.edit_text("Теперь язык русский")
    elif action == "en":
        await callback.message.edit_text("Теперь язык английский")
    await callback.answer()

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Это меню помощи! Тут будут инструкции")