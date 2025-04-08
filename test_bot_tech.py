import random 
from test_bot_dp import check_user, add_user_stat, check_user_main_db, add_user_main_dp
import logging


# настроика логирование 
logging.basicConfig(
    level=logging.DEBUG,
    format='[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - {message}',
    style='{'
)

logger = logging.getLogger(__name__)

# Создаем хендлер для записи в файл
file_handler = logging.FileHandler(
    filename='logs.log',
    encoding='utf-8'
)

# Назначаем тот же формат,что и в basicConfig
formatter = logging.Formatter('[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - {message}',
                              style='{'
)
file_handler.setFormatter(formatter)

# Добавляем хэндлер к логгеру
logger.addHandler(file_handler)

# пример использование
#logger.debug('Стартовый логгер для теста ')

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
        logger.debug(f'Начался добавлятся в основную базу id пользователя{user_id}')
        add_user_main_dp(message.from_user.id, message.from_user.is_bot, message.from_user.first_name,
                         message.from_user.last_name, message.from_user.username, message.chat.type)
        logger.debug(f'Новый пользователь {user_id} в основную базу добавлен')
    else:
        logger.debug(f'Пользователь {user_id} уже есть в оновном базе')

    # Проверка пользователя в статистика базе
    if not user_exists:  # Если пользователя нет в базе
        logger.debug(f'Начался добавлятся в статистика базу id пользователя{user_id}')
        add_user_stat(user_id, False, None, None, 0, 0)
        logger.debug(f'Новый пользователь {user_id} в статистика базу добавлен')
    else:
        logger.debug(f'Пользователь {user_id} уже есть в статистика  базе')