import aiosqlite
from config import DB_NAME

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS quiz_state (
                user_id INTEGER PRIMARY KEY, 
                question_index INTEGER
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                user_id INTEGER PRIMARY KEY,
                correct_answers INTEGER,
                wrong_answers INTEGER
            )
        ''')
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()

async def update_quiz_score(user_id, is_correct):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT correct_answers, wrong_answers FROM quiz_results WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            correct, wrong = result if result else (0, 0)
            if is_correct:
                correct += 1
            else:
                wrong += 1
            await db.execute('INSERT OR REPLACE INTO quiz_results (user_id, correct_answers, wrong_answers) VALUES (?, ?, ?)', (user_id, correct, wrong))
            await db.commit()

async def get_quiz_results(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT correct_answers, wrong_answers FROM quiz_results WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result if result else (0, 0)

async def reset_quiz(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, 0)', (user_id,))
        await db.execute('INSERT OR REPLACE INTO quiz_results (user_id, correct_answers, wrong_answers) VALUES (?, 0, 0)', (user_id,))
        await db.commit()
