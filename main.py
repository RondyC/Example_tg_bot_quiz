import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config import API_TOKEN
from quiz_handlers import handle_answer, show_score, show_statistics, new_quiz
from db_utils import create_table

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Показать результат"))
    builder.add(types.KeyboardButton(text="Показать статистику"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text == "Показать результат")
async def cmd_show_result(message: types.Message):
    await show_score(message, message.from_user.id)

@dp.message(F.text == "Показать статистику")
async def cmd_show_statistics(message: types.Message):
    await show_statistics(message)

@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

@dp.callback_query(F.data.startswith("answer_"))
async def callback_handler(callback: types.CallbackQuery):
    await handle_answer(callback)

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
