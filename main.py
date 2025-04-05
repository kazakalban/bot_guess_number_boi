from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from private_for_API import TEST_BOT_TOKEN
import test_bot_text as texts
from test_bot_tech import ATTEMPTS,get_random_number,STICKER_ID, check_and_add_user_db
from test_bot_dp import get_user_stat, update_user_stat

bot = Bot(token=TEST_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command(commands='start'))
async def start(message: Message):
    # Проверка с базы 
    check_and_add_user_db(message)

    await message.answer('Салем! Мен сенің данныйыңды өзіме жазып алдым Рахмет!!!')
    await message.answer(
        texts.START_TEXT,
        parse_mode='Markdown'
    )


# Этот хендлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def proccess_help_command(message:Message):
    # Проверка с базы
    check_and_add_user_db(message)
    
    await message.answer(
        texts.HELP_TEXT.format(ATTEMPTS = ATTEMPTS),
        parse_mode='Markdown'
    )


# Этот хендлер будет срабатывать на команду "/stat"
@dp.message(Command(commands='stat'))
async def process_stat_command(message:Message):
    # Проверка с базы
    check_and_add_user_db(message)
    # Получает статистику пользователя по user_id
    user_stat = get_user_stat(message.from_user.id)
    print(f'Игрок {message.from_user.id} нажал кнопку статистики')
    await message.answer(
        texts.STAT_TEXT.format(total_games = user_stat['total_games'], wins = user_stat['wins']),
        parse_mode="Markdown"
    )


# Этот хэндлер будет срабатывать на команду "/cancel"
@dp.message(Command(commands='cancel'))
async def proccess_cancel_command(message: Message):
    # Проверка с базы
    check_and_add_user_db(message)
    # Получает статистику пользователя по user_id
    user_stat = get_user_stat(message.from_user.id)
    print(f'Игрок {message.from_user.id} нажал кнопку отмены')
    #user_stat нам возвращает резултаты виде ключа 
    if user_stat['in_game']:
        print(f'у Игрока {message.from_user.id} статус игры {user_stat['in_game']}')
        # Передаем данные чтобы он менялся в базе
        update_user_stat(user_id = message.from_user.id, in_game = False)
        await message.answer(
            texts.CANCEL_TEXT,
            parse_mode="Markdown"
        )
    else:
        print(f'у Игрока {message.from_user.id} статус игры {user_stat['in_game']}')
        await message.answer(
            texts.CANCEL_TEXT_ELSE,
            parse_mode="Markdown"        
        )


# Этот хендлер будет срабатывать на согласие пользователя сыграть в игру
@dp.message(F.text.lower().in_ (texts.POSITIVE_ANSWER))
async def proccess_positive_answer(message: Message):
    # Проверка с базы
    check_and_add_user_db(message)
    # Получает статистику пользователя по user_id
    user_stat = get_user_stat(message.from_user.id)
    print(f'Игрок {message.from_user.id} согласился играть')
    if not user_stat['in_game']:
        update_user_stat(user_id = message.from_user.id, in_game = True)
        update_user_stat(user_id = message.from_user.id, secret_number = get_random_number())
        print(f'У Игрока {message.from_user.id} секретный номер {get_user_stat(message.from_user.id)['secret_number']}')
        update_user_stat(user_id = message.from_user.id, attempts = ATTEMPTS)
        await message.answer(
            texts.POSITIVE_ANSWER_TEXT
        )
    else:
        await message.answer(
            texts.POSITIVE_ANSWER_TEXT_ELSE 
        )


# Этот хендлер будет срабатывать на отправку пользователяем чисел от 1 до 100
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def proccess_number_answer(message: Message):
    # Проверка с базы
    check_and_add_user_db(message)
    # Отправлет запрос в базу статистики
    user_stat = get_user_stat(message.from_user.id)
    print(f'Для игрока {message.from_user.id} проверка  загаденного номера. Игрок ввел номер {message.text} а должен {get_user_stat(message.from_user.id)['secret_number']}')
    if user_stat['in_game']:
        if int(message.text) == user_stat['secret_number']:
            update_user_stat(user_id = message.from_user.id,
                             in_game = False,
                             total_games = get_user_stat(message.from_user.id)['wins'] + 1,
                             wins = get_user_stat(message.from_user.id)['wins'] + 1)
            await message.answer(
                texts.NUMBER_ANSWER_TEXT,
                parse_mode='Markdown'
            )
            print(f'{message.from_user.id} выйграл')
        elif int(message.text) > user_stat['secret_number']:
            print('Заданный число меньше')
            update_user_stat(user_id=message.from_user.id,
                             attempts = user_stat['attempts'] - 1)
            await message.answer(texts.MY_NUMBER_LESS)
        elif int(message.text) < user_stat['secret_number']:
            print('Заданный число меньше')
            update_user_stat(user_id=message.from_user.id,
                             attempts = user_stat['attempts'] - 1)
            await message.answer(texts.MY_NUMBER_MORE)
        if user_stat['attempts'] == 0:
            update_user_stat(user_id=message.from_user.id,
                             in_game=False,
                             total_games=user_stat['total_games'] + 1)
            await message.answer(
                texts.NUMBER_ANSWER_TEXT_NO_LIFE.format(
                    secret_number = user_stat['secret_number']),
                parse_mode='Markdown'
            )
    else:
        await message.answer(texts.NUMBER_ANSWER_TEXT_IN_GAME_FALSE)
@dp.message(F.text.lower().in_ (texts.NEGATIVE_ANSWER))
async def procces_negative_answer(message: Message):
    check_and_add_user_db(message)
    user_stat = get_user_stat(message.from_user.id)
    if not user_stat['in_game']:
        await message.answer(
            texts.NO_ANSWER_TEXT,
            parse_mode='Markdown'
        )
    else:
        await message.answer(
            texts.OTHER_ANSWER_TEXT,
            parse_mode='Markdown'
        )
if __name__ == '__main__':
    dp.run_polling(bot)
