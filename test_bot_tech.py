import random 
from test_bot_dp import check_user, add_user_stat, check_user_main_db, add_user_main_dp

#Количества попыток, доступных пользователю в игре
ATTEMPTS = 5


# Функция возвращающая случайное целое цисло от 1 до 100
def get_random_number() -> int:
    return random.randint(1, 100)


# File ID стикера (замени на реальный)
STICKER_ID = "CAACAgIAAxkBAAICKGfFl2yV7-7VAAHz8US_hs67xRXdkAAChxUAAiMAAaBLV73BzYKM-wI2BA"

def check_and_add_user_db(message):
    user_id = message.from_user.id
    # Проверка пользователя есть или нет в базе
    user_exists = check_user(user_id)
    # Проверка пользователя есть или нет в базе
    user_exists_main_db = check_user_main_db(user_id)
    # Если нет в базе то добавляем
    if not user_exists_main_db:  # Если пользователя нет в базе
        print(f'Начался добавлятся в основную базу id пользователя{user_id}')
        add_user_main_dp(message.from_user.id, message.from_user.is_bot, message.from_user.first_name,
                         message.from_user.last_name, message.from_user.username, message.chat.type)
        print(f'Новый пользователь {user_id} в основную базу добавлен')
    else:
        print(f'Пользователь {user_id} уже есть в оновном базе')

    # Проверка пользователя в статистика базе
    if not user_exists:  # Если пользователя нет в базе
        print(f'Начался добавлятся в статистика базу id пользователя{user_id}')
        add_user_stat(user_id, False, None, None, 0, 0)
        print(f'Новый пользователь {user_id} в статистика базу добавлен')
    else:
        print(f'Пользователь {user_id} уже есть в статистика  базе')