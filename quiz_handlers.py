import aiosqlite
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from config import DB_NAME
from quiz_data import quiz_data
from db_utils import get_quiz_index, update_quiz_index, update_quiz_score, get_quiz_results, reset_quiz

def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answer_{idx}")
        )
    builder.adjust(1)
    return builder.as_markup()

async def handle_answer(callback: types.CallbackQuery):
    selected_option = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']
    selected_text = quiz_data[current_question_index]['options'][selected_option]

    await callback.message.answer(f"Ваш ответ: {selected_text}")

    if selected_option == correct_option:
        await callback.message.answer("Верно!")
        await update_quiz_score(user_id, True)
    else:
        correct_text = quiz_data[current_question_index]['options'][correct_option]
        await callback.message.answer(f"Неправильно. Правильный ответ: {correct_text}")
        await update_quiz_score(user_id, False)

    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await callback.message.answer("Квиз завершен!")
        await show_score(callback.message, user_id)

async def show_score(message: types.Message, user_id: int):
    correct_count, wrong_count = await get_quiz_results(user_id)
    total = correct_count + wrong_count
    if total == 0:
        await message.answer("Вы еще не ответили ни на один вопрос.")
        return

    correct_percent = (correct_count / total) * 100
    wrong_percent = (wrong_count / total) * 100

    await message.answer(
        f"Результаты:\n"
        f"Правильных ответов: {correct_count} ({correct_percent:.2f}%)\n"
        f"Неправильных ответов: {wrong_count} ({wrong_percent:.2f}%)"
    )

async def show_statistics(message: types.Message):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, correct_answers, wrong_answers FROM quiz_results') as cursor:
            rows = await cursor.fetchall()
            if not rows:
                await message.answer("Нет данных для отображения статистики.")
                return

            stats = []
            for row in rows:
                user_id, correct, wrong = row
                total = correct + wrong
                correct_percent = (correct / total) * 100 if total > 0 else 0
                wrong_percent = (wrong / total) * 100 if total > 0 else 0
                stats.append(
                    f"Пользователь {user_id}: "
                    f"Правильных ответов: {correct} ({correct_percent:.2f}%), "
                    f"Неправильных ответов: {wrong} ({wrong_percent:.2f}%)"
                )
            await message.answer("\n".join(stats))

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts)
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    await reset_quiz(user_id)
    await get_question(message, user_id)
